#!/usr/bin/env python3
"""
Server Launcher - Direct execution approach
"""
import os
import sys
import time
import subprocess

def main():
    print("=" * 60)
    print("🚀 Chat2API Server Starting...")
    print("=" * 60)
    print()
    
    try:
        print("📦 Loading dependencies...")
        
        # Force import python-multipart first with existing submodules
        import python_multipart
        import python_multipart.multipart
        print("✅ python-multipart loaded")
        
        # Import FastAPI and all its submodules
        import fastapi
        import fastapi.middleware
        import fastapi.middleware.cors
        import fastapi.security
        import fastapi.templating
        import fastapi.exceptions
        print("✅ FastAPI dependencies loaded")
        
        # Import other dependencies
        import uvicorn
        import jinja2
        import apscheduler
        import apscheduler.schedulers
        import apscheduler.schedulers.asyncio
        import chatgpt
        import chatgpt.authorization
        import chatgpt.chatFormat
        import chatgpt.chatLimit
        import chatgpt.ChatService
        import chatgpt.proofofWork
        import chatgpt.refreshToken
        import chatgpt.turnstile
        import chatgpt.wssClient
        import jwt
        
        # Import tiktoken and related modules
        import tiktoken
        import tiktoken_ext
        import tiktoken_ext.openai_public
        print("✅ Tiktoken dependencies loaded")
        
        print("✅ All dependencies loaded")
        
        print("✅ Dependencies loaded successfully")
        
        # Set up environment to ensure multipart is available
        import sys
        if 'multipart' not in sys.modules:
            sys.modules['multipart'] = python_multipart
        
        # Display version information (hardcoded)
        version = "1.7.1-beta1"
        print(f"📋 Version: {version}")
        
        print("🌐 Starting server on http://0.0.0.0:5005")
        print("📚 API Documentation: http://localhost:5005/docs")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 60)
        print()
        
        # Import and run the app directly
        from app import app
        uvicorn.run(app, host="0.0.0.0", port=5005, log_level="info")
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Server stopped by user")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("=" * 60)
    
    # Keep terminal open
    print("\nPress Enter to close this window...")
    input()

if __name__ == "__main__":
    main()
