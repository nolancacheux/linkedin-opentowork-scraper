# Usage Guide

## Basic Usage

### Interactive Mode

Run without arguments for interactive prompts:

```bash
python -m src.main
```

The script will ask for:
1. Job title (e.g., "Testing Engineer", "Data Scientist")
2. Location (e.g., "Lille, France", "Paris")
3. Maximum number of profiles to collect

### Command Line Mode

Specify all options via command line:

```bash
python -m src.main --job "Testing Engineer" --location "Lille" --max 100
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--job` | `-j` | Job title to search | (prompt) |
| `--location` | `-l` | Location filter | (prompt) |
| `--max` | `-m` | Max profiles to collect | 100 |
| `--output` | `-o` | Output format (csv/sheets) | csv |
| `--sheet-id` | | Google Sheets ID | (from .env) |
| `--headless` | | Run browser headless | false |
| `--all-profiles` | | Include non-Open to Work | false |

## Examples

### Search for QA Engineers in Paris, export to CSV

```bash
python -m src.main -j "QA Engineer" -l "Paris, France" -m 50
```

### Search and export to Google Sheets

```bash
python -m src.main -j "Data Scientist" -l "Lyon" --output sheets --sheet-id YOUR_SHEET_ID
```

### Collect all profiles (not just Open to Work)

```bash
python -m src.main -j "DevOps Engineer" -l "Toulouse" --all-profiles
```

## Workflow

1. **Browser opens**: The script opens your Chrome browser
2. **Login check**: If not logged into LinkedIn, you'll be prompted to log in
3. **Search**: The script navigates to LinkedIn and performs the search
4. **Scraping**: Profiles are scraped with human-like delays
5. **Export**: Results are exported to CSV or Google Sheets

## Output

### CSV Output

CSV files are saved in the `output/` directory with timestamps:

```
output/linkedin_opentowork_20260201_153045.csv
```

### Google Sheets Output

Data is written to the specified spreadsheet starting at cell A1.

## Tips

### Avoid Detection

- Keep `max` under 200 for a single session
- Don't run multiple sessions in a short time
- Let the script use natural delays (don't reduce them)

### Best Results

- Be specific with job titles
- Include city name in location
- Run during off-peak hours

### If You Get Blocked

1. Stop the script immediately
2. Wait at least 24 hours before running again
3. Consider using a different LinkedIn account
4. Reduce the number of profiles per session
