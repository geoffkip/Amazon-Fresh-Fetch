# Distribution Guide for Developers

## How to Prepare Releases for GitHub

This guide explains how to package and distribute the installer so users can easily install the app.

## 📦 Creating Release Packages

### Step 1: Build Standalone Installers

**On Windows:**
```bash
python build_standalone.py
# Creates: dist/AmazonFreshFetch-Installer.exe
```

**On macOS:**
```bash
python3 build_standalone.py
# Creates: dist/AmazonFreshFetch-Installer

# Or create DMG:
python3 build_mac.py
# Creates: dist/AmazonFreshFetch-Installer.dmg
```

### Step 2: Create Release on GitHub

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version (e.g., `v1.0.0`)
4. Upload files:
   - `AmazonFreshFetch-Installer.exe` (Windows)
   - `AmazonFreshFetch-Installer` (macOS) or create a DMG
   - Optionally: Source code ZIP

### Step 3: Create DMG for macOS (Optional but Recommended)

```bash
# After building standalone installer
python3 build_mac.py
# Choose option 1 for standalone, then create DMG manually or use create-dmg
```

Or manually:
1. Create a folder named "Amazon Fresh Fetch Installer"
2. Copy `AmazonFreshFetch-Installer` into it
3. Open Disk Utility
4. File → New Image → Image from Folder
5. Select the folder
6. Save as `AmazonFreshFetch-Installer.dmg`

## 📋 Release Checklist

Before publishing a release:

- [ ] Build standalone installer for Windows
- [ ] Build standalone installer for macOS
- [ ] Create DMG for macOS (optional)
- [ ] Test installer on clean system (or VM)
- [ ] Verify all dependencies install correctly
- [ ] Test API key input
- [ ] Verify app launches successfully
- [ ] Update version numbers in code
- [ ] Update CHANGELOG.md (if you have one)
- [ ] Write release notes

## 🎯 What Users Will Download

### Recommended Distribution:

**GitHub Releases Page:**
- `AmazonFreshFetch-Installer.exe` (Windows, ~50-100 MB)
- `AmazonFreshFetch-Installer.dmg` (macOS, ~50-100 MB)
- Source code ZIP (optional, for developers)

### Alternative: Direct ZIP Download

If you want users to download source code as ZIP:

1. Users download ZIP from GitHub
2. Extract it
3. Run: `python3 installer_standalone.py` (requires Python)
   OR
4. Build standalone installer themselves (for developers)

## 📝 Release Notes Template

```markdown
## Version 1.0.0

### Installation

**Windows:**
1. Download `AmazonFreshFetch-Installer.exe`
2. Double-click to run
3. Follow setup wizard

**macOS:**
1. Download `AmazonFreshFetch-Installer.dmg`
2. Open DMG and run installer
3. Follow setup wizard

### Requirements
- Internet connection
- No Python or Git needed (bundled in installer)

### Features
- AI-powered meal planning
- Automated Amazon Fresh shopping
- Budget tracking
- And more!

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions.
```

## 🔄 Update Process

When releasing updates:

1. **Build new installers** with updated code
2. **Test thoroughly** on clean systems
3. **Create new GitHub release** with new version tag
4. **Upload new installers** to release
5. **Update documentation** if needed

Users can simply download and run the new installer - it will update their existing installation.

## 🌐 Alternative Distribution Methods

### Option 1: GitHub Releases (Recommended)
- Easy for users
- Automatic versioning
- Release notes
- Download statistics

### Option 2: Direct Download Link
- Host installers on your website
- Custom download page
- More control over branding

### Option 3: Package Managers (Advanced)
- Homebrew (macOS): `brew install --cask amazon-fresh-fetch`
- Chocolatey (Windows): `choco install amazon-fresh-fetch`
- Requires maintaining package definitions

## 📊 File Sizes

Expected file sizes:
- **Windows .exe**: ~50-100 MB (includes Python)
- **macOS executable**: ~50-100 MB (includes Python)
- **macOS .dmg**: ~50-100 MB (same as executable, just packaged)
- **Source code ZIP**: ~1-5 MB (without dependencies)

## ✅ Testing Before Release

Test on:
- [ ] Clean Windows 10/11 VM
- [ ] Clean macOS VM
- [ ] Different Python versions (if not using standalone)
- [ ] Different network conditions
- [ ] With and without existing installations

## 🚨 Important Notes

1. **GitHub Repository**: Make sure repo is public or users have access
2. **Branch Name**: Standalone installer downloads from `main` branch by default
3. **API Keys**: Never include API keys in releases
4. **Security**: Consider code signing for Windows/macOS (requires certificates)
5. **Updates**: Users can run installer again to update

## 📞 User Support

Provide users with:
- Clear installation instructions (INSTALLATION_GUIDE.md)
- Troubleshooting guide
- GitHub Issues for bug reports
- Clear release notes

---

**Ready to distribute?** Build the installers, test them, and create your first GitHub release! 🚀

