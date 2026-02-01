"""Main entry point for LinkedIn Open to Work Scraper."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.table import Table

from .config import config
from .scraper import LinkedInScraper
from .scraper.profile_parser import ProfileData
from .export import CSVExporter, GoogleSheetsExporter
from .utils.logger import setup_logger, get_logger

console = Console()


def print_banner():
    """Print application banner."""
    banner = """
LinkedIn Open to Work Scraper
Search profiles and filter by Open to Work status
    """
    console.print(Panel(banner.strip(), border_style="blue"))


def print_results_table(profiles: list[ProfileData]):
    """Print results in a table format."""
    table = Table(title="Scraped Profiles")

    table.add_column("Name", style="cyan")
    table.add_column("Headline", style="white", max_width=40)
    table.add_column("Location", style="green")
    table.add_column("Open to Work", style="yellow")

    for profile in profiles[:20]:
        table.add_row(
            profile.full_name,
            profile.headline[:40] + "..." if len(profile.headline) > 40 else profile.headline,
            profile.location,
            "Yes" if profile.is_open_to_work else "No",
        )

    if len(profiles) > 20:
        table.add_row("...", f"({len(profiles) - 20} more)", "...", "...")

    console.print(table)


@click.command()
@click.option("--job", "-j", help="Job title to search for")
@click.option("--location", "-l", help="Location to filter by")
@click.option("--max", "-m", "max_profiles", type=int, help="Maximum profiles to collect")
@click.option("--output", "-o", type=click.Choice(["csv", "sheets"]), default="csv", help="Output format")
@click.option("--sheet-id", help="Google Sheets ID (for sheets output)")
@click.option("--headless", is_flag=True, help="Run in headless mode (not recommended)")
@click.option("--all-profiles", is_flag=True, help="Include profiles without Open to Work badge")
def main(
    job: Optional[str],
    location: Optional[str],
    max_profiles: Optional[int],
    output: str,
    sheet_id: Optional[str],
    headless: bool,
    all_profiles: bool,
):
    """
    LinkedIn Open to Work Scraper

    Search LinkedIn profiles by job title and location,
    filter by Open to Work status, and export results.
    """
    setup_logger()
    logger = get_logger()

    print_banner()

    if not job:
        job = Prompt.ask("[cyan]Job title to search for[/cyan]")

    if not location:
        location = Prompt.ask("[cyan]Location[/cyan]", default="")

    if not max_profiles:
        max_profiles = IntPrompt.ask(
            "[cyan]Maximum profiles to collect[/cyan]",
            default=100,
        )

    max_profiles = min(max_profiles, config.MAX_PROFILES_PER_SESSION)

    console.print()
    console.print(f"[bold]Search:[/bold] {job}")
    console.print(f"[bold]Location:[/bold] {location or 'Any'}")
    console.print(f"[bold]Max profiles:[/bold] {max_profiles}")
    console.print(f"[bold]Filter:[/bold] {'All profiles' if all_profiles else 'Open to Work only'}")
    console.print(f"[bold]Output:[/bold] {output.upper()}")
    console.print()

    if not Confirm.ask("Start scraping?", default=True):
        console.print("[yellow]Cancelled[/yellow]")
        return

    profiles = []

    try:
        with LinkedInScraper(headless=headless) as scraper:
            for profile in scraper.scrape_search_results(
                job_title=job,
                location=location,
                max_profiles=max_profiles,
                open_to_work_only=not all_profiles,
            ):
                profiles.append(profile)

    except KeyboardInterrupt:
        console.print("\n[yellow]Scraping interrupted by user[/yellow]")

    except Exception as e:
        logger.error(f"Scraping error: {e}")
        console.print(f"[red]Error: {e}[/red]")

    if not profiles:
        console.print("[yellow]No profiles found[/yellow]")
        return

    console.print()
    print_results_table(profiles)
    console.print()

    try:
        if output == "csv":
            filepath = CSVExporter.export(profiles)
            console.print(f"[green]Exported to: {filepath}[/green]")

        elif output == "sheets":
            sheets_id = sheet_id or config.GOOGLE_SHEETS_ID
            if not sheets_id:
                sheets_id = Prompt.ask("[cyan]Google Sheets ID[/cyan]")

            exporter = GoogleSheetsExporter(spreadsheet_id=sheets_id)
            exporter.export(profiles, clear_existing=True)
            console.print(f"[green]Exported to Google Sheets[/green]")
            console.print(f"[blue]https://docs.google.com/spreadsheets/d/{sheets_id}[/blue]")

    except Exception as e:
        logger.error(f"Export error: {e}")
        console.print(f"[red]Export error: {e}[/red]")

        if output == "sheets":
            console.print("[yellow]Falling back to CSV export...[/yellow]")
            filepath = CSVExporter.export(profiles)
            console.print(f"[green]Exported to: {filepath}[/green]")

    console.print()
    console.print(f"[bold green]Done! Collected {len(profiles)} profiles.[/bold green]")


if __name__ == "__main__":
    main()
