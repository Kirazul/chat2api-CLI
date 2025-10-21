import warnings
import sys
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from utils.config import enable_gateway, api_prefix

warnings.filterwarnings("ignore")


log_config = uvicorn.config.LOGGING_CONFIG
default_format = "%(asctime)s | %(levelname)s | %(message)s"
access_format = r'%(asctime)s | %(levelname)s | %(client_addr)s: %(request_line)s %(status_code)s'
log_config["formatters"]["default"]["fmt"] = default_format
log_config["formatters"]["access"]["fmt"] = access_format

app = FastAPI(
    docs_url="/docs",    # Set Swagger UI documentation path
    redoc_url="/redoc",  # Set Redoc documentation path
    openapi_url="/openapi.json"  # Set OpenAPI JSON path
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle templates path for both development and PyInstaller bundle
def get_templates_directory():
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, 'templates')
    else:
        # Running in development
        return "templates"

templates = Jinja2Templates(directory=get_templates_directory())
security_scheme = HTTPBearer()

import api.chat2api

# Import sync API for CLI-to-Server communication
from api.sync import router as sync_router
app.include_router(sync_router)

# Add a simple health check endpoint
@app.get("/")
async def root():
    return {"message": "Chat2API Server is running", "status": "healthy", "version": "1.7.1-beta1"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Chat2API Server is running"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working", "api_prefix": api_prefix}

if enable_gateway:
    import gateway.share
    import gateway.login
    import gateway.chatgpt
    import gateway.gpts
    import gateway.admin
    import gateway.v1
    import gateway.backend


if __name__ == "__main__":
    import os
    
    # Get host and port from environment variables (Railway compatible)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5005"))
    
    # Production settings
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"Starting Chat2API server on {host}:{port}")
    print(f"Environment: {environment}")
    print(f"Gateway enabled: {enable_gateway}")
    print(f"API prefix: '{api_prefix}'")
    
    if environment == "production":
        uvicorn.run(
            "app:app", 
            host=host, 
            port=port,
            access_log=True,
            log_level="info"
        )
    else:
        uvicorn.run("app:app", host=host, port=port)
