"""Logging utilities."""

import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

_logger = None


def setup_logger(name: str = "linkedin_scraper", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and return a configured logger.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    global _logger

    if _logger is not None:
        return _logger

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )

    _logger = logging.getLogger(name)
    return _logger


def get_logger() -> logging.Logger:
    """Get the configured logger instance."""
    if _logger is None:
        return setup_logger()
    return _logger
