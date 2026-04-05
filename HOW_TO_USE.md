# PackinClub Invoice Dashboard - Setup Guide

## For First Time Setup (Only Once)

1. **Unzip** this folder anywhere on your computer (Desktop is fine)
2. Open the folder and **double-click** `INSTALL_AND_RUN.bat`
3. If Python is not installed, it will open the download page for you:
   - Click **"Download Python"**
   - ⚠️ **IMPORTANT**: Check the box **"Add Python to PATH"** at the bottom of the installer!
   - Click **"Install Now"**
   - After installation, double-click `INSTALL_AND_RUN.bat` again
4. Wait 1-2 minutes while it installs everything
5. Your browser will open with the dashboard!

## For Daily Use (After First Setup)

Just **double-click** `START_Dashboard.bat` — that's it!

Your browser will open automatically with the dashboard.

## Important Notes

- **Keep the black command window OPEN** while using the dashboard. Closing it will stop the app.
- Your data (customers, products, invoices) is saved in `dashboard.db` inside this folder.
- **To back up your data**, just copy the `dashboard.db` file somewhere safe.
- The app runs on your computer only — no internet needed after setup.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python is not recognized" | Reinstall Python and make sure to check **"Add to PATH"** |
| Browser doesn't open | Manually go to **http://localhost:8501** in your browser |
| App won't start | Close any other command windows running the dashboard, then try again |
| Need to reset everything | Delete `dashboard.db` and restart (⚠️ this erases all data) |
