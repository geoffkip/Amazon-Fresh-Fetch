# Building Installers for Amazon Fresh Fetch

This guide explains how to create executable installers for both Windows (.exe) and macOS (.dmg).

## Prerequisites

### For Windows Build:
- Python 3.8+ installed
- PyInstaller: `pip install pyinstaller`
- Windows machine (or Wine for cross-platform building)

### For macOS Build:
- Python 3.8+ installed
- Xcode Command Line Tools: `xcode-select --install`
- create-dmg (optional, for better DMG creation): `brew install create-dmg`

## Building

### Quick Build (Auto-detect platform):
```bash
chmod +x build.sh
./build.sh
```

### Windows Build:
```bash
python build_windows.py
```

The executable will be in the `dist/` directory as `AmazonFreshFetch.exe`.

### macOS Build:
```bash
python3 build_mac.py
```

The DMG will be in the `dist/` directory as `AmazonFreshFetch-Installer.dmg`.

## How the Installer Works

1. **Download**: The installer downloads the latest code from GitHub
2. **Install**: Sets up Python virtual environment and installs dependencies
3. **Configure**: Prompts user for Google API key and creates .env file
4. **Launch**: Creates launcher scripts and optionally launches the app

## Distribution

### Windows:
- Distribute `AmazonFreshFetch.exe` from the `dist/` folder
- Users double-click to run the installer
- The installer creates everything in `~/AmazonFreshFetch/`

### macOS:
- Distribute `AmazonFreshFetch-Installer.dmg` from the `dist/` folder
- Users mount the DMG and drag the app to Applications
- Or distribute the .app bundle directly

## Testing the Installer

Before distributing:

1. Test on a clean system (or VM)
2. Verify all dependencies install correctly
3. Test API key input
4. Verify the app launches successfully
5. Test Playwright browser installation

## Troubleshooting

### Windows:
- If PyInstaller fails, ensure all dependencies are installed
- Check that `installer.py` runs correctly first
- Verify Python path is correct

### macOS:
- If DMG creation fails, use Disk Utility manually
- Ensure app bundle has correct permissions: `chmod +x dist/Amazon\ Fresh\ Fetch.app/Contents/MacOS/AmazonFreshFetch`
- Test on a clean macOS system

## Customization

### Adding an Icon:

**Windows:**
1. Create `icon.ico` file
2. Update `build_windows.py`: `--icon=icon.ico`

**macOS:**
1. Create `icon.icns` file
2. Place in `Resources/` folder in app bundle
3. Update Info.plist

### Changing Installation Directory:

Edit `installer.py`:
```python
INSTALL_DIR = Path.home() / "AmazonFreshFetch"  # Change this
```

### Adding More Configuration:

Edit `installer.py` to add more setup steps in the `main()` function.

