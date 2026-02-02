# LinkedIn Open to Work Scraper

Search LinkedIn profiles by job title and location, automatically filter by "Open to Work" status, and export results to CSV.

## Features

- Search by job title and location (e.g., "Testing Engineer" in "Lille, France")
- Auto-detect "Open to Work" badge on profiles
- Export to CSV
- Human-like behavior to avoid detection
- Uses your existing Chrome browser and LinkedIn session

## Requirements

- Python 3.11 or higher ([Download](https://www.python.org/downloads/))
- Google Chrome browser ([Download](https://www.google.com/chrome/))
- Git ([Download](https://git-scm.com/downloads))
- LinkedIn account

## Important

**Before running the script, you MUST:**
1. Close ALL Google Chrome windows
2. Be logged into LinkedIn in Chrome (before closing it)

The script uses your existing Chrome profile to access your LinkedIn session.

## Quick Start

### Windows

```bash
# Clone the repository
git clone https://github.com/nolancacheux/linkedin-opentowork-scraper.git
cd linkedin-opentowork-scraper

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure
copy .env.example .env

# Run
python -m src.main
```

### macOS / Linux

```bash
# Clone the repository
git clone https://github.com/nolancacheux/linkedin-opentowork-scraper.git
cd linkedin-opentowork-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env

# Run
python -m src.main
```

## Usage

### Interactive Mode

Run without arguments to get prompted for input:

```bash
python -m src.main
```

The script will ask for:
- Job title (e.g., "Testing Engineer")
- Location (e.g., "Lille, France")
- Maximum number of profiles to scrape

### Command Line Mode

```bash
python -m src.main --job "Testing Engineer" --location "Lille" --max 100
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--job` | `-j` | Job title to search | (prompt) |
| `--location` | `-l` | Location filter | (prompt) |
| `--max` | `-m` | Max profiles to collect | 100 |
| `--headless` | | Run browser headless | false |
| `--all-profiles` | | Include non-Open to Work | false |

## Configuration

Edit `.env` to customize settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `MIN_DELAY` | Minimum delay between actions (seconds) | 2 |
| `MAX_DELAY` | Maximum delay between actions (seconds) | 5 |
| `SCROLL_PAUSE` | Pause after each scroll (seconds) | 1 |
| `MAX_PROFILES_PER_SESSION` | Safety limit per session | 500 |

## Output

CSV files are saved in the `output/` folder:

```
output/linkedin_opentowork_20260202_083000.csv
```

The scraper collects the following data:

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

Recommendations:
- Keep searches under 200 profiles per session
- Wait at least a few hours between sessions
- Use a secondary LinkedIn account if possible

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [Usage Guide](docs/USAGE.md) - How to use the scraper
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## Disclaimer

This tool is for educational and research purposes only.

Scraping LinkedIn may violate their Terms of Service. Use at your own risk. The authors are not responsible for any account bans or legal issues arising from the use of this tool.

## License

MIT License - see [LICENSE](LICENSE) for details.
