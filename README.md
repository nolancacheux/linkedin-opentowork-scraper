# LinkedIn Open to Work Scraper

Search LinkedIn profiles by job title and location, automatically filter by "Open to Work" status, and export results to Google Sheets or CSV.

## Features

- Search by job title and location (e.g., "Testing Engineer" in "Lille, France")
- Auto-detect "Open to Work" badge on profiles
- Export to Google Sheets or CSV
- Human-like behavior to avoid detection
- Uses your existing Chrome browser and LinkedIn session

## Requirements

- Python 3.11+
- Google Chrome browser
- LinkedIn account (logged in via Chrome)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/nolancacheux/linkedin-opentowork-scraper.git
cd linkedin-opentowork-scraper
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chromium
```

### 5. (Optional) Set up Google Sheets export

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for Google Sheets API setup.

## Usage

### Basic usage

```bash
python -m src.main
```

The script will prompt you for:
- Job title (e.g., "Testing Engineer")
- Location (e.g., "Lille, France")
- Maximum number of profiles to scrape

### Command line options

```bash
python -m src.main --job "Testing Engineer" --location "Lille" --max 100
```

### Export options

```bash
# Export to CSV (default)
python -m src.main --output csv

# Export to Google Sheets
python -m src.main --output sheets --sheet-id YOUR_SHEET_ID
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `MIN_DELAY` | Minimum delay between actions (seconds) | 2 |
| `MAX_DELAY` | Maximum delay between actions (seconds) | 5 |
| `SCROLL_PAUSE` | Pause after each scroll (seconds) | 1 |
| `MAX_PROFILES_PER_SESSION` | Safety limit per session | 500 |
| `GOOGLE_SHEETS_ID` | Target Google Sheets ID | - |

## Output

The scraper collects the following data for each "Open to Work" profile:

| Field | Description |
|-------|-------------|
| `first_name` | First name |
| `last_name` | Last name |
| `headline` | Profile headline/title |
| `current_company` | Current company (if available) |
| `location` | Location |
| `profile_url` | LinkedIn profile URL |
| `scraped_at` | Timestamp |

## Safety

This tool implements several anti-detection measures:

- Randomized delays between actions (2-5 seconds)
- Natural scrolling behavior
- Long pauses every 50 actions
- Uses your existing browser profile (not headless)
- Respects session limits

## Disclaimer

This tool is for educational and research purposes only.

Scraping LinkedIn may violate their Terms of Service. Use at your own risk. The authors are not responsible for any account bans or legal issues arising from the use of this tool.

## License

MIT License - see [LICENSE](LICENSE) for details.
