"""Main LinkedIn scraper class."""

import random
import sys
from typing import Generator, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..config import config
from ..utils.logger import get_logger
from ..utils.delays import human_delay, long_pause, scroll_pause
from ..utils.browser import get_chrome_user_data_dir
from .profile_parser import ProfileParser, ProfileData
from .opentowork import OpenToWorkDetector
from .search import build_search_url_simple

logger = get_logger()


class LinkedInScraper:
    """Scrape LinkedIn profiles with Open to Work detection."""

    def __init__(self, headless: bool = False):
        """
        Initialize the scraper.

        Args:
            headless: Run browser in headless mode (not recommended)
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.action_count = 0

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def start(self) -> None:
        """Start the browser."""
        logger.info("Starting browser...")
        logger.info("IMPORTANT: Close all Chrome windows before running!")

        self.playwright = sync_playwright().start()

        user_data_dir = get_chrome_user_data_dir()
        logger.info(f"Using Chrome profile: {user_data_dir}")

        try:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir,
                headless=self.headless,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--start-maximized",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
                viewport={"width": 1920, "height": 1080},
                ignore_default_args=["--enable-automation"],
            )

            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()

            logger.info("Browser started successfully")

        except Exception as e:
            error_msg = str(e).lower()
            if "user data directory is already in use" in error_msg or "lock" in error_msg:
                logger.error("Chrome is already running!")
                logger.error("Please close ALL Chrome windows and try again.")
                sys.exit(1)
            else:
                logger.error(f"Failed to start browser: {e}")
                logger.info("Falling back to new browser instance (you will need to log in)...")

                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    channel="chrome",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                    ],
                )
                self.context = self.browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                self.page = self.context.new_page()

    def close(self) -> None:
        """Close the browser."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")

    def _increment_action(self) -> None:
        """Increment action counter and take long pause if needed."""
        self.action_count += 1

        if self.action_count % config.LONG_PAUSE_INTERVAL == 0:
            logger.info(f"Taking a break after {self.action_count} actions...")
            long_pause()

    def is_logged_in(self) -> bool:
        """
        Check if user is logged into LinkedIn.

        Returns:
            True if logged in
        """
        try:
            self.page.goto(config.LINKEDIN_BASE_URL, wait_until="domcontentloaded")
            human_delay(2, 4)

            current_url = self.page.url
            logger.info(f"Current URL: {current_url}")

            if "/login" in current_url or "/checkpoint" in current_url or "signin" in current_url:
                logger.info("Not logged in - login page detected")
                return False

            if "/feed" in current_url:
                logger.info("Logged in - feed page detected")
                return True

            logged_in_indicators = [
                ".global-nav__me-photo",
                ".feed-identity-module__actor-image",
                "img.global-nav__me-photo",
                "[data-control-name='identity_welcome_message']",
            ]

            for selector in logged_in_indicators:
                try:
                    if self.page.locator(selector).count() > 0:
                        logger.info(f"Logged in - found indicator: {selector}")
                        return True
                except Exception:
                    continue

            page_text = self.page.content().lower()
            if "sign in" in page_text and "join now" in page_text:
                logger.info("Not logged in - sign in page content detected")
                return False

            logger.info("Login status unclear, assuming not logged in")
            return False

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def wait_for_login(self, timeout: int = 300) -> bool:
        """
        Wait for user to log in manually.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if logged in within timeout
        """
        logger.info("=" * 50)
        logger.info("Please log in to LinkedIn in the browser window!")
        logger.info(f"Waiting up to {timeout} seconds...")
        logger.info("=" * 50)

        self.page.goto(f"{config.LINKEDIN_BASE_URL}/login", wait_until="domcontentloaded")

        start_time = self.page.evaluate("() => Date.now()")

        while True:
            current_time = self.page.evaluate("() => Date.now()")
            elapsed = (current_time - start_time) / 1000

            if elapsed > timeout:
                logger.error("Login timeout exceeded")
                return False

            current_url = self.page.url
            if "/feed" in current_url:
                logger.info("Login successful!")
                return True

            if self.is_logged_in():
                logger.info("Login successful!")
                return True

            human_delay(3, 5)

    def _scroll_page(self) -> bool:
        """
        Scroll down the page to load more results.

        Returns:
            True if new content was loaded
        """
        try:
            prev_height = self.page.evaluate("() => document.body.scrollHeight")

            scroll_amount = random.randint(300, 600)
            self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            scroll_pause()

            self._increment_action()

            new_height = self.page.evaluate("() => document.body.scrollHeight")

            return new_height > prev_height

        except Exception as e:
            logger.debug(f"Scroll error: {e}")
            return False

    def _get_profile_cards(self):
        """Get all profile cards on the current page."""
        selectors = ProfileParser.CARD_SELECTORS["container"]

        for selector in selectors:
            cards = self.page.locator(selector)
            if cards.count() > 0:
                return cards

        return self.page.locator("li.reusable-search__result-container")

    def _go_to_next_page(self) -> bool:
        """
        Navigate to the next page of results.

        Returns:
            True if navigation successful
        """
        try:
            next_button = self.page.locator("button[aria-label='Next']")

            if next_button.count() > 0 and next_button.is_enabled():
                human_delay()
                next_button.click()
                human_delay(2, 4)
                self._increment_action()
                return True

            next_link = self.page.locator("a[aria-label='Next']")
            if next_link.count() > 0:
                human_delay()
                next_link.click()
                human_delay(2, 4)
                self._increment_action()
                return True

            return False

        except Exception as e:
            logger.debug(f"Next page error: {e}")
            return False

    def scrape_search_results(
        self,
        job_title: str,
        location: str,
        max_profiles: int = 100,
        open_to_work_only: bool = True,
    ) -> Generator[ProfileData, None, None]:
        """
        Scrape LinkedIn search results.

        Args:
            job_title: Job title to search for
            location: Location to filter by
            max_profiles: Maximum profiles to collect
            open_to_work_only: Only return Open to Work profiles

        Yields:
            ProfileData objects for matching profiles
        """
        logger.info("Checking LinkedIn login status...")

        if not self.is_logged_in():
            if not self.wait_for_login():
                logger.error("Could not log in to LinkedIn")
                return

        search_url = build_search_url_simple(job_title, location)
        logger.info(f"Navigating to search: {job_title} in {location}")

        self.page.goto(search_url, wait_until="domcontentloaded")
        human_delay(3, 5)

        current_url = self.page.url
        if "/login" in current_url:
            logger.error("Redirected to login page - session expired?")
            if not self.wait_for_login():
                return
            self.page.goto(search_url, wait_until="domcontentloaded")
            human_delay(3, 5)

        collected_count = 0
        total_scraped = 0
        seen_urls = set()
        page_num = 1

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            task = progress.add_task(
                f"[cyan]Scraping profiles (Open to Work: {collected_count})...",
                total=max_profiles,
            )

            while collected_count < max_profiles:
                if total_scraped >= config.MAX_PROFILES_PER_SESSION:
                    logger.warning("Session limit reached")
                    break

                for _ in range(3):
                    self._scroll_page()
                    human_delay(1, 2)

                cards = self._get_profile_cards()
                card_count = cards.count()

                if card_count == 0:
                    logger.warning("No profile cards found on page")
                    logger.info(f"Current URL: {self.page.url}")
                    page_title = self.page.title()
                    logger.info(f"Page title: {page_title}")
                    break

                logger.info(f"Page {page_num}: Found {card_count} profile cards")

                for i in range(card_count):
                    if collected_count >= max_profiles:
                        break

                    try:
                        card = cards.nth(i)
                        is_open = OpenToWorkDetector.detect_from_card(card)
                        profile = ProfileParser.parse_card(card, is_open_to_work=is_open)

                        if profile and profile.profile_url not in seen_urls:
                            seen_urls.add(profile.profile_url)
                            total_scraped += 1

                            if not open_to_work_only or profile.is_open_to_work:
                                collected_count += 1
                                progress.update(
                                    task,
                                    advance=1,
                                    description=f"[cyan]Scraping profiles (Open to Work: {collected_count})...",
                                )
                                yield profile

                    except Exception as e:
                        logger.debug(f"Error processing card {i}: {e}")
                        continue

                if not self._go_to_next_page():
                    logger.info("No more pages available")
                    break

                page_num += 1
                human_delay(2, 4)

        logger.info(f"Scraping complete: {collected_count} Open to Work profiles from {total_scraped} total")
