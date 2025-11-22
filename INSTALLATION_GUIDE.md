# Installation Guide for End Users

## 🎯 Quick Start

**Easiest Method:** Download the standalone installer - no Python or Git needed!

## 📥 Download Options

### Option 1: Standalone Installer (Recommended - No Dependencies!)

**For Windows:**
1. Go to the [Releases](https://github.com/geoffkip/Amazon-Fresh-Fetch/releases) page
2. Download `AmazonFreshFetch-Installer.exe`
3. Double-click to run
4. Follow the setup wizard

**For macOS:**
1. Go to the [Releases](https://github.com/geoffkip/Amazon-Fresh-Fetch/releases) page
2. Download `AmazonFreshFetch-Installer.dmg` (or the standalone executable)
3. Open the DMG or run the executable
4. Follow the setup wizard

**What you need:**
- ✅ Internet connection
- ❌ **NO Python needed** (bundled in installer)
- ❌ **NO Git needed** (downloads ZIP automatically)

---

### Option 2: Source Code (For Developers or Advanced Users)

**Download as ZIP:**
1. Go to the GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Follow instructions below based on your OS

---

## 🪟 Windows Installation

### Using Standalone Installer (Easiest)

1. **Download** `AmazonFreshFetch-Installer.exe` from Releases
2. **Run** the installer (Windows may show security warning - click "More info" → "Run anyway")
3. **Wait** for installation (downloads app, installs dependencies - takes 5-10 minutes)
4. **Enter** your Google API key when prompted
5. **Launch** the app from the installation folder or desktop shortcut

**Installation Location:** `C:\Users\YourName\AmazonFreshFetch\`

### Using Source Code

1. **Download ZIP** from GitHub and extract it
2. **Open Command Prompt** or PowerShell in the extracted folder
3. **Run installer:**
   ```cmd
   python installer_standalone.py
   ```
   (If you don't have Python, download it from [python.org](https://www.python.org/downloads/))

4. **Follow** the setup wizard
5. **Launch** using `launch.bat` in the installation folder

---

## 🍎 macOS Installation

### Using Standalone Installer (Easiest)

1. **Download** `AmazonFreshFetch-Installer.dmg` or the standalone executable from Releases
2. **Open** the DMG (double-click) or run the executable
3. **Security Warning:** If macOS says "App can't be opened":
   - Right-click the app → "Open"
   - Or: System Preferences → Security & Privacy → "Open Anyway"
4. **Run** the installer
5. **Wait** for installation (downloads app, installs dependencies - takes 5-10 minutes)
6. **Enter** your Google API key when prompted
7. **Launch** the app

**Installation Location:** `~/AmazonFreshFetch/`

### Using Source Code

1. **Download ZIP** from GitHub and extract it
2. **Open Terminal** in the extracted folder
3. **Run installer:**
   ```bash
   python3 installer_standalone.py
   ```
   (If you don't have Python, install it: `brew install python3` or download from [python.org](https://www.python.org/downloads/))

4. **Follow** the setup wizard
5. **Launch** using:
   ```bash
   ~/AmazonFreshFetch/launch.sh
   ```

---

## 🔑 Getting Your Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key
5. Paste it into the installer when prompted

**Important:** Keep your API key secret! Don't share it publicly.

---

## 🚀 After Installation

### Launching the App

**Windows:**
- Double-click `launch.bat` in `C:\Users\YourName\AmazonFreshFetch\`
- Or use the desktop shortcut (if created)

**macOS:**
- Run: `~/AmazonFreshFetch/launch.sh`
- Or double-click the app in Applications (if installed there)

The app will open in your web browser at `http://localhost:8501` (or similar port).

---

## ❓ Troubleshooting

### Windows Issues

**"Windows protected your PC" warning:**
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- The installer is safe

**"Python not found" error:**
- Use the standalone installer instead (includes Python)
- Or install Python from [python.org](https://www.python.org/downloads/)

**Installation fails:**
- Check internet connection
- Try running as Administrator
- Check Windows Defender isn't blocking it

### macOS Issues

**"App can't be opened because it's from an unidentified developer":**
- Right-click → "Open"
- Or: System Preferences → Security & Privacy → "Open Anyway"

**"Python not found" error:**
- Use the standalone installer instead (includes Python)
- Or install Python: `brew install python3`

**Installation fails:**
- Check internet connection
- Make sure you have Xcode Command Line Tools: `xcode-select --install`

### General Issues

**Download fails:**
- Check internet connection
- Verify GitHub repository is accessible
- Try again later

**Dependencies fail to install:**
- Check internet connection
- Try running installer again
- Check firewall settings

**App won't launch:**
- Verify installation completed successfully
- Check `.env` file exists with your API key
- Try running launcher script manually

---

## 🔄 Updating

To update to the latest version:

1. **Download** the latest installer from Releases
2. **Run** it again - it will update your existing installation
3. Your settings and meal plan history are preserved

---

## 🗑️ Uninstalling

### Windows

1. Delete the installation folder: `C:\Users\YourName\AmazonFreshFetch\`
2. Remove desktop shortcuts (if any)

### macOS

1. Delete the installation folder:
   ```bash
   rm -rf ~/AmazonFreshFetch
   ```
2. Remove from Applications (if installed there)

---

## 📞 Need Help?

- Check the [README.md](README.md) for more information
- Open an issue on [GitHub](https://github.com/geoffkip/Amazon-Fresh-Fetch/issues)
- Review the troubleshooting section above

---

## ✅ Installation Checklist

After installation, verify:

- [ ] Installation completed without errors
- [ ] `.env` file created with your API key
- [ ] Launcher script exists
- [ ] App launches successfully
- [ ] Browser opens with Streamlit interface
- [ ] Can create a meal plan
- [ ] Browser automation works (Playwright)

---

**Enjoy using Amazon Fresh Fetch! 🥕🛒**

