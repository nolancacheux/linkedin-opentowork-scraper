# Installation Guide

Complete guide to set up the LinkedIn Open to Work Scraper from scratch.

## Prerequisites

### 1. Install Python 3.11+

**Windows:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or higher
3. Run the installer
4. IMPORTANT: Check "Add Python to PATH" during installation
5. Click "Install Now"

To verify installation, open Command Prompt and run:
```bash
python --version
```

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2. Install Google Chrome

Download and install from: https://www.google.com/chrome/

### 3. Install Git

**Windows:**
1. Download from https://git-scm.com/download/win
2. Run installer with default options

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

### 4. LinkedIn Account

You need a LinkedIn account. Log into LinkedIn via Chrome before running the scraper.

---

## Installation Steps

### Step 1: Clone the Repository

Open a terminal (Command Prompt on Windows) and run:

```bash
git clone https://github.com/nolancacheux/linkedin-opentowork-scraper.git
cd linkedin-opentowork-scraper
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browser

```bash
playwright install chromium
```

### Step 5: Configure Environment

**Windows:**
```bash
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

### Step 6: Verify Installation

```bash
python -m src.main --help
```

You should see the help message with available options.

---

## Google Sheets Setup (Optional)

Follow these steps to enable Google Sheets export.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click "Select a project" (top bar) > "New Project"
4. Enter a project name (e.g., "LinkedIn Scraper")
5. Click "Create"
6. Wait for the project to be created, then select it

### Step 2: Enable Google Sheets API

1. In the Google Cloud Console, go to the menu (hamburger icon, top left)
2. Click "APIs & Services" > "Library"
3. Search for "Google Sheets API"
4. Click on "Google Sheets API"
5. Click "Enable"

### Step 3: Create Service Account

1. Go to menu > "APIs & Services" > "Credentials"
2. Click "Create Credentials" (top of page)
3. Select "Service Account"
4. Enter a name (e.g., "scraper-service")
5. Click "Create and Continue"
6. Skip the optional steps, click "Done"

### Step 4: Generate JSON Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Select "JSON"
6. Click "Create"
7. A JSON file will be downloaded automatically

### Step 5: Configure the Scraper

1. Rename the downloaded JSON file to `credentials.json`
2. Move it to the project root folder (same level as README.md)
3. Open `.env` file and set your Google Sheet ID:

```
GOOGLE_SHEETS_ID=your_spreadsheet_id_here
```

**How to find your Google Sheet ID:**
- Open your Google Sheet
- Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- The SPREADSHEET_ID is the long string between `/d/` and `/edit`

### Step 6: Share the Spreadsheet

1. Open the `credentials.json` file
2. Find the `client_email` field (looks like: `name@project.iam.gserviceaccount.com`)
3. Copy this email
4. Open your Google Sheet
5. Click "Share" (top right)
6. Paste the service account email
7. Select "Editor" permission
8. Click "Send" (ignore the warning about not notifying)

---

## Troubleshooting

### "python" is not recognized (Windows)

Python was not added to PATH. Reinstall Python and check "Add Python to PATH".

### "git" is not recognized

Git is not installed. Download from https://git-scm.com/

### Chrome not found

Make sure Chrome is installed in the default location:
- Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- macOS: `/Applications/Google Chrome.app`

### Permission denied (Linux/macOS)

Use `python3` instead of `python`:
```bash
python3 -m venv venv
python3 -m src.main
```

### Playwright installation fails

Try:
```bash
pip uninstall playwright
pip install playwright
playwright install chromium --with-deps
```

### Google Sheets "Permission denied"

1. Make sure you shared the spreadsheet with the service account email
2. Make sure you gave "Editor" access (not "Viewer")
3. Wait a few minutes for permissions to propagate

### "credentials.json not found"

1. Make sure the file is in the project root folder
2. Make sure it's named exactly `credentials.json`
3. Check `GOOGLE_CREDENTIALS_PATH` in `.env` if using a different location
