"""Google Sheets export functionality."""

import os
from pathlib import Path
from typing import List, Optional

from ..config import config
from ..scraper.profile_parser import ProfileData
from ..utils.logger import get_logger

logger = get_logger()


class GoogleSheetsExporter:
    """Export profile data to Google Sheets."""

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    HEADERS = [
        "First Name",
        "Last Name",
        "Full Name",
        "Headline",
        "Current Company",
        "Location",
        "Profile URL",
        "Open to Work",
        "Scraped At",
    ]

    def __init__(self, spreadsheet_id: str = None, credentials_path: str = None):
        """
        Initialize Google Sheets exporter.

        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            credentials_path: Path to service account credentials JSON
        """
        self.spreadsheet_id = spreadsheet_id or config.GOOGLE_SHEETS_ID
        self.credentials_path = credentials_path or config.GOOGLE_CREDENTIALS_PATH
        self.service = None

    def _get_service(self):
        """Get or create Google Sheets API service."""
        if self.service is not None:
            return self.service

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            if not Path(self.credentials_path).exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_path}\n"
                    "Please set up Google Sheets API credentials.\n"
                    "See docs/INSTALLATION.md for instructions."
                )

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES,
            )

            self.service = build("sheets", "v4", credentials=credentials)
            return self.service

        except ImportError:
            raise ImportError(
                "Google API libraries not installed.\n"
                "Run: pip install google-auth google-auth-oauthlib google-api-python-client"
            )

    def _profile_to_row(self, profile: ProfileData) -> list:
        """Convert ProfileData to a row for Google Sheets."""
        return [
            profile.first_name,
            profile.last_name,
            profile.full_name,
            profile.headline,
            profile.current_company,
            profile.location,
            profile.profile_url,
            "Yes" if profile.is_open_to_work else "No",
            profile.scraped_at.strftime("%Y-%m-%d %H:%M:%S"),
        ]

    def export(
        self,
        profiles: List[ProfileData],
        sheet_name: str = "Sheet1",
        clear_existing: bool = False,
    ) -> int:
        """
        Export profiles to Google Sheets.

        Args:
            profiles: List of ProfileData objects
            sheet_name: Name of the sheet to write to
            clear_existing: Clear existing data before writing

        Returns:
            Number of rows written
        """
        if not self.spreadsheet_id:
            raise ValueError(
                "Spreadsheet ID not configured.\n"
                "Set GOOGLE_SHEETS_ID in .env or pass spreadsheet_id to constructor."
            )

        service = self._get_service()
        sheets = service.spreadsheets()

        range_name = f"{sheet_name}!A1"

        if clear_existing:
            sheets.values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:Z",
            ).execute()

        values = [self.HEADERS]
        values.extend([self._profile_to_row(p) for p in profiles])

        body = {"values": values}

        result = sheets.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body,
        ).execute()

        updated_rows = result.get("updatedRows", 0)
        logger.info(f"Exported {len(profiles)} profiles to Google Sheets")
        logger.info(f"Spreadsheet: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")

        return updated_rows

    def append(self, profile: ProfileData, sheet_name: str = "Sheet1") -> None:
        """
        Append a single profile to Google Sheets.

        Args:
            profile: ProfileData object
            sheet_name: Name of the sheet to append to
        """
        if not self.spreadsheet_id:
            raise ValueError("Spreadsheet ID not configured")

        service = self._get_service()
        sheets = service.spreadsheets()

        row = self._profile_to_row(profile)

        body = {"values": [row]}

        sheets.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{sheet_name}!A:I",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()
