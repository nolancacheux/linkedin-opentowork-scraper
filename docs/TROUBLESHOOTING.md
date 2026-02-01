# Troubleshooting Guide

## Common Issues

### Browser Issues

#### "Failed to start browser"

**Cause**: Chrome user data directory is locked or inaccessible.

**Solutions**:
1. Close all Chrome windows before running the script
2. Set a custom `CHROME_USER_DATA_DIR` in `.env`
3. Try running with a fresh browser profile

#### "Chrome not found"

**Cause**: Chrome is not installed or not in the default location.

**Solutions**:
1. Install Google Chrome
2. Verify Chrome is in the default path for your OS
3. Set the path manually in the code if needed

### LinkedIn Issues

#### "Not logged in"

**Cause**: No active LinkedIn session in Chrome.

**Solutions**:
1. Open Chrome manually and log into LinkedIn
2. Make sure "Stay signed in" is checked
3. Clear Chrome cookies and log in again

#### "No profile cards found"

**Cause**: LinkedIn page structure may have changed or search returned no results.

**Solutions**:
1. Try a different search query
2. Check if LinkedIn has updated their UI
3. Try searching manually to verify results exist

#### "Rate limited" or CAPTCHA

**Cause**: LinkedIn detected automated behavior.

**Solutions**:
1. Stop immediately
2. Wait 24+ hours before trying again
3. Reduce `MAX_PROFILES_PER_SESSION` in `.env`
4. Increase `MIN_DELAY` and `MAX_DELAY` in `.env`

### Export Issues

#### "Spreadsheet ID not configured"

**Cause**: Google Sheets ID not set.

**Solutions**:
1. Set `GOOGLE_SHEETS_ID` in `.env`
2. Pass `--sheet-id` on command line

#### "Credentials file not found"

**Cause**: Google service account credentials missing.

**Solutions**:
1. Follow the setup in INSTALLATION.md
2. Ensure `credentials.json` is in project root
3. Set correct path in `GOOGLE_CREDENTIALS_PATH`

#### "Permission denied" on Google Sheets

**Cause**: Service account doesn't have access to the spreadsheet.

**Solutions**:
1. Share the spreadsheet with the service account email
2. Grant "Editor" permissions
3. Wait a few minutes for permissions to propagate

### Python Issues

#### "ModuleNotFoundError"

**Cause**: Dependencies not installed or wrong Python version.

**Solutions**:
1. Activate your virtual environment
2. Run `pip install -r requirements.txt`
3. Verify Python version is 3.11+

#### "Playwright not found"

**Cause**: Playwright browsers not installed.

**Solutions**:
```bash
playwright install chromium
```

## Getting Help

If you encounter an issue not listed here:

1. Check the logs for detailed error messages
2. Search for similar issues online
3. Open an issue on GitHub with:
   - Python version
   - OS and version
   - Full error message
   - Steps to reproduce

## Reset Everything

If things are completely broken:

```bash
# Remove virtual environment
rm -rf venv

# Recreate
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall
pip install -r requirements.txt
playwright install chromium

# Reset config
cp .env.example .env
```
