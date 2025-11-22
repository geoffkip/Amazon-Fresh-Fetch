#!/usr/bin/env python3
"""
Build script for creating Mac .dmg installer.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_app_bundle():
    """Create macOS .app bundle."""
    app_name = "Amazon Fresh Fetch.app"
    app_path = Path("dist") / app_name
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Create directory structure
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>AmazonFreshFetch</string>
    <key>CFBundleIdentifier</key>
    <string>com.amazonfreshfetch.app</string>
    <key>CFBundleName</key>
    <string>Amazon Fresh Fetch</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
</dict>
</plist>
"""
    
    with open(contents_path / "Info.plist", "w") as f:
        f.write(info_plist)
    
    # Create launcher script - Use PyInstaller bundled version
    # First, we need to build the standalone installer with PyInstaller
    launcher_script = macos_path / "AmazonFreshFetch"
    
    # Check if PyInstaller executable exists, if not, create a script that uses system Python
    installer_exe = Path("dist") / "AmazonFreshFetch-Installer"
    if installer_exe.exists() or (Path("dist") / "AmazonFreshFetch-Installer.app").exists():
        # Use the bundled executable
        launcher_content = f"""#!/bin/bash
cd "$(dirname "$0")/../../../.."
exec "$(dirname "$0")/AmazonFreshFetch-Installer"
"""
    else:
        # Fallback: use system Python (requires Python to be installed)
        launcher_content = """#!/bin/bash
cd "$(dirname "$0")/../../.."
exec python3 installer_standalone.py
"""
    
    with open(launcher_script, "w") as f:
        f.write(launcher_content)
    
    os.chmod(launcher_script, 0o755)
    
    return app_path

def create_dmg():
    """Create .dmg file using create-dmg or hdiutil."""
    app_path = Path("dist") / "Amazon Fresh Fetch.app"
    
    if not app_path.exists():
        print("Error: App bundle not found!")
        return False
    
    dmg_name = "AmazonFreshFetch-Installer.dmg"
    dmg_path = Path("dist") / dmg_name
    
    # Try create-dmg first (install with: brew install create-dmg)
    try:
        subprocess.run([
            "create-dmg",
            "--volname", "Amazon Fresh Fetch",
            "--window-pos", "200", "120",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--app-drop-link", "425", "200",
            str(dmg_path),
            str(app_path)
        ], check=True)
        print(f"DMG created successfully: {dmg_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to hdiutil
        print("create-dmg not found, using hdiutil...")
        try:
            # Create temporary directory
            temp_dir = Path("dist") / "dmg_temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            # Copy app to temp directory
            shutil.copytree(app_path, temp_dir / app_path.name)
            
            # Create DMG
            subprocess.run([
                "hdiutil", "create",
                "-volname", "Amazon Fresh Fetch",
                "-srcfolder", str(temp_dir),
                "-ov",
                "-format", "UDZO",
                str(dmg_path)
            ], check=True)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            print(f"DMG created successfully: {dmg_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating DMG: {e}")
            print("\nTo create DMG manually:")
            print("1. Open Disk Utility")
            print("2. File > New Image > Image from Folder")
            print(f"3. Select: {app_path}")
            print("4. Save as: AmazonFreshFetch-Installer.dmg")
            return False

def build_standalone_installer():
    """Build standalone installer using PyInstaller."""
    print("Building standalone installer with PyInstaller...")
    
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Clean previous builds
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=AmazonFreshFetch-Installer",
        "--onefile",
        "--console",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.simpledialog",
        "--hidden-import=urllib.request",
        "--hidden-import=zipfile",
        "--hidden-import=tempfile",
        "--collect-all=tkinter",
        "installer.py"
    ]
    
    print("Running PyInstaller (this may take a few minutes)...")
    subprocess.run(cmd, check=True)
    
    installer_exe = Path("dist") / "AmazonFreshFetch-Installer"
    if installer_exe.exists():
        os.chmod(installer_exe, 0o755)
        print(f"✅ Standalone installer created: {installer_exe}")
        return installer_exe
    else:
        print("❌ Build failed")
        return None

def main():
    print("Building macOS installer...")
    print("\nOption 1: Standalone installer (recommended - no Python needed)")
    print("Option 2: App bundle (requires Python on user's system)")
    
    choice = input("\nChoose option (1 or 2, default=1): ").strip() or "1"
    
    if choice == "1":
        # Build standalone installer
        installer_exe = build_standalone_installer()
        if installer_exe:
            print(f"\n✅ Standalone installer ready: {installer_exe}")
            print("   Users can run this directly - no Python needed!")
            print("\nTo create a DMG:")
            print("  1. Create a folder")
            print(f"  2. Copy {installer_exe.name} into it")
            print("  3. Use Disk Utility to create DMG from folder")
    else:
        # Create app bundle (old method)
        app_path = create_app_bundle()
        print(f"App bundle created: {app_path}")
        
        # Create DMG
        if create_dmg():
            print("\nBuild complete! DMG is in the 'dist' directory.")
        else:
            print("\nApp bundle created. Please create DMG manually or install create-dmg:")
            print("  brew install create-dmg")

if __name__ == "__main__":
    main()

