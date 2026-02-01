"""Open to Work badge detection."""

from playwright.sync_api import Locator
from ..utils.logger import get_logger

logger = get_logger()


class OpenToWorkDetector:
    """Detect Open to Work status on LinkedIn profiles."""

    OPEN_TO_WORK_INDICATORS = [
        "open-to-work",
        "opentowork",
        "#opentowork",
        "hiring",
        "open for opportunities",
    ]

    BADGE_SELECTORS = [
        "[data-test-id='open-to-work-badge']",
        ".pv-open-to-work-card",
        ".pv-member-badge--is-open-to-work",
        "img[alt*='Open to work']",
        "img[alt*='open to work']",
        "[class*='open-to-work']",
        "[class*='opentowork']",
        ".member-badge--open-to-work",
    ]

    PHOTO_FRAME_INDICATORS = [
        "open-to-work-photo-frame",
        "photo-frame--open-to-work",
    ]

    @classmethod
    def detect_from_card(cls, card_element: Locator) -> bool:
        """
        Detect if a search result card indicates Open to Work status.

        Args:
            card_element: Playwright locator for the profile card

        Returns:
            True if Open to Work badge is detected
        """
        try:
            card_html = card_element.inner_html().lower()

            for indicator in cls.OPEN_TO_WORK_INDICATORS:
                if indicator in card_html:
                    return True

            for selector in cls.BADGE_SELECTORS:
                try:
                    if card_element.locator(selector).count() > 0:
                        return True
                except Exception:
                    continue

            for indicator in cls.PHOTO_FRAME_INDICATORS:
                if indicator in card_html:
                    return True

            img_elements = card_element.locator("img")
            for i in range(img_elements.count()):
                try:
                    img = img_elements.nth(i)
                    src = img.get_attribute("src") or ""
                    alt = img.get_attribute("alt") or ""

                    combined = (src + alt).lower()
                    if any(ind in combined for ind in cls.OPEN_TO_WORK_INDICATORS):
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.debug(f"Error detecting Open to Work: {e}")
            return False

    @classmethod
    def detect_from_profile_page(cls, page) -> bool:
        """
        Detect Open to Work status from a profile page.

        Args:
            page: Playwright page object

        Returns:
            True if Open to Work status is detected
        """
        try:
            page_content = page.content().lower()

            for indicator in cls.OPEN_TO_WORK_INDICATORS:
                if indicator in page_content:
                    return True

            for selector in cls.BADGE_SELECTORS:
                try:
                    if page.locator(selector).count() > 0:
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.debug(f"Error detecting Open to Work on profile: {e}")
            return False
