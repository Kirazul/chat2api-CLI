"""
API Key Mapping Middleware
Intercepts all requests and maps sk-xxx API keys to ChatGPT tokens
"""
import json
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
from utils.Logger import logger


class APIKeyMapperMiddleware(BaseHTTPMiddleware):
    """Middleware to map API keys to ChatGPT tokens"""
    
    def __init__(self, app):
        super().__init__(app)
        self.apikeys_file = Path("apikeys.json")
        self.tokens_file = Path("tokens.json")
    
    def load_mappings(self):
        """Load API key and token mappings"""
        try:
            apikeys = {}
            tokens = {}
            
            if self.apikeys_file.exists():
                with open(self.apikeys_file, 'r') as f:
                    apikeys = json.load(f)
            
            if self.tokens_file.exists():
                with open(self.tokens_file, 'r') as f:
                    tokens = json.load(f)
            
            return apikeys, tokens
        except Exception as e:
            logger.error(f"Error loading mappings: {e}")
            return {}, {}
    
    def map_apikey_to_token(self, api_key: str) -> str:
        """Map sk-xxx API key to ChatGPT token"""
        if not api_key or not api_key.startswith("sk-"):
            return api_key
        
        try:
            apikeys, tokens = self.load_mappings()
            
            logger.info(f"🔑 Checking API key: {api_key[:15]}...")
            logger.info(f"📁 Loaded {len(apikeys)} API keys and {len(tokens)} tokens")
            
            # Find the API key
            for name, data in apikeys.items():
                if isinstance(data, dict) and data.get('key') == api_key:
                    token_name = data.get('token_name', 'auto')
                    
                    if token_name in tokens:
                        logger.info(f"✅ Mapped API key '{name}' → token '{token_name}'")
                        return tokens[token_name]
                    elif token_name == 'auto' and tokens:
                        logger.info(f"✅ Mapped API key '{name}' → first available token")
                        return list(tokens.values())[0]
            
            logger.warning(f"⚠️ API key not found in mapping: {api_key[:15]}...")
            return api_key
            
        except Exception as e:
            logger.error(f"❌ Error mapping API key: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return api_key
    
    async def dispatch(self, request, call_next):
        """Intercept request and map API key if present"""
        
        # Check for Authorization header
        auth_header = request.headers.get("authorization", "")
        
        if auth_header.startswith("Bearer "):
            original_token = auth_header[7:]  # Remove "Bearer "
            
            if original_token.startswith("sk-"):
                logger.info(f"🔍 Detected API key in request")
                
                # Map the API key to ChatGPT token
                mapped_token = self.map_apikey_to_token(original_token)
                
                if mapped_token != original_token:
                    logger.info(f"🔄 Replacing API key with ChatGPT token")
                    
                    # Update the authorization header in the request scope
                    headers = MutableHeaders(request.scope["headers"])
                    headers["authorization"] = f"Bearer {mapped_token}"
                    
                    # Update the scope
                    request.scope["headers"] = headers.raw
        
        # Continue with the request
        response = await call_next(request)
        return response
