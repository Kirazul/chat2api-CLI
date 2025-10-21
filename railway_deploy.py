#!/usr/bin/env python3
"""
Railway Direct Deployment Script
This script will help you deploy Chat2API to Railway
"""

import os
import subprocess
import sys

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK: Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("ERROR: Railway CLI not found")
            return False
    except FileNotFoundError:
        print("ERROR: Railway CLI not installed")
        return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("Starting Railway deployment...")
    
    # Check if Railway CLI is available
    if not check_railway_cli():
        print("\nManual deployment required:")
        print("1. Go to https://railway.app")
        print("2. Sign up/Login with GitHub")
        print("3. Click 'New Project'")
        print("4. Select 'Deploy from GitHub repo'")
        print("5. Choose your 'APITESTPUSH' repository")
        print("6. Railway will automatically deploy!")
        return False
    
    # Try to deploy
    try:
        print("\nAttempting Railway deployment...")
        
        # Check if already logged in
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if "Unauthorized" in result.stderr:
            print("ERROR: Not logged in to Railway")
            print("Please run: railway login")
            return False
        
        # Deploy the project
        print("Deploying to Railway...")
        result = subprocess.run(['railway', 'up'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS: Deployment successful!")
            print(result.stdout)
            return True
        else:
            print("ERROR: Deployment failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"ERROR: Error during deployment: {e}")
        return False

def main():
    print("Chat2API Railway Deployment")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("ERROR: app.py not found. Please run this script from the Chat2API directory.")
        return
    
    if not os.path.exists('requirements.txt'):
        print("ERROR: requirements.txt not found. Please run this script from the Chat2API directory.")
        return
    
    print("OK: Chat2API files found")
    
    # Try to deploy
    success = deploy_to_railway()
    
    if not success:
        print("\n📋 Alternative: Manual Deployment")
        print("Your repository is ready at: https://github.com/Kirazul/APITESTPUSH.git")
        print("Just connect it to Railway through the web interface!")

if __name__ == "__main__":
    main()
