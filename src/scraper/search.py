"""LinkedIn search functionality."""

import urllib.parse
from typing import Optional
from ..config import config


def build_search_url(
    job_title: str,
    location: str,
    page: int = 1,
    network: Optional[list[str]] = None,
) -> str:
    """
    Build LinkedIn people search URL.

    Args:
        job_title: Job title to search for
        location: Location to filter by
        page: Page number (1-indexed)
        network: Network filter (e.g., ["F", "S"] for 1st and 2nd connections)

    Returns:
        Complete search URL
    """
    base_url = config.LINKEDIN_SEARCH_URL

    keywords = f'"{job_title}"'

    params = {
        "keywords": keywords,
        "origin": "GLOBAL_SEARCH_HEADER",
        "sid": "search",
    }

    if location:
        params["geoUrn"] = f'["{location}"]'

    if page > 1:
        params["page"] = str(page)

    if network:
        params["network"] = str(network)

    query_string = urllib.parse.urlencode(params, safe='[]"')

    return f"{base_url}?{query_string}"


def build_search_url_simple(job_title: str, location: str, open_to_work_only: bool = False) -> str:
    """
    Build a simple LinkedIn search URL with proper location filtering.

    Args:
        job_title: Job title to search for
        location: Location to filter by
        open_to_work_only: Not used (kept for API compatibility)

    Returns:
        Complete search URL
    """
    encoded_keywords = urllib.parse.quote(job_title)

    url = f"{config.LINKEDIN_SEARCH_URL}?keywords={encoded_keywords}&origin=GLOBAL_SEARCH_HEADER"

    # Add location as a separate filter parameter
    if location:
        encoded_location = urllib.parse.quote(location)
        url += f"&location={encoded_location}"

    return url
