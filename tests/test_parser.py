"""Tests for profile parser."""

import pytest
from src.scraper.profile_parser import ProfileParser


class TestProfileParser:
    """Test ProfileParser functionality."""

    def test_parse_name_simple(self):
        """Test simple name parsing."""
        first, last = ProfileParser.parse_name("John Doe")
        assert first == "John"
        assert last == "Doe"

    def test_parse_name_single(self):
        """Test single name parsing."""
        first, last = ProfileParser.parse_name("John")
        assert first == "John"
        assert last == ""

    def test_parse_name_multiple(self):
        """Test name with multiple parts."""
        first, last = ProfileParser.parse_name("Jean-Pierre De La Fontaine")
        assert first == "Jean-Pierre"
        assert last == "De La Fontaine"

    def test_parse_name_with_title(self):
        """Test name with title in parentheses."""
        first, last = ProfileParser.parse_name("John Doe (PhD)")
        assert first == "John"
        assert last == "Doe"

    def test_parse_name_with_comma(self):
        """Test name with comma suffix."""
        first, last = ProfileParser.parse_name("John Doe, MBA")
        assert first == "John"
        assert last == "Doe"

    def test_parse_name_extra_whitespace(self):
        """Test name with extra whitespace."""
        first, last = ProfileParser.parse_name("  John   Doe  ")
        assert first == "John"
        assert last == "Doe"

    def test_parse_name_empty(self):
        """Test empty name."""
        first, last = ProfileParser.parse_name("")
        assert first == ""
        assert last == ""

    def test_extract_company_at(self):
        """Test company extraction with 'at'."""
        company = ProfileParser.extract_company_from_headline("Software Engineer at Google")
        assert company == "Google"

    def test_extract_company_chez(self):
        """Test company extraction with 'chez' (French)."""
        company = ProfileParser.extract_company_from_headline("Ingenieur Logiciel chez Microsoft")
        assert company == "Microsoft"

    def test_extract_company_pipe(self):
        """Test company extraction with pipe separator."""
        company = ProfileParser.extract_company_from_headline("Software Engineer | Amazon")
        assert company == "Amazon"

    def test_extract_company_none(self):
        """Test when no company found."""
        company = ProfileParser.extract_company_from_headline("Software Engineer")
        assert company == ""

    def test_extract_company_complex(self):
        """Test complex headline."""
        company = ProfileParser.extract_company_from_headline(
            "Senior Software Engineer at Meta | Ex-Google"
        )
        assert company == "Meta"
