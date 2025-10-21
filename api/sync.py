"""
Sync API for CLI to Server communication
Allows CLI to sync tokens and API keys to the Railway server
"""
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

# File paths
TOKENS_FILE = Path("tokens.json")
APIKEYS_FILE = Path("apikeys.json")
DATA_TOKEN_FILE = Path("data/token.txt")


class TokensSyncRequest(BaseModel):
    tokens: Dict[str, str]
    sync_type: str


class APIKeysSyncRequest(BaseModel):
    apikeys: Dict[str, dict]
    sync_type: str


@router.post("/admin/sync/tokens")
async def sync_tokens(request: TokensSyncRequest):
    """Sync tokens from CLI to server"""
    try:
        # Load existing tokens
        existing_tokens = {}
        if TOKENS_FILE.exists():
            with open(TOKENS_FILE, 'r') as f:
                existing_tokens = json.load(f)
        
        # Merge with new tokens
        existing_tokens.update(request.tokens)
        
        # Save to tokens.json
        with open(TOKENS_FILE, 'w') as f:
            json.dump(existing_tokens, f, indent=2)
        
        # Also append to data/token.txt
        DATA_TOKEN_FILE.parent.mkdir(exist_ok=True)
        with open(DATA_TOKEN_FILE, 'a') as f:
            for token in request.tokens.values():
                f.write(f"{token}\n")
        
        return {
            "status": "success",
            "message": "Tokens synced successfully",
            "tokens_count": len(existing_tokens)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/admin/sync/apikeys")
async def sync_apikeys(request: APIKeysSyncRequest):
    """Sync API keys from CLI to server"""
    try:
        # Load existing API keys
        existing_apikeys = {}
        if APIKEYS_FILE.exists():
            with open(APIKEYS_FILE, 'r') as f:
                existing_apikeys = json.load(f)
        
        # Merge with new API keys
        existing_apikeys.update(request.apikeys)
        
        # Save to apikeys.json
        with open(APIKEYS_FILE, 'w') as f:
            json.dump(existing_apikeys, f, indent=2)
        
        return {
            "status": "success",
            "message": "API keys synced successfully",
            "apikeys_count": len(existing_apikeys)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get("/admin/sync/status")
async def sync_status():
    """Get sync status and file information"""
    try:
        tokens_count = 0
        apikeys_count = 0
        
        if TOKENS_FILE.exists():
            with open(TOKENS_FILE, 'r') as f:
                tokens = json.load(f)
                tokens_count = len(tokens) if isinstance(tokens, dict) else 0
        
        if APIKEYS_FILE.exists():
            with open(APIKEYS_FILE, 'r') as f:
                apikeys = json.load(f)
                apikeys_count = len(apikeys) if isinstance(apikeys, dict) else 0
        
        return {
            "status": "online",
            "tokens_count": tokens_count,
            "apikeys_count": apikeys_count,
            "files": {
                "tokens_json": TOKENS_FILE.exists(),
                "apikeys_json": APIKEYS_FILE.exists(),
                "data_token_txt": DATA_TOKEN_FILE.exists()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
