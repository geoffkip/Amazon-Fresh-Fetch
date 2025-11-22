#!/usr/bin/env python3
"""
Build standalone installers that bundle Python (no dependencies needed for end users).
This creates truly standalone installers.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def build_windows_standalone():
    """Build Windows standalone installer with PyInstaller."""
    print("Building Windows standalone installer...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
    
    # PyInstaller command - bundles Python with the installer
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
    
    exe_path = dist_dir / "AmazonFreshFetch-Installer.exe"
    if exe_path.exists():
        print(f"\n✅ Success! Standalone installer created: {exe_path}")
        print(f"   Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        print("\nThis executable includes Python - users don't need Python installed!")
    else:
        print("❌ Build failed - executable not found")

def build_mac_standalone():
    """Build macOS standalone installer."""
    print("Building macOS standalone installer...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
    
    # PyInstaller command for macOS app bundle
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
    
    exe_path = dist_dir / "AmazonFreshFetch-Installer"
    if exe_path.exists():
        print(f"\n✅ Success! Standalone installer created: {exe_path}")
        print(f"   Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        print("\nThis executable includes Python - users don't need Python installed!")
        
        # Make it executable
        os.chmod(exe_path, 0o755)
        
        # Optionally create DMG
        print("\nTo create a DMG, run: python3 build_mac.py")
    else:
        print("❌ Build failed - executable not found")

def main():
    """Main build function."""
    system = platform.system()
    
    print("="*60)
    print("Building Standalone Installer")
    print("="*60)
    print(f"Platform: {system}\n")
    
    if system == "Windows":
        build_windows_standalone()
    elif system == "Darwin":  # macOS
        build_mac_standalone()
    else:
        print(f"Unsupported platform: {system}")
        print("Please build on Windows or macOS")

if __name__ == "__main__":
    main()

