#!/usr/bin/env python3
"""
Build script for creating Windows .exe installer using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("Building Windows executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Create build directory
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    # Clean previous builds
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # PyInstaller command - Use standalone installer that doesn't need Git
    # This bundles Python with the installer, so users don't need Python installed!
    cmd = [
        "pyinstaller",
        "--name=AmazonFreshFetch-Installer",
        "--onefile",
        "--console",  # Keep console to show progress
        "--icon=NONE",  # Add icon path if you have one: --icon=icon.ico
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.simpledialog",
        "--hidden-import=urllib.request",
        "--hidden-import=zipfile",
        "--hidden-import=tempfile",
        "installer.py"
    ]
    
    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)
    
    print("\nBuild complete! Executable is in the 'dist' directory.")
    print("You can distribute 'AmazonFreshFetch.exe' to Windows users.")

if __name__ == "__main__":
    main()

