"""Browser utilities."""

import os
import platform
from pathlib import Path
from ..config import config


def get_chrome_user_data_dir() -> str:
    """
    Get Chrome user data directory for the current platform.

    Returns:
        Path to Chrome user data directory
    """
    if config.CHROME_USER_DATA_DIR:
        return config.CHROME_USER_DATA_DIR

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
