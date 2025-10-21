#!/usr/bin/env python3
"""
Railway-optimized startup script for Chat2API
"""
import os
import sys
from dotenv import load_dotenv

def load_environment():
    """Load appropriate environment file based on ENVIRONMENT variable"""
    environment = os.getenv('ENVIRONMENT', 'development')
    
    if environment == 'production':
        # Try to load production env file if it exists
        if os.path.exists('.env.production'):
            load_dotenv('.env.production')
            print("Loaded .env.production")
    else:
        # Load default .env for development
        if os.path.exists('.env'):
            load_dotenv('.env')
            print("Loaded .env")
    
    # Always load any additional environment variables from Railway
    print(f"Environment: {environment}")
    print(f"Port: {os.getenv('PORT', 'Not set')}")
    print(f"Host: {os.getenv('HOST', '0.0.0.0')}")

if __name__ == "__main__":
    load_environment()
    
    # Import and run the main app
    from app import app
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5005"))
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"Starting Chat2API server on {host}:{port}")
    print(f"Environment: {environment}")
    
    # Run with appropriate settings for production
    if environment == "production":
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            access_log=True,
            log_level="info",
            workers=1  # Railway works better with single worker
        )
    else:
        uvicorn.run(app, host=host, port=port, reload=True)