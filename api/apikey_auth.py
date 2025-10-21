"""
API Key Authentication Middleware
Maps generated sk-xxx API keys to ChatGPT access tokens
"""
import json
import sys
from pathlib import Path
from typing import Optional

# Configuration - Use exe-relative paths when bundled
def get_config_dir():
    """Get the appropriate config directory based on execution context"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle - use exe directory
        return Path(sys.executable).parent
    else:
        # Running as script - use home directory
        return Path.home() / ".chat2api_cli"

CONFIG_DIR = get_config_dir()
APIKEYS_FILE = CONFIG_DIR / "apikeys.json"
TOKENS_FILE = CONFIG_DIR / "tokens.json"


class APIKeyAuth:
    """Handles API key authentication and mapping"""

    def __init__(self):
        self.apikeys = self.load_apikeys()
        self.tokens = self.load_tokens()

    def load_apikeys(self) -> dict:
        """Load generated API keys"""
        if APIKEYS_FILE.exists():
            try:
                with open(APIKEYS_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, Exception):
                pass
        return {}

    def load_tokens(self) -> dict:
        """Load ChatGPT tokens"""
        if TOKENS_FILE.exists():
            try:
                with open(TOKENS_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, Exception):
                pass
        return {}

    def validate_and_map_apikey(self, api_key: str) -> Optional[str]:
        """
        Validate an API key and return the corresponding ChatGPT token

        Args:
            api_key: The API key to validate (sk-xxx format)

        Returns:
            The ChatGPT access token if valid, None otherwise
        """
        # Reload files in case they were updated
        self.apikeys = self.load_apikeys()
        self.tokens = self.load_tokens()

        # If it doesn't start with sk-, it's probably a direct ChatGPT token
        if not api_key.startswith("sk-"):
            return api_key

        # Search for the API key in our generated keys
        for name, data in self.apikeys.items():
            if data.get('key') == api_key:
                # Found the API key, now get the associated token
                token_name = data.get('token_name', 'auto')

                if token_name in self.tokens:
                    # Return the ChatGPT token
                    return self.tokens[token_name]
                elif token_name == 'auto' and self.tokens:
                    # Return first available token
                    return list(self.tokens.values())[0]

        # API key not found, return original (let server handle it)
        return api_key


# Global instance
apikey_auth = APIKeyAuth()
