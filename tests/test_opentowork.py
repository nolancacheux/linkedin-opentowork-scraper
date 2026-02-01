"""Tests for Open to Work detection."""

import pytest
from src.scraper.opentowork import OpenToWorkDetector


class TestOpenToWorkDetector:
    """Test OpenToWorkDetector functionality."""

    def test_indicators_lowercase(self):
        """Test that indicators are lowercase for comparison."""
        for indicator in OpenToWorkDetector.OPEN_TO_WORK_INDICATORS:
            assert indicator == indicator.lower()

    def test_has_badge_selectors(self):
        """Test that badge selectors are defined."""
        assert len(OpenToWorkDetector.BADGE_SELECTORS) > 0

    def test_has_photo_frame_indicators(self):
        """Test that photo frame indicators are defined."""
        assert len(OpenToWorkDetector.PHOTO_FRAME_INDICATORS) > 0
