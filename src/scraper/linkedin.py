"""Main LinkedIn scraper class."""

import random
from typing import Generator, Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

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
            logger.error(f"Failed to start browser: {e}")
            logger.info("Falling back to new browser instance...")

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

            logged_in_indicators = [
                "nav.global-nav",
                "[data-control-name='nav.settings']",
                ".feed-identity-module",
                ".global-nav__me",
            ]

            for selector in logged_in_indicators:
                if self.page.locator(selector).count() > 0:
                    return True

            if "/login" in self.page.url or "/checkpoint" in self.page.url:
                return False

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
        logger.info("Please log in to LinkedIn in the browser window...")
        logger.info(f"Waiting up to {timeout} seconds...")

        self.page.goto(f"{config.LINKEDIN_BASE_URL}/login", wait_until="domcontentloaded")

        start_time = self.page.evaluate("() => Date.now()")

        while True:
            current_time = self.page.evaluate("() => Date.now()")
            elapsed = (current_time - start_time) / 1000

            if elapsed > timeout:
                logger.error("Login timeout exceeded")
                return False

            if self.is_logged_in():
                logger.info("Login successful!")
                return True

            human_delay(2, 3)

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
            # Multiple selectors for different languages and LinkedIn versions
            next_selectors = [
                "button[aria-label='Next']",
                "button[aria-label='Suivant']",  # French
                "button[aria-label='Weiter']",   # German
                "a[aria-label='Next']",
                "a[aria-label='Suivant']",
                "button.artdeco-pagination__button--next",
                "button[class*='pagination__button--next']",
                "li.artdeco-pagination__indicator--number:last-child button",
            ]

            for selector in next_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible():
                        # Check if button is enabled (not disabled)
                        is_disabled = btn.get_attribute("disabled")
                        if is_disabled:
                            continue

                        human_delay()
                        btn.click()
                        human_delay(2, 4)
                        self._increment_action()
                        logger.debug(f"Navigated to next page using: {selector}")
                        return True
                except Exception:
                    continue

            # Try scrolling to bottom and looking for pagination
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            human_delay(1, 2)

            # Try clicking on next page number directly
            try:
                # Find current page and click next number
                current = self.page.locator("button[aria-current='true']").first
                if current.count() > 0:
                    current_text = current.inner_text()
                    if current_text.isdigit():
                        next_num = int(current_text) + 1
                        next_page_btn = self.page.locator(f"button:has-text('{next_num}')").first
                        if next_page_btn.count() > 0:
                            human_delay()
                            next_page_btn.click()
                            human_delay(2, 4)
                            self._increment_action()
                            return True
            except Exception:
                pass

            return False

        except Exception as e:
            logger.debug(f"Next page error: {e}")
            return False

    def _apply_location_filter(self, location: str) -> bool:
        """
        Apply location filter through LinkedIn's UI.

        Args:
            location: Location name to filter by

        Returns:
            True if filter was applied successfully
        """
        try:
            # Check if location filter is already showing results for the location
            # by looking at the current filters
            current_url = self.page.url
            if f"location={location}" in current_url.lower() or "geourn" in current_url.lower():
                logger.debug("Location filter may already be applied via URL")

            # Click on "Locations" filter button
            location_filter_selectors = [
                "button:has-text('Locations')",
                "button:has-text('Lieux')",  # French
                "button:has-text('Standorte')",  # German
                "button[aria-label*='location']",
                "button[aria-label*='Location']",
                "#searchFilter_geoUrn",
            ]

            filter_clicked = False
            for selector in location_filter_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click()
                        human_delay(1, 2)
                        filter_clicked = True
                        break
                except Exception:
                    continue

            if not filter_clicked:
                logger.debug("Could not find location filter button")
                return False

            # Type in the location search box
            location_input_selectors = [
                "input[placeholder*='location']",
                "input[placeholder*='Location']",
                "input[placeholder*='lieu']",
                "input[aria-label*='location']",
                "input[role='combobox']",
            ]

            for selector in location_input_selectors:
                try:
                    input_el = self.page.locator(selector).first
                    if input_el.count() > 0 and input_el.is_visible():
                        input_el.fill(location)
                        human_delay(1, 2)

                        # Click on first suggestion
                        suggestion_selectors = [
                            "[role='option']",
                            ".basic-typeahead__selectable",
                            "li[id*='typeahead']",
                        ]

                        for sug_sel in suggestion_selectors:
                            try:
                                suggestion = self.page.locator(sug_sel).first
                                if suggestion.count() > 0:
                                    suggestion.click()
                                    human_delay(0.5, 1)
                                    break
                            except Exception:
                                continue

                        break
                except Exception:
                    continue

            # Click "Show results" button
            apply_selectors = [
                "button:has-text('Show results')",
                "button:has-text('Afficher les résultats')",
                "button[data-test-reusables-filter-apply-button]",
                "button.search-reusables__filter-apply-button",
            ]

            for selector in apply_selectors:
                try:
                    apply_btn = self.page.locator(selector).first
                    if apply_btn.count() > 0 and apply_btn.is_visible():
                        apply_btn.click()
                        human_delay(2, 3)
                        logger.info(f"Applied location filter: {location}")
                        return True
                except Exception:
                    continue

            # Try pressing Enter as fallback
            self.page.keyboard.press("Enter")
            human_delay(2, 3)

            return True

        except Exception as e:
            logger.debug(f"Error applying location filter: {e}")
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
        if not self.is_logged_in():
            if not self.wait_for_login():
                logger.error("Could not log in to LinkedIn")
                return

        search_url = build_search_url_simple(job_title, location)
        logger.info(f"Navigating to search: {job_title}" + (f" in {location}" if location else ""))

        self.page.goto(search_url, wait_until="domcontentloaded")
        human_delay(3, 5)

        # Apply location filter through UI if needed
        if location:
            self._apply_location_filter(location)

        collected_count = 0
        total_scraped = 0
        seen_urls = set()
        page_num = 1

        with Progress(
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

                            # Check location filter
                            location_match = True
                            if location:
                                profile_loc = profile.location.lower()
                                search_loc = location.lower()
                                # Match if location contains the search term or vice versa
                                location_match = search_loc in profile_loc or profile_loc in search_loc

                            if location_match and (not open_to_work_only or profile.is_open_to_work):
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
