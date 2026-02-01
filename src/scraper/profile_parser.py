"""LinkedIn profile data parsing."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from playwright.sync_api import Locator
from ..utils.logger import get_logger

logger = get_logger()


@dataclass
class ProfileData:
    """Data structure for a LinkedIn profile."""

    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    headline: str = ""
    current_company: str = ""
    location: str = ""
    profile_url: str = ""
    is_open_to_work: bool = False
    scraped_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "headline": self.headline,
            "current_company": self.current_company,
            "location": self.location,
            "profile_url": self.profile_url,
            "is_open_to_work": self.is_open_to_work,
            "scraped_at": self.scraped_at.isoformat(),
        }


class ProfileParser:
    """Parse LinkedIn profile data from search results."""

    CARD_SELECTORS = {
        "container": [
            "li.reusable-search__result-container",
            "[data-chameleon-result-urn]",
            ".search-result__wrapper",
        ],
        "name": [
            ".entity-result__title-text a span[aria-hidden='true']",
            ".entity-result__title-text a",
            ".actor-name",
            "span.name",
        ],
        "headline": [
            ".entity-result__primary-subtitle",
            ".search-result__snippets",
            ".subline-level-1",
        ],
        "location": [
            ".entity-result__secondary-subtitle",
            ".subline-level-2",
        ],
        "link": [
            ".entity-result__title-text a",
            "a[data-control-name='search_srp_result']",
            "a.app-aware-link",
        ],
    }

    @classmethod
    def parse_name(cls, full_name: str) -> tuple[str, str]:
        """
        Split full name into first and last name.

        Args:
            full_name: The full name string

        Returns:
            Tuple of (first_name, last_name)
        """
        full_name = full_name.strip()
        full_name = re.sub(r"\s+", " ", full_name)
        full_name = re.sub(r"\([^)]*\)", "", full_name).strip()
        full_name = re.sub(r",.*$", "", full_name).strip()

        parts = full_name.split(" ")

        if len(parts) == 0:
            return "", ""
        elif len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], " ".join(parts[1:])

    @classmethod
    def extract_company_from_headline(cls, headline: str) -> str:
        """
        Extract company name from headline.

        Args:
            headline: Profile headline

        Returns:
            Company name if found
        """
        patterns = [
            r"(?:at|@|chez|presso|bei)\s+(.+?)(?:\s*[|\-]|$)",
            r"[|\-]\s*(.+?)(?:\s*[|\-]|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, headline, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if company and len(company) > 1:
                    return company

        return ""

    @classmethod
    def parse_card(cls, card: Locator, is_open_to_work: bool = False) -> Optional[ProfileData]:
        """
        Parse a search result card into ProfileData.

        Args:
            card: Playwright locator for the card element
            is_open_to_work: Whether Open to Work badge was detected

        Returns:
            ProfileData if parsing successful, None otherwise
        """
        try:
            profile = ProfileData(is_open_to_work=is_open_to_work)

            for selector in cls.CARD_SELECTORS["name"]:
                try:
                    name_el = card.locator(selector).first
                    if name_el.count() > 0:
                        profile.full_name = name_el.inner_text().strip()
                        break
                except Exception:
                    continue

            if profile.full_name:
                profile.first_name, profile.last_name = cls.parse_name(profile.full_name)

            for selector in cls.CARD_SELECTORS["headline"]:
                try:
                    headline_el = card.locator(selector).first
                    if headline_el.count() > 0:
                        profile.headline = headline_el.inner_text().strip()
                        break
                except Exception:
                    continue

            if profile.headline:
                profile.current_company = cls.extract_company_from_headline(profile.headline)

            for selector in cls.CARD_SELECTORS["location"]:
                try:
                    loc_el = card.locator(selector).first
                    if loc_el.count() > 0:
                        profile.location = loc_el.inner_text().strip()
                        break
                except Exception:
                    continue

            for selector in cls.CARD_SELECTORS["link"]:
                try:
                    link_el = card.locator(selector).first
                    if link_el.count() > 0:
                        href = link_el.get_attribute("href")
                        if href:
                            profile.profile_url = href.split("?")[0]
                            break
                except Exception:
                    continue

            if not profile.full_name and not profile.profile_url:
                return None

            return profile

        except Exception as e:
            logger.debug(f"Error parsing card: {e}")
            return None
