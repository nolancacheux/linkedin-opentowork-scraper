"""Open to Work badge detection."""

import requests
from io import BytesIO
from PIL import Image
from playwright.sync_api import Locator
from ..utils.logger import get_logger

logger = get_logger()


def detect_green_frame(image_url: str) -> bool:
    """
    Detect if a profile photo has the green Open to Work frame.

    The frame is a green ring around the circular profile photo.
    LinkedIn's Open to Work green is approximately RGB(98, 164, 113) / #62a471

    Args:
        image_url: URL of the profile photo

    Returns:
        True if green frame detected
    """
    try:
        response = requests.get(image_url, timeout=5)
        if response.status_code != 200:
            return False

        img = Image.open(BytesIO(response.content)).convert('RGB')
        width, height = img.size

        # Check pixels around the edge (the frame area)
        # Sample points at ~5% from edge around the circle
        green_pixels = 0
        total_samples = 0

        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2

        # Sample at 95% of radius (edge area where frame appears)
        check_radius = int(radius * 0.95)

        import math
        for angle in range(0, 360, 10):  # Sample every 10 degrees
            rad = math.radians(angle)
            x = int(center_x + check_radius * math.cos(rad))
            y = int(center_y + check_radius * math.sin(rad))

            if 0 <= x < width and 0 <= y < height:
                r, g, b = img.getpixel((x, y))
                total_samples += 1

                # Check for LinkedIn's Open to Work green
                # Allow some tolerance for compression artifacts
                if g > 120 and g > r and g > b and (g - r) > 30 and (g - b) > 20:
                    green_pixels += 1

        # If more than 50% of edge samples are green, likely has the frame
        if total_samples > 0 and (green_pixels / total_samples) > 0.5:
            logger.debug(f"Green frame detected: {green_pixels}/{total_samples} samples")
            return True

        return False

    except Exception as e:
        logger.debug(f"Error checking green frame: {e}")
        return False


class OpenToWorkDetector:
    """Detect Open to Work status on LinkedIn profiles."""

    OPEN_TO_WORK_INDICATORS = [
        "open-to-work",
        "opentowork",
        "#opentowork",
        "open to work",
        "open for work",
        "actively seeking",
        "seeking opportunities",
        "seeking new opportunities",
        "looking for opportunities",
        "available for hire",
        "available immediately",
        "open to opportunities",
    ]

    BADGE_SELECTORS = [
        "[data-test-id='open-to-work-badge']",
        ".pv-open-to-work-card",
        ".pv-member-badge--is-open-to-work",
        "img[alt*='Open to work']",
        "img[alt*='open to work']",
        "img[alt*='Open To Work']",
        "[class*='open-to-work']",
        "[class*='opentowork']",
        ".member-badge--open-to-work",
        # Green photo frame indicators
        "[class*='job-seeker']",
        "[class*='jobseeker']",
        ".photo-frame--green",
        "svg[aria-label*='Open to work']",
        "svg[aria-label*='open to work']",
    ]

    PHOTO_FRAME_INDICATORS = [
        "open-to-work-photo-frame",
        "photo-frame--open-to-work",
        "job-seeker",
        "jobseeker",
        # Green color hex codes often used
        "#70b5f9",  # LinkedIn blue for open to work
        "rgb(112, 181, 249)",
    ]

    @classmethod
    def detect_from_card(cls, card_element: Locator) -> bool:
        """
        Detect if a search result card indicates Open to Work status.

        Uses multiple detection methods:
        1. Text indicators in profile headline
        2. CSS selectors for badge elements
        3. Image analysis for green frame (most accurate)

        Args:
            card_element: Playwright locator for the profile card

        Returns:
            True if Open to Work badge is detected
        """
        try:
            card_html = card_element.inner_html().lower()

            # Method 1: Text indicators
            for indicator in cls.OPEN_TO_WORK_INDICATORS:
                if indicator in card_html:
                    logger.debug(f"Open to Work detected via text: {indicator}")
                    return True

            # Method 2: CSS selectors
            for selector in cls.BADGE_SELECTORS:
                try:
                    if card_element.locator(selector).count() > 0:
                        logger.debug(f"Open to Work detected via selector: {selector}")
                        return True
                except Exception:
                    continue

            # Method 3: Photo frame indicators in HTML
            for indicator in cls.PHOTO_FRAME_INDICATORS:
                if indicator in card_html:
                    return True

            # Method 4: Check image attributes
            img_elements = card_element.locator("img")
            for i in range(img_elements.count()):
                try:
                    img = img_elements.nth(i)
                    src = img.get_attribute("src") or ""
                    alt = img.get_attribute("alt") or ""

                    combined = (src + alt).lower()
                    if any(ind in combined for ind in cls.OPEN_TO_WORK_INDICATORS):
                        return True

                    # Method 5: Image analysis for green frame (profile photos only)
                    if src and ("profile" in src or "media.licdn" in src) and "100_100" in src:
                        if detect_green_frame(src):
                            logger.debug("Open to Work detected via green frame analysis")
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
