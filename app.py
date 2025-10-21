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
    docs_url=f"/{api_prefix}/docs",    # Set Swagger UI documentation path
    redoc_url=f"/{api_prefix}/redoc",  # Set Redoc documentation path
    openapi_url=f"/{api_prefix}/openapi.json"  # Set OpenAPI JSON path
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

from app import app

import api.chat2api

if enable_gateway:
    import gateway.share
    import gateway.login
    import gateway.chatgpt
    import gateway.gpts
    import gateway.admin
    import gateway.v1
    import gateway.backend
else:
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
    async def reverse_proxy():
        raise HTTPException(status_code=404, detail="Gateway is disabled")


if __name__ == "__main__":
    import os
    
    # Get host and port from environment variables (Railway compatible)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5005"))
    
    # Production settings
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        uvicorn.run(
            "app:app", 
            host=host, 
            port=port,
            access_log=False,
            log_level="warning"
        )
    else:
        uvicorn.run("app:app", host=host, port=port)
