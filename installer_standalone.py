#!/usr/bin/env python3
"""
Amazon Fresh Fetch - Installer
Cross-platform installer that downloads and sets up the application.
Can be bundled with PyInstaller to create standalone executables.
"""

import os
import sys
import subprocess
import platform
import shutil
import zipfile
import urllib.request
from pathlib import Path
import tempfile

# Try to import tkinter for GUI
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# Configuration
GITHUB_REPO = "geoffkip/Amazon-Fresh-Fetch"  # Update with your repo
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
APP_NAME = "Amazon Fresh Fetch"
INSTALL_DIR = Path.home() / "AmazonFreshFetch"
VENV_DIR = INSTALL_DIR / ".venv"
APP_DIR = INSTALL_DIR / "app"

def print_status(message):
    """Print status message."""
    print(f"[*] {message}")

def print_success(message):
    """Print success message."""
    print(f"[+] {message}")

def print_error(message):
    """Print error message."""
    print(f"[-] {message}")

def check_python():
    """Check if Python 3.8+ is installed."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required!")
        print_error("Please install Python from https://www.python.org/downloads/")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def download_from_github_zip():
    """Download repository as ZIP file (no Git required)."""
    print_status("Downloading application from GitHub...")
    
    try:
        # Create temp directory for download
        temp_dir = Path(tempfile.mkdtemp())
        zip_path = temp_dir / "repo.zip"
        
        print_status("Downloading ZIP file...")
        urllib.request.urlretrieve(GITHUB_ZIP_URL, zip_path)
        print_success("Download complete")
        
        # Extract ZIP
        print_status("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the folder name (usually repo-main or repo-master)
            zip_ref.extractall(temp_dir)
            # Find the extracted folder
            extracted_folders = [f for f in temp_dir.iterdir() if f.is_dir() and f.name != zip_path.name]
            if not extracted_folders:
                raise Exception("Could not find extracted folder")
            
            extracted_folder = extracted_folders[0]
            
            # Remove old app directory if exists
            if APP_DIR.exists():
                shutil.rmtree(APP_DIR)
            
            # Move extracted folder to app directory
            shutil.move(str(extracted_folder), str(APP_DIR))
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print_success("Repository extracted successfully")
        return True
    except Exception as e:
        print_error(f"Failed to download from GitHub: {e}")
        print_error("Please check your internet connection and try again.")
        return False

def create_virtual_env():
    """Create Python virtual environment."""
    print_status("Creating virtual environment...")
    
    if VENV_DIR.exists():
        print_status("Virtual environment already exists, reusing...")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the pip command for the virtual environment."""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "pip.exe")
    else:
        return str(VENV_DIR / "bin" / "pip")

def get_python_command():
    """Get the Python command for the virtual environment."""
    if platform.system() == "Windows":
        return str(VENV_DIR / "Scripts" / "python.exe")
    else:
        return str(VENV_DIR / "bin" / "python")

def install_dependencies():
    """Install Python dependencies."""
    print_status("Installing dependencies (this may take a few minutes)...")
    
    pip_cmd = get_pip_command()
    requirements_file = APP_DIR / "requirements.txt"
    
    if not requirements_file.exists():
        print_error("requirements.txt not found!")
        return False
    
    try:
        # Upgrade pip first (silent)
        subprocess.run([pip_cmd, "install", "--upgrade", "pip", "--quiet"], 
                      check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install requirements
        print_status("Installing Python packages...")
        subprocess.run([pip_cmd, "install", "-r", str(requirements_file)], check=True)
        
        # Install Playwright browsers
        print_status("Installing Playwright browser...")
        python_cmd = get_python_command()
        subprocess.run([python_cmd, "-m", "playwright", "install", "chromium"], check=True)
        
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def setup_api_key_gui():
    """Setup API key using GUI."""
    root = tk.Tk()
    root.title(f"{APP_NAME} - Setup")
    root.geometry("500x300")
    root.resizable(False, False)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (300 // 2)
    root.geometry(f"500x300+{x}+{y}")
    
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text=f"Welcome to {APP_NAME}!", font=("Arial", 16, "bold")).pack(pady=10)
    ttk.Label(frame, text="Please enter your Google API Key:", font=("Arial", 10)).pack(pady=5)
    
    api_key_var = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=api_key_var, width=50, show="*")
    entry.pack(pady=10)
    entry.focus()
    
    ttk.Label(frame, text="Get your API key from: https://makersuite.google.com/app/apikey", 
              font=("Arial", 8), foreground="gray").pack(pady=5)
    
    result = {"api_key": None, "cancelled": False}
    
    def on_ok():
        api_key = api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key!")
            return
        result["api_key"] = api_key
        root.destroy()
    
    def on_cancel():
        result["cancelled"] = True
        root.destroy()
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
    return result["api_key"] if not result["cancelled"] else None

