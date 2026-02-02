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
