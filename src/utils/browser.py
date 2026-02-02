"""Browser utilities."""

import os
import platform
import shutil
from pathlib import Path
from ..config import config


def get_chrome_user_data_dir() -> str:
    """
    Get a dedicated Chrome user data directory for Playwright.
    Creates a separate profile to avoid conflicts with running Chrome instances.

    Returns:
        Path to Chrome user data directory for Playwright
    """
    if config.CHROME_USER_DATA_DIR:
        return config.CHROME_USER_DATA_DIR

    # Use a dedicated directory for Playwright to avoid conflicts
    system = platform.system()
    
    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        playwright_profile = Path(local_app_data) / "Google" / "Chrome" / "PlaywrightProfile"
    elif system == "Darwin":
        playwright_profile = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "PlaywrightProfile"
    else:
        playwright_profile = Path.home() / ".config" / "google-chrome-playwright"
    
    # Create the directory if it doesn't exist
    playwright_profile.mkdir(parents=True, exist_ok=True)
    
    return str(playwright_profile)


def get_original_chrome_user_data_dir() -> str:
    """
    Get the original Chrome user data directory.

    Returns:
        Path to original Chrome user data directory
    """
    system = platform.system()

    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return str(Path(local_app_data) / "Google" / "Chrome" / "User Data")
    elif system == "Darwin":
        return str(Path.home() / "Library" / "Application Support" / "Google" / "Chrome")
    else:
        return str(Path.home() / ".config" / "google-chrome")


def get_chrome_executable() -> str:
    """
    Get Chrome executable path for the current platform.

    Returns:
        Path to Chrome executable
    """
    system = platform.system()

    if system == "Windows":
        paths = [
            Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        ]
        for path in paths:
            if path.exists():
                return str(path)
        return "chrome.exe"
    elif system == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    else:
        return "google-chrome"