def setup_api_key_cli():
    """Setup API key using CLI."""
    print("\n" + "="*60)
    print(f"Welcome to {APP_NAME} Setup!")
    print("="*60)
    print("\nPlease enter your Google API Key.")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    print("\n" + "-"*60)
    
    api_key = input("Google API Key: ").strip()
    
    if not api_key:
        print_error("API key cannot be empty!")
        return None
    
    return api_key

def create_env_file(api_key):
    """Create .env file with API key."""
    print_status("Creating .env file...")
    
    env_file = APP_DIR / ".env"
    try:
        with open(env_file, "w") as f:
            f.write(f"GOOGLE_API_KEY={api_key}\n")
        print_success(".env file created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")
        return False

def create_launcher():
    """Create launcher script."""
    print_status("Creating launcher script...")
    
    if platform.system() == "Windows":
        launcher_path = INSTALL_DIR / "launch.bat"
        launcher_content = f"""@echo off
cd /d "{APP_DIR}"
if exist "{VENV_DIR}\\Scripts\\streamlit.exe" (
    "{VENV_DIR}\\Scripts\\streamlit.exe" run amazon_fresh_fetch.py
) else (
    echo Error: Streamlit not found. Please run installer again.
    pause
)
"""
    else:
        launcher_path = INSTALL_DIR / "launch.sh"
        launcher_content = f"""#!/bin/bash
cd "{APP_DIR}"
"{VENV_DIR}/bin/streamlit" run amazon_fresh_fetch.py
"""
    
    try:
        with open(launcher_path, "w") as f:
            f.write(launcher_content)
        
        if platform.system() != "Windows":
            os.chmod(launcher_path, 0o755)
        
        print_success("Launcher script created")
        return True
    except Exception as e:
        print_error(f"Failed to create launcher: {e}")
        return False

def main():
    """Main installation function."""
    print("\n" + "="*60)
    print(f"{APP_NAME} Installer")
    print("="*60 + "\n")
    
    # Check prerequisites (only Python needed now, no Git!)
    if not check_python():
        print("\n" + "="*60)
        print("INSTALLATION REQUIREMENTS:")
        print("="*60)
        print("This installer requires Python 3.8 or higher.")
        print("Download Python from: https://www.python.org/downloads/")
        print("="*60 + "\n")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create installation directory
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    print_status(f"Installation directory: {INSTALL_DIR}")
    
    # Download from GitHub (no Git needed!)
    if not download_from_github_zip():
        print("\n" + "="*60)
        print("DOWNLOAD FAILED")
        print("="*60)
        print("Please check your internet connection and try again.")
        print("="*60 + "\n")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_env():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n" + "="*60)
        print("INSTALLATION FAILED")
        print("="*60)
        print("Failed to install dependencies. Please check your internet connection.")
        print("="*60 + "\n")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Setup API key
    if GUI_AVAILABLE:
        api_key = setup_api_key_gui()
    else:
        api_key = setup_api_key_cli()
    
    if not api_key:
        print_error("Installation cancelled or API key not provided")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file(api_key):
        sys.exit(1)
    
    # Create launcher
    if not create_launcher():
        sys.exit(1)
    
    # Success message
    print("\n" + "="*60)
    print_success("Installation completed successfully!")
    print("="*60)
    print(f"\nInstallation directory: {INSTALL_DIR}")
    launcher_name = "launch.bat" if platform.system() == "Windows" else "launch.sh"
    print(f"To launch the app, run: {INSTALL_DIR / launcher_name}")
    print("\n" + "="*60 + "\n")
    
    # Ask to launch
    if GUI_AVAILABLE:
        root = tk.Tk()
        root.withdraw()
        if messagebox.askyesno("Installation Complete", "Would you like to launch the app now?"):
            root.destroy()
            launch_app()
    else:
        response = input("Would you like to launch the app now? (y/n): ").strip().lower()
        if response == 'y':
            launch_app()

def launch_app():
    """Launch the Streamlit application."""
    print_status("Launching application...")
    
    if platform.system() == "Windows":
        streamlit_cmd = VENV_DIR / "Scripts" / "streamlit.exe"
    else:
        streamlit_cmd = VENV_DIR / "bin" / "streamlit"
    
    try:
        os.chdir(APP_DIR)
        subprocess.run([str(streamlit_cmd), "run", "amazon_fresh_fetch.py"])
    except Exception as e:
        print_error(f"Failed to launch app: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

