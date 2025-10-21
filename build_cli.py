#!/usr/bin/env python3
"""
Build script for Chat2API CLI
Creates a standalone .exe file
"""
import os
import sys
import shutil
import subprocess

def build_exe():
    """Build the CLI as a standalone executable"""
    
    print("=" * 60)
    print("Building Chat2API CLI Executable")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    print()
    print("Building executable...")
    print()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--name=Chat2API-CLI",          # Output name
        "--icon=NONE",                  # No icon
        "--clean",                      # Clean cache
        "--noconfirm",                  # Overwrite without asking
        "--add-data=tokens.json;.",     # Include tokens.json
        "--add-data=config.json;.",     # Include config.json
        "--hidden-import=rich",
        "--hidden-import=prompt_toolkit",
        "--hidden-import=httpx",
        "chat.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print()
        print("Executable location: dist/Chat2API-CLI.exe")
        print()
        
        # Show file size
        exe_path = "dist/Chat2API-CLI.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"File size: {size_mb:.2f} MB")
        
        print()
        print("You can now run: dist\\Chat2API-CLI.exe")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ Build failed!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
