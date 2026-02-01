# Installation Guide

## Prerequisites

- Python 3.11 or higher
- Google Chrome browser
- LinkedIn account

## Step 1: Clone the Repository

```bash
git clone https://github.com/nolancacheux/linkedin-opentowork-scraper.git
cd linkedin-opentowork-scraper
```

## Step 2: Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

## Step 5: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to customize settings if needed.

## Step 6 (Optional): Set Up Google Sheets Export

### Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API

### Create Service Account Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the details and create
4. Go to the service account > "Keys" tab
5. Add Key > Create new key > JSON
6. Download the JSON file

### Configure the Scraper

1. Rename the downloaded file to `credentials.json`
2. Place it in the project root directory
3. Set `GOOGLE_SHEETS_ID` in `.env` to your spreadsheet ID

### Share Your Spreadsheet

1. Open your Google Spreadsheet
2. Click "Share"
3. Add the service account email (found in `credentials.json` as `client_email`)
4. Give it "Editor" access

## Verify Installation

Run the following to verify everything is set up:

```bash
python -m src.main --help
```

You should see the command-line help output.

## Troubleshooting

### Chrome not found

Make sure Google Chrome is installed in the default location, or set `CHROME_USER_DATA_DIR` in `.env`.

### Playwright issues

Try reinstalling Playwright:

```bash
pip uninstall playwright
pip install playwright
playwright install chromium
```

### Google Sheets authentication errors

1. Verify `credentials.json` is in the correct location
2. Ensure the service account has access to the spreadsheet
3. Check that the Google Sheets API is enabled in your project
