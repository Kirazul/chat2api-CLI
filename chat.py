#!/usr/bin/env python3
"""
Chat2API CLI - Professional, modern interface
"""
import sys
import json
import asyncio
import os
import secrets
import string
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.columns import Columns
from rich.rule import Rule
from rich.live import Live
from rich.status import Status
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML

# Retro color scheme
class Theme:
    """Retro pixelated theme for the CLI"""
    # Primary colors
    PRIMARY = "#8b5cf6"      # Bright Purple
    SECONDARY = "#10b981"    # Bright Green
    SUCCESS = "#10b981"      # Bright Green
    WARNING = "#f59e0b"      # Orange
    ERROR = "#ef4444"        # Red
    INFO = "#06b6d4"         # Cyan
    
    # Neutral colors
    BACKGROUND = "#000000"   # Black
    SURFACE = "#1a1a1a"      # Dark gray
    BORDER = "#8b5cf6"       # Purple border
    TEXT_PRIMARY = "#ffffff" # White
    TEXT_SECONDARY = "#e5e7eb" # Light gray
    TEXT_MUTED = "#9ca3af"   # Muted gray
    
    # Accent colors
    ACCENT_BLUE = "#10b981"  # Green
    ACCENT_PURPLE = "#8b5cf6" # Bright Purple
    ACCENT_GREEN = "#10b981"  # Bright Green
    ACCENT_YELLOW = "#f59e0b"
    ACCENT_RED = "#ef4444"
    ACCENT_CYAN = "#06b6d4"

# Initialize console with professional theme
from rich.theme import Theme as RichTheme

rich_theme = RichTheme({
    "info": Theme.INFO,
    "warning": Theme.WARNING,
    "error": Theme.ERROR,
    "success": Theme.SUCCESS,
    "primary": Theme.PRIMARY,
    "secondary": Theme.SECONDARY,
})

console = Console(
    color_system="truecolor",
    theme=rich_theme
)

# Configuration - Use exe-relative paths when bundled
def get_data_dir():
    """Get the appropriate data directory based on execution context"""
    # First check if config.json exists in current directory
    current_dir = Path.cwd()
    if (current_dir / "config.json").exists():
        return current_dir
    
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle - use exe directory
        return Path(sys.executable).parent
    else:
        # Running as script - use home directory
        return Path.home() / ".chat2api_cli"

CONFIG_DIR = get_data_dir()
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKENS_FILE = CONFIG_DIR / "tokens.json"
APIKEYS_FILE = CONFIG_DIR / "apikeys.json"
DATA_DIR = CONFIG_DIR / "data"

class Config:
    """CLI Configuration Manager"""
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.tokens_file = TOKENS_FILE
        self.apikeys_file = APIKEYS_FILE
        self.config = self.load_config()
        self.tokens = self.load_tokens()
        self.apikeys = self.load_apikeys()

    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "api_endpoint": "http://localhost:5005",
            "default_model": "gpt-3.5-turbo",
            "active_token": None
        }

    def load_tokens(self) -> dict:
        """Load labeled tokens"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                    # Ensure we return a dictionary, not a list
                    if isinstance(data, dict):
                        return data
                    else:
                        # If it's a list or other type, return empty dict
                        return {}
            except (json.JSONDecodeError, Exception):
                # If file is corrupted or invalid, return empty dict
                return {}
        return {}

    def save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def save_tokens(self):
        """Save tokens to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2)

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.save_config()

    def add_token(self, name: str, token: str):
        """Add a labeled token"""
        # Ensure tokens is a dictionary
        if not isinstance(self.tokens, dict):
            self.tokens = {}
        
        self.tokens[name] = token
        self.save_tokens()
        # Also save to data/token.txt for server compatibility
        DATA_DIR.mkdir(exist_ok=True)
        token_file = DATA_DIR / "token.txt"
        with open(token_file, 'a') as f:
            f.write(f"{token}\n")

    def remove_token(self, name: str):
        """Remove a labeled token"""
        # Ensure tokens is a dictionary
        if not isinstance(self.tokens, dict):
            self.tokens = {}
            
        if name in self.tokens:
            del self.tokens[name]
            self.save_tokens()
            return True
        return False

    def use_token(self, name: str):
        """Set active token by name"""
        # Ensure tokens is a dictionary
        if not isinstance(self.tokens, dict):
            self.tokens = {}
            
        if name in self.tokens:
            self.config['active_token'] = name
            self.save_config()
            return True
        return False

    def get_active_token(self):
        """Get the currently active token"""
        # Ensure tokens is a dictionary
        if not isinstance(self.tokens, dict):
            self.tokens = {}

        active = self.config.get('active_token')
        if active and active in self.tokens:
            return self.tokens[active]
        # Fallback to first token
        if self.tokens:
            return list(self.tokens.values())[0]
        return None

    def load_apikeys(self) -> dict:
        """Load generated API keys"""
        if self.apikeys_file.exists():
            try:
                with open(self.apikeys_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    else:
                        return {}
            except (json.JSONDecodeError, Exception):
                return {}
        return {}

    def save_apikeys(self):
        """Save API keys to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.apikeys_file, 'w') as f:
            json.dump(self.apikeys, f, indent=2)

    def generate_apikey(self, name: str) -> str:
        """Generate a new OpenAI-compatible API key"""
        # Ensure apikeys is a dictionary
        if not isinstance(self.apikeys, dict):
            self.apikeys = {}

        # Generate a secure random API key in OpenAI format (sk-...)
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(48))
        api_key = f"sk-{random_part}"

        # Store with metadata
        self.apikeys[name] = {
            "key": api_key,
            "created": __import__('datetime').datetime.now().isoformat(),
            "token_name": self.config.get('active_token', 'auto')
        }
        self.save_apikeys()

        return api_key

    def remove_apikey(self, name: str):
        """Remove an API key"""
        if not isinstance(self.apikeys, dict):
            self.apikeys = {}

        if name in self.apikeys:
            del self.apikeys[name]
            self.save_apikeys()
            return True
        return False

config = Config()

# Command definitions with descriptions
COMMANDS = {
    "/help": "Show all available commands",
    "/status": "Display current settings and connection status",
    "/models": "List all available AI models",
    "/use": "Switch to a different model (e.g., /use gpt-4)",
    "/stream": "Toggle streaming mode on/off",
    "/clear": "Clear conversation history",
    "/reset": "Reset all settings, tokens, and API keys to defaults",
    "/token": "Manage access tokens (add/list/use/remove)",
    "/token add": "Add a new access token",
    "/token list": "List all saved tokens",
    "/token use": "Switch to a specific token",
    "/token remove": "Remove a token",
    "/apikey": "Generate OpenAI-compatible API keys for external programs",
    "/apikey generate": "Generate a new API key",
    "/apikey list": "List all generated API keys",
    "/apikey test": "Test a specific API key",
    "/apikey remove": "Remove an API key",
    "/endpoint": "Switch API endpoint (e.g., /endpoint https://your-server.com)",
    "/web": "Open ChatGPT web interface in default browser",
    "/exit": "Exit the CLI",
}

class CommandCompleter(Completer):
    """Custom completer for slash commands with descriptions"""

    def get_completions(self, document, complete_event):
        text = document.text

        # Only show completions if text starts with /
        if not text.startswith('/'):
            return

        # Get matching commands - iterate over items properly
        for cmd, desc in sorted(COMMANDS.items()):
            if cmd.lower().startswith(text.lower()):
                # Simple white text for better readability
                display_meta = HTML(f'<ansibrightwhite>{desc}</ansibrightwhite>')
                yield Completion(
                    cmd,
                    start_position=-len(text),
                    display_meta=display_meta
                )

def get_user_input():
    """Get user input with retro styling and command completion"""
    try:
        completer = CommandCompleter()
        result = pt_prompt(
            HTML('<ansibrightmagenta>></ansibrightmagenta> '),
            completer=completer,
            complete_while_typing=True,
            enable_history_search=True
        )
        return result
    except (KeyboardInterrupt, EOFError):
        raise

def show_banner():
    """Show retro pixelated banner"""
    # Clear screen for better presentation
    os.system('cls' if os.name == 'nt' else 'clear')

    # Create gradient purple effect for CHAT2API
    console.print()
    
    # Top border with gradient
    console.print(Align.center("╔══════════════════════════════════════════════════════════════════════════════╗"), style="#a855f7")
    console.print(Align.center("║                                                                              ║"), style="#9333ea")
    
    # CHAT2API with gradient effect (using different purple shades)
    chat2api_lines = [
        "    ██████╗██╗  ██╗ █████╗ ████████╗██████╗  █████╗ ██████╗ ██╗               ",
        "   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝╚════██╗██╔══██╗██╔══██╗██║               ",
        "   ██║     ███████║███████║   ██║    █████╔╝███████║██████╔╝██║               ",
        "   ██║     ██╔══██║██╔══██║   ██║   ██╔═══╝ ██╔══██║██╔═══╝ ██║               ",
        "   ╚██████╗██║  ██║██║  ██║   ██║   ███████╗██║  ██║██║     ██║               ",
        "    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝               "
    ]
    
    # Apply gradient effect to each line
    gradient_colors = ["#a855f7", "#9333ea", "#7c3aed", "#6d28d9", "#5b21b6", "#4c1d95"]
    
    for i, line in enumerate(chat2api_lines):
        color = gradient_colors[i % len(gradient_colors)]
        console.print(Align.center(f"║{line}║"), style=color)
    
    console.print(Align.center("║                                                                              ║"), style="#7c3aed")
    console.print(Align.center("╚══════════════════════════════════════════════════════════════════════════════╝"), style="#6d28d9")
    console.print()
    console.print(Align.center("[bold white]OpenAI-Compatible API Gateway[/bold white]"))
    console.print(Align.center("[dim]Transform ChatGPT into powerful APIs[/dim]"))
    console.print()

def show_help():
    """Show available commands with professional formatting"""
    console.print()

    # Create a comprehensive help panel
    help_content = """
[bold #10b981]Chat & Navigation[/bold #10b981]
  [bold #a855f7]/help[/bold #a855f7]                    Show this command reference
  [bold #a855f7]/status[/bold #a855f7]                  Display system status and configuration
  [bold #a855f7]/clear[/bold #a855f7]                   Clear conversation history
  [bold #a855f7]/web[/bold #a855f7]                     Open ChatGPT web interface in browser
  [bold #a855f7]/exit[/bold #a855f7]                    Exit the application

[bold #8b5cf6]Model Management[/bold #8b5cf6]
  [bold #a855f7]/models[/bold #a855f7]                  List available AI models
  [bold #a855f7]/use <model>[/bold #a855f7]             Switch to a different model
  [bold #a855f7]/stream[/bold #a855f7]                  Toggle streaming mode

[bold #10b981]Authentication[/bold #10b981]
  [bold #a855f7]/token add[/bold #a855f7]               Add a new access token
  [bold #a855f7]/token list[/bold #a855f7]              List all saved tokens
  [bold #a855f7]/token use <name>[/bold #a855f7]        Switch to a specific token
  [bold #a855f7]/token remove <name>[/bold #a855f7]     Remove a token

[bold #f59e0b]API Integration[/bold #f59e0b]
  [bold #a855f7]/endpoint <url>[/bold #a855f7]          Switch API endpoint (e.g., /endpoint https://your-server.com)
  [bold #a855f7]/apikey generate[/bold #a855f7]         Generate OpenAI-compatible API key
  [bold #a855f7]/apikey list[/bold #a855f7]             List all generated API keys
  [bold #a855f7]/apikey test <name>[/bold #a855f7]      Test a specific API key
  [bold #a855f7]/apikey remove <name>[/bold #a855f7]    Remove an API key

[bold #ef4444]System[/bold #ef4444]
  [bold #a855f7]/reset[/bold #a855f7]                   Reset all settings, tokens, and API keys

[dim][bold]Quick Start:[/bold] Type normally to chat with AI. Commands start with /[/dim]
[dim][bold]Examples:[/bold] /use gpt-4, /token add, /apikey generate, /web[/dim]
    """
    
    help_panel = Panel(
        help_content,
        title="[bold white]Command Reference[/bold white]",
        subtitle="[dim]Professional Chat2API CLI[/dim]",
        border_style="#a855f7",
        padding=(1, 2),
        title_align="left"
    )
    
    console.print(Align.center(help_panel))
    console.print()

def open_web_interface():
    """Open the ChatGPT web interface in the default browser"""
    console.print()
    
    # Get the web URL
    endpoint = config.get("api_endpoint", "http://localhost:5005")
    web_url = f"{endpoint}/"
    
    # Open the web interface directly
    try:
        webbrowser.open(web_url)
        
        success_panel = Panel(
            f"[bold green]✓ Opening ChatGPT web interface![/bold green]\n\n"
            f"[bold]URL:[/bold] [underline]{web_url}[/underline]\n"
            f"[dim]The web interface should open in your default browser.[/dim]\n"
            f"[dim]If it doesn't open automatically, copy the URL above.[/dim]",
            title="[bold]Web Interface[/bold]",
            border_style=Theme.SUCCESS,
            padding=(1, 2)
        )
        console.print(success_panel)
        console.print()
        
    except Exception as e:
        error_panel = Panel(
            f"[bold red]✗ Failed to open browser![/bold red]\n\n"
            f"[dim]Error: {str(e)}[/dim]\n"
            f"[bold]Please manually open:[/bold] [underline]{web_url}[/underline]",
            title="[bold]Browser Error[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()

def switch_endpoint(new_endpoint):
    """Switch the API endpoint with validation"""
    console.print()
    
    # Validate URL format
    if not new_endpoint.startswith(('http://', 'https://')):
        error_panel = Panel(
            "[bold red]✗ Invalid endpoint format![/bold red]\n\n"
            "[bold]Endpoint must start with:[/bold]\n"
            "• [bold #a855f7]http://[/bold #a855f7] (for local servers)\n"
            "• [bold #a855f7]https://[/bold #a855f7] (for secure servers)\n\n"
            "[bold]Examples:[/bold]\n"
            "• [#a855f7]http://localhost:5005[/#a855f7]\n"
            "• [#a855f7]https://your-server.com[/#a855f7]\n"
            "• [#a855f7]https://api.example.com:8080[/#a855f7]",
            title="[bold]Invalid Endpoint[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return False
    
    # Test the new endpoint
    console.print(f"[dim]Testing endpoint: {new_endpoint}...[/dim]")
    
    try:
        import requests
        # Test with a simple request to /v1/models
        test_url = f"{new_endpoint}/v1/models"
        response = requests.get(test_url, timeout=5)
        
        if response.status_code == 200:
            # Endpoint is working
            config.set("api_endpoint", new_endpoint)
            
            success_panel = Panel(
                f"[bold green]✓ Endpoint switched successfully![/bold green]\n\n"
                f"[bold]New Endpoint:[/bold] [yellow]{new_endpoint}[/yellow]\n"
                f"[bold]Status:[/bold] [green]✓ Online and responding[/green]\n"
                f"[bold]Response Time:[/bold] [dim]{response.elapsed.total_seconds():.2f}s[/dim]\n\n"
                f"[dim]All future API requests will use this endpoint.[/dim]",
                title="[bold]Endpoint Changed[/bold]",
                border_style=Theme.SUCCESS,
                padding=(1, 2)
            )
            console.print(success_panel)
            console.print()
            return True
        else:
            # Endpoint responded but with error
            error_panel = Panel(
                f"[bold yellow]⚠ Endpoint responded but with error![/bold yellow]\n\n"
                f"[bold]Endpoint:[/bold] [yellow]{new_endpoint}[/yellow]\n"
                f"[bold]Status Code:[/bold] [yellow]{response.status_code}[/yellow]\n"
                f"[bold]Response:[/bold] [dim]{response.text[:100]}...[/dim]\n\n"
                f"[dim]The endpoint is reachable but may not be a valid Chat2API server.[/dim]",
                title="[bold]Endpoint Error[/bold]",
                border_style=Theme.WARNING,
                padding=(1, 2)
            )
            console.print(error_panel)
            console.print()
            return False
            
    except requests.exceptions.Timeout:
        error_panel = Panel(
            f"[bold red]✗ Endpoint timeout![/bold red]\n\n"
            f"[bold]Endpoint:[/bold] [yellow]{new_endpoint}[/yellow]\n"
            f"[bold]Error:[/bold] [red]Connection timeout (5s)[/red]\n\n"
            f"[dim]The endpoint is not responding or is too slow.[/dim]\n"
            f"[dim]Please check if the server is running and accessible.[/dim]",
            title="[bold]Connection Timeout[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return False
        
    except requests.exceptions.ConnectionError:
        error_panel = Panel(
            f"[bold red]✗ Connection failed![/bold red]\n\n"
            f"[bold]Endpoint:[/bold] [yellow]{new_endpoint}[/yellow]\n"
            f"[bold]Error:[/bold] [red]Connection refused[/red]\n\n"
            f"[dim]The endpoint is not reachable. Please check:[/dim]\n"
            f"[dim]• Server is running[/dim]\n"
            f"[dim]• URL is correct[/dim]\n"
            f"[dim]• Network connectivity[/dim]\n"
            f"[dim]• Firewall settings[/dim]",
            title="[bold]Connection Failed[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return False
        
    except Exception as e:
        error_panel = Panel(
            f"[bold red]✗ Unexpected error![/bold red]\n\n"
            f"[bold]Endpoint:[/bold] [yellow]{new_endpoint}[/yellow]\n"
            f"[bold]Error:[/bold] [red]{str(e)}[/red]\n\n"
            f"[dim]An unexpected error occurred while testing the endpoint.[/dim]",
            title="[bold]Test Error[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return False

def show_status(current_model, current_stream, conversation_history):
    """Show current status with retro design"""
    console.print()

    # Connection Status
    endpoint = config.get("api_endpoint", "http://localhost:5005")
    try:
        import requests
        response = requests.get(f"{endpoint}/v1/models", timeout=2)
        status_icon = "●"
        status_text = "ONLINE"
        status_color = Theme.SUCCESS
    except:
        status_icon = "●"
        status_text = "OFFLINE"
        status_color = Theme.ERROR

    # Simple status display with gradient borders
    console.print(Align.center("╔══════════════════════════════════════════════════════════════════════════════╗"), style="#a855f7")
    console.print(Align.center("║                                Server Status                                 ║"), style="#9333ea")
    console.print(Align.center("╚══════════════════════════════════════════════════════════════════════════════╝"), style="#7c3aed")
    console.print()
    
    console.print(Align.center(f"● Status     [{status_color}]{status_text}[/{status_color}]"))
    console.print(Align.center(f"Endpoint     [underline]{endpoint}[/underline]"))
    console.print(Align.center(f"Model        [{Theme.ACCENT_PURPLE}]{current_model}[/{Theme.ACCENT_PURPLE}]"))
    console.print(Align.center(f"Streaming    [{Theme.SUCCESS if current_stream else Theme.WARNING}]{'Enabled' if current_stream else 'Disabled'}[/{Theme.SUCCESS if current_stream else Theme.WARNING}]"))
    console.print()
    
    # Quick help
    console.print(Align.center(f"Type [{Theme.ACCENT_PURPLE}]/help[/{Theme.ACCENT_PURPLE}] for commands"))
    console.print()

def list_models():
    """Show available models with professional formatting"""
    models = [
        # GPT-3.5 Models
        ("gpt-3.5-turbo", "Fast & Efficient", "Best for quick questions and general use", Theme.ACCENT_GREEN),
        # GPT-4 Models
        ("gpt-4", "Advanced Reasoning", "Best for complex tasks and analysis", Theme.ACCENT_BLUE),
        ("gpt-4-mobile", "Mobile Optimized", "Optimized for mobile devices", Theme.ACCENT_BLUE),
        ("gpt-4-gizmo", "Gizmo Integration", "GPT-4 with gizmo capabilities", Theme.ACCENT_BLUE),
        # GPT-4o Models
        ("gpt-4o", "Latest Generation", "Most advanced capabilities", Theme.ACCENT_YELLOW),
        ("gpt-4o-mini", "Efficient GPT-4o", "Faster, cheaper GPT-4o variant", Theme.ACCENT_YELLOW),
        ("gpt-4o-canmore", "Canmore Model", "Specialized GPT-4o variant", Theme.ACCENT_CYAN),
        ("gpt-4.5o", "Enhanced GPT-4o", "Advanced GPT-4o variant", Theme.ACCENT_CYAN),
        # GPT-5
        ("gpt-5", "Next Generation", "Future AI capabilities", Theme.ACCENT_CYAN),
        # O1 Models
        ("o1-preview", "Reasoning Engine", "Advanced reasoning and problem solving", Theme.ACCENT_RED),
        ("o1-mini", "Lightweight Reasoning", "Efficient reasoning capabilities", Theme.ACCENT_RED),
        ("o1", "General Reasoning", "General purpose reasoning model", Theme.ACCENT_RED),
        # Auto Selection
        ("auto", "Auto Selection", "Automatically select best available model", Theme.ACCENT_PURPLE)
    ]

    console.print()
    
    # Create models table
    models_table = Table(
        title="[bold white]Available AI Models[/bold white]",
        show_header=True,
        header_style="bold white",
        box=box.ROUNDED,
        border_style="#a855f7",
        title_style="bold white"
    )
    
    models_table.add_column("Model", style="bold", width=20)
    models_table.add_column("Description", style="default", width=25)
    models_table.add_column("Best For", style="dim", width=30)
    models_table.add_column("Status", style="default", width=15)

    for model, desc, use_case, color in models:
        models_table.add_row(
            f"[{color}]{model}[/{color}]",
            desc,
            use_case,
            f"[{Theme.SUCCESS}]Available[/{Theme.SUCCESS}]"
        )

    console.print(Align.left(models_table))
    console.print()
    
    # Usage instructions
    usage_panel = Panel(
        "[bold]Usage:[/bold] [#a855f7]/use <model-name>[/#a855f7]\n"
        "[bold]Example:[/bold] [#a855f7]/use gpt-4[/#a855f7]\n"
        "[dim]Models are automatically selected based on your needs[/dim]",
        title="[bold]Quick Switch[/bold]",
        border_style="#9333ea",
        padding=(1, 2)
    )
    console.print(Align.left(usage_panel))
    console.print()

def list_tokens():
    """List all saved tokens with professional formatting"""
    # Ensure tokens is a dictionary
    if not isinstance(config.tokens, dict):
        config.tokens = {}

    if not config.tokens:
        console.print()
        empty_panel = Panel(
            "[bold yellow]⚠ No access tokens configured[/bold yellow]\n\n"
            "[dim]Add your first token with:[/dim] [bold #a855f7]/token add[/bold #a855f7]\n"
            "[dim]Get tokens from:[/dim] [bold #a855f7]https://chatgpt.com[/bold #a855f7]",
            title="[bold]No Tokens Found[/bold]",
            border_style=Theme.WARNING,
            padding=(1, 2)
        )
        console.print(empty_panel)
        console.print()
        return

    active = config.get('active_token')

    console.print()
    
    # Create tokens table
    tokens_table = Table(
        title="[bold white]Access Tokens[/bold white]",
        show_header=True,
        header_style="bold white",
        box=box.ROUNDED,
        border_style="#a855f7",
        title_style="bold white"
    )
    
    tokens_table.add_column("Name", style="bold", width=20)
    tokens_table.add_column("Type", style="default", width=15)
    tokens_table.add_column("Preview", style="dim", width=25)
    tokens_table.add_column("Status", style="default", width=15)

    for name, token in config.tokens.items():
        # Determine token type and color
        if token.startswith("eyJhbGciOi"):
            token_type = "JWT"
            type_color = Theme.ACCENT_BLUE
        elif token.startswith("fk-"):
            token_type = "FakeOpen"
            type_color = Theme.ACCENT_PURPLE
        elif len(token) == 45:
            token_type = "Refresh"
            type_color = Theme.ACCENT_GREEN
        else:
            token_type = "Unknown"
            type_color = Theme.ACCENT_YELLOW

        # Show preview
        preview = f"{token[:12]}...{token[-6:]}" if len(token) > 25 else token

        # Active indicator
        if name == active:
            status = f"[{Theme.SUCCESS}]Active[/{Theme.SUCCESS}]"
            name_style = f"[{Theme.SUCCESS}]{name}[/{Theme.SUCCESS}]"
        else:
            status = "[dim]Inactive[/dim]"
            name_style = name

        tokens_table.add_row(
            name_style,
            f"[{type_color}]{token_type}[/{type_color}]",
            preview,
            status
        )

    console.print(Align.center(tokens_table))
    console.print()
    
    # Management instructions
    if active:
        active_info = f"[bold green]Active Token:[/bold green] [bold]{active}[/bold]"
    else:
        active_info = "[bold yellow]Auto-selection enabled[/bold yellow]"
    
    management_panel = Panel(
        f"{active_info}\n\n"
        "[bold]Management Commands:[/bold]\n"
        "• [#a855f7]/token add[/#a855f7] - Add new token\n"
        "• [#a855f7]/token use <name>[/#a855f7] - Switch token\n"
        "• [#a855f7]/token remove <name>[/#a855f7] - Remove token",
        title="[bold]Token Management[/bold]",
        border_style="#9333ea",
        padding=(1, 2)
    )
    console.print(Align.center(management_panel))
    console.print()

def add_token_interactive():
    """Add a token with professional interactive prompts"""
    console.print()
    
    # Welcome panel
    welcome_panel = Panel(
        "[bold white]Add New Access Token[/bold white]\n\n"
        "[dim]This will securely store your ChatGPT access token for use with the CLI.[/dim]",
        title="[bold]Token Setup[/bold]",
        border_style="#a855f7",
        padding=(1, 2)
    )
    console.print(welcome_panel)
    console.print()

    # Ask for name
    name = Prompt.ask(
        "[bold #a855f7]Token Name[/bold #a855f7]",
        default="default",
        show_default=True
    )

    if not name:
        console.print(f"[{Theme.ERROR}]✗ Name cannot be empty![/{Theme.ERROR}]")
        return

    # Ensure tokens is a dictionary
    if not isinstance(config.tokens, dict):
        config.tokens = {}

    if name in config.tokens:
        if not Confirm.ask(f"[{Theme.WARNING}]⚠ Token '{name}' already exists. Replace it?[/{Theme.WARNING}]"):
            console.print("[dim]✗ Operation cancelled[/dim]")
            return

    # Instructions panel
    instructions_panel = Panel(
        "[bold]How to get your access token:[/bold]\n\n"
        "1. You can find it in [bold #a855f7]@https://chatgpt.com/api/auth/session[/bold #a855f7]\n"
        "2. Copy the returned token value\n\n"
        "[dim]The token should start with 'eyJ' or be a long string of characters.[/dim]",
        title="[bold]Instructions[/bold]",
        border_style="#9333ea",
        padding=(1, 2)
    )
    console.print(instructions_panel)
    console.print()

    # Ask for token
    token = Prompt.ask(
        "[bold #a855f7]Access Token[/bold #a855f7]"
    )

    if not token or len(token) < 20:
        console.print(f"[{Theme.ERROR}]✗ Invalid token! Token must be at least 20 characters.[/{Theme.ERROR}]")
        return

    # Save token
    config.add_token(name, token)

    # Success panel
    success_panel = Panel(
        f"[bold green]✓ Token '{name}' added successfully![/bold green]\n\n"
        f"[dim]Token preview:[/dim] [bold]{token[:12]}...{token[-6:]}[/bold]",
        title="[bold]Success[/bold]",
        border_style=Theme.SUCCESS,
        padding=(1, 2)
    )
    console.print(success_panel)
    console.print()

    # Ask if they want to use it now
    if Confirm.ask(f"[{Theme.ACCENT_BLUE}]🚀 Use this token now?[/{Theme.ACCENT_BLUE}]", default=True):
        config.use_token(name)
        console.print(f"[{Theme.SUCCESS}]✓ Now using token '{name}'[/{Theme.SUCCESS}]")

    console.print()

def generate_apikey_interactive():
    """Generate a new API key for external programs with professional interface"""
    console.print()

    # Check if there's an active token
    if not config.get_active_token():
        error_panel = Panel(
            "[bold red]✗ No ChatGPT access token configured![/bold red]\n\n"
            "[dim]You need to add a ChatGPT access token first before generating API keys.[/dim]\n"
            "[bold]Add one with:[/bold] [cyan]/token add[/cyan]",
            title="[bold]Missing Token[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return

    # Welcome panel
    welcome_panel = Panel(
        "[bold white]Generate OpenAI-Compatible API Key[/bold white]\n\n"
        "[dim]This creates a secure API key that external applications can use to access your ChatGPT account.[/dim]",
        title="[bold]API Key Generator[/bold]",
        border_style=Theme.PRIMARY,
        padding=(1, 2)
    )
    console.print(welcome_panel)
    console.print()

    # Ask for name
    name = Prompt.ask(
        "[bold #a855f7]🏷️  API Key Name[/bold #a855f7]",
        default="my-app",
        show_default=True
    )

    if not name:
        console.print(f"[{Theme.ERROR}]✗ Name cannot be empty![/{Theme.ERROR}]")
        return

    # Ensure apikeys is a dictionary
    if not isinstance(config.apikeys, dict):
        config.apikeys = {}

    if name in config.apikeys:
        if not Confirm.ask(f"[{Theme.WARNING}]⚠ API key '{name}' already exists. Replace it?[/{Theme.WARNING}]"):
            console.print("[dim]✗ Operation cancelled[/dim]")
            return

    # Generate the API key
    api_key = config.generate_apikey(name)
    endpoint = config.get("api_endpoint", "http://localhost:5005")

    # Success panel with key details
    success_panel = Panel(
        f"[bold green]✓ API Key Generated Successfully![/bold green]\n\n"
        f"[bold]Name:[/bold] [yellow]{name}[/yellow]\n"
        f"[bold]API Key:[/bold] [#a855f7]{api_key}[/#a855f7]\n"
        f"[bold]Base URL:[/bold] [magenta]{endpoint}/v1[/magenta]",
        title="[bold]Success[/bold]",
        border_style=Theme.SUCCESS,
        padding=(1, 2)
    )
    console.print(success_panel)
    console.print()

    # Usage examples
    examples_panel = Panel(
        "[bold]Configuration Examples:[/bold]\n\n"
        "[bold yellow]Continue.dev (VS Code Extension):[/bold yellow]\n"
        "[dim]Add to settings.json:[/dim]\n"
        "[bold #a855f7]{\n"
        '  "models": [\n'
        '    {\n'
        f'      "apiKey": "{api_key}",\n'
        f'      "apiBase": "{endpoint}/v1",\n'
        '      "model": "gpt-4"\n'
        '    }\n'
        '  ]\n'
        "}\n\n"
        "[bold yellow]Python OpenAI Library:[/bold yellow]\n"
        "[dim]import openai[/dim]\n"
        f'[bold #a855f7]openai.api_key = "{api_key}"\n'
        f'openai.api_base = "{endpoint}/v1"[/bold #a855f7]',
        title="[bold]Usage Examples[/bold]",
        border_style=Theme.INFO,
        padding=(1, 2)
    )
    console.print(examples_panel)
    console.print()

    # Security note
    security_panel = Panel(
        "[bold yellow]🔒 Security Note[/bold yellow]\n\n"
        "[dim]This API key provides access to your ChatGPT account through this CLI.\n"
        "Keep it secure and don't share it publicly. You can revoke it anytime by removing it.[/dim]",
        border_style=Theme.WARNING,
        padding=(1, 2)
    )
    console.print(security_panel)
    console.print()

def list_apikeys():
    """List all generated API keys with professional formatting"""
    # Ensure apikeys is a dictionary
    if not isinstance(config.apikeys, dict):
        config.apikeys = {}

    if not config.apikeys:
        console.print()
        empty_panel = Panel(
            "[bold yellow]⚠ No API keys generated yet![/bold yellow]\n\n"
            "[dim]Generate your first API key with:[/dim] [bold #a855f7]/apikey generate[/bold #a855f7]\n"
            "[dim]API keys allow external applications to use your ChatGPT access.[/dim]",
            title="[bold]No API Keys Found[/bold]",
            border_style=Theme.WARNING,
            padding=(1, 2)
        )
        console.print(empty_panel)
        console.print()
        return

    endpoint = config.get("api_endpoint", "http://localhost:5005")

    console.print()
    
    # Create API keys table
    apikeys_table = Table(
        title="[bold white]Generated API Keys[/bold white]",
        show_header=True,
        header_style="bold white",
        box=box.ROUNDED,
        border_style=Theme.PRIMARY,
        title_style="bold white"
    )
    
    apikeys_table.add_column("Name", style="bold", width=20)
    apikeys_table.add_column("API Key Preview", style="dim", width=25)
    apikeys_table.add_column("Token Source", style="default", width=15)
    apikeys_table.add_column("Created", style="default", width=15)
    apikeys_table.add_column("Status", style="default", width=10)

    for name, data in config.apikeys.items():
        api_key = data.get('key', '')
        token_name = data.get('token_name', 'unknown')
        created = data.get('created', 'unknown')

        # Format created date
        try:
            from datetime import datetime
            created_dt = datetime.fromisoformat(created)
            created_str = created_dt.strftime("%m/%d %H:%M")
        except:
            created_str = created[:10] if len(created) > 10 else created

        # Show preview
        preview = f"{api_key[:15]}...{api_key[-8:]}" if len(api_key) > 30 else api_key

        apikeys_table.add_row(
            f"[{Theme.ACCENT_GREEN}]{name}[/{Theme.ACCENT_GREEN}]",
            preview,
            f"[{Theme.ACCENT_BLUE}]{token_name}[/{Theme.ACCENT_BLUE}]",
            created_str,
            f"[{Theme.SUCCESS}]✓ Active[/{Theme.SUCCESS}]"
        )

    console.print(apikeys_table)
    console.print()
    
    # Management panel
    management_panel = Panel(
        f"[bold]Base URL:[/bold] [magenta]{endpoint}/v1[/magenta]\n\n"
        "[bold]Management Commands:[/bold]\n"
        "• [#a855f7]/apikey test <name>[/#a855f7] - Test API key\n"
        "• [#a855f7]/apikey remove <name>[/#a855f7] - Remove API key\n"
        "• [#a855f7]/apikey generate[/#a855f7] - Create new API key",
        title="[bold]API Key Management[/bold]",
        border_style=Theme.BORDER,
        padding=(1, 2)
    )
    console.print(management_panel)
    console.print()

def extract_actual_model(response_model: str, requested_model: str) -> str:
    """Extract the actual model being used from the response model field"""
    if not response_model:
        return requested_model
    
    # If the response model matches the requested model, return as is
    if response_model == requested_model:
        return response_model
    
    # Handle model mapping - return the actual model that was used
    # This handles cases where gpt-4 becomes gpt-4-0613, etc.
    return response_model

async def verify_model(model: str) -> bool:
    """Verify that the specified model is actually being used by the server"""
    endpoint = config.get("api_endpoint", "http://localhost:5005")
    auth = config.get_active_token()

    if not auth:
        return False

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth}"
    }

    # Simple test message - we only need to check the response model field
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{endpoint}/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                response_model = result.get("model", "")
                
                # Direct model verification - check if the server returned the correct model
                if response_model:
                    # Handle model mapping (e.g., gpt-4 -> gpt-4-0613)
                    if (model in response_model or 
                        response_model in model or
                        any(mapped in response_model for mapped in [
                            "gpt-4-0613", "gpt-4-0125", "gpt-4-turbo", "gpt-4o", "gpt-5",
                            "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106",
                            "o1-preview", "o1-mini", "claude-3"
                        ] if model in ["gpt-4", "gpt-4o", "gpt-4-turbo", "gpt-5", "gpt-3.5-turbo", "o1-preview", "o1-mini", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"])):
                        return True
                
                return False
            else:
                return False

    except Exception:
        return False

async def test_apikey(api_key_name: str, model: str):
    """Test a specific API key"""
    console.print()
    console.print("╔════════════════════════════════════════════════════════════════════════╗", style="#a855f7")
    console.print("║                        [bold bright_white]TESTING API KEY[/bold bright_white]                                ║", style="#9333ea")
    console.print("╚════════════════════════════════════════════════════════════════════════╝", style="#7c3aed")
    console.print()

    # Ensure apikeys is a dictionary
    if not isinstance(config.apikeys, dict):
        config.apikeys = {}

    # Find the API key
    if api_key_name not in config.apikeys:
        console.print(f"[bright_red]✗ API key '{api_key_name}' not found![/bright_red]")
        console.print("[dim bright_white]💡 List available keys with: [#a855f7]/apikey list[/#a855f7][/dim bright_white]")
        console.print()
        return False

    api_key_data = config.apikeys[api_key_name]
    api_key = api_key_data.get('key', '')
    token_name = api_key_data.get('token_name', 'unknown')

    endpoint = config.get("api_endpoint", "http://localhost:5005")

    console.print(f"[dim bright_white]🔑 Key Name:  [bright_yellow]{api_key_name}[/bright_yellow][/dim bright_white]")
    console.print(f"[dim bright_white]🎫 Token:     [bright_green]{token_name}[/bright_green][/dim bright_white]")
    console.print(f"[dim bright_white]🔗 Endpoint:  [#a855f7]{endpoint}[/#a855f7][/dim bright_white]")
    console.print(f"[dim bright_white]🤖 Model:     [bright_yellow]{model}[/bright_yellow][/dim bright_white]")
    console.print()
    console.print("[dim bright_white]📡 Sending test request...[/dim bright_white]")
    console.print()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{endpoint}/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                console.print("==================================================================================", style="bright_green")
                console.print("|                         [bold bright_white]✓ API KEY IS WORKING![/bold bright_white]                          |", style="bright_green")
                console.print("==================================================================================", style="bright_green")
                console.print()
                console.print("[bright_white]Response from AI:[/bright_white]")
                console.print(f"  [#a855f7]{content[:100]}{'...' if len(content) > 100 else ''}[/#a855f7]")
                console.print()
                console.print(f"[bright_green]✓ API key '[bright_yellow]{api_key_name}[/bright_yellow]' is working correctly![/bright_green]")
                console.print()
                console.print("[dim bright_white]You can now use this key in external applications:[/dim bright_white]")
                console.print(f"  [dim bright_white]API Key:  [#a855f7]{api_key}[/#a855f7][/dim bright_white]")
                console.print(f"  [dim bright_white]Base URL: [bright_magenta]{endpoint}/v1[/bright_magenta][/dim bright_white]")
                console.print()
                return True
            else:
                console.print(f"[bright_red]✗ Server error: Status {response.status_code}[/bright_red]")
                error_detail = response.text[:300]
                console.print(f"[dim]{error_detail}[/dim]")
                console.print()
                return False

    except httpx.ConnectError:
        console.print(f"[bright_red]✗ Cannot connect to server at {endpoint}[/bright_red]")
        console.print("[bright_yellow]💡 Make sure the server is running: [#a855f7]py app.py[/#a855f7][/bright_yellow]")
        console.print()
        return False
    except Exception as e:
        console.print(f"[bright_red]✗ Error: {e}[/bright_red]")
        console.print()
        return False

async def send_message(message: str, model: str, conversation_history: list, stream: bool):
    """Send message to API with professional error handling and animations"""
    endpoint = config.get("api_endpoint", "http://localhost:5005")
    auth = config.get_active_token()

    if not auth:
        error_panel = Panel(
            "[bold red]✗ No access token configured![/bold red]\n\n"
            "[dim]You need to add a ChatGPT access token to use the chat feature.[/dim]\n"
            "[bold]Add one with:[/bold] [#a855f7]/token add[/#a855f7]",
            title="[bold]Authentication Required[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return None, model

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth}"
    }

    data = {
        "model": model,
        "messages": conversation_history,
        "stream": stream
    }

    try:
        if stream:
            async with httpx.AsyncClient(timeout=60.0) as client:
                console.print()
                
                # Retro assistant header
                console.print(f"[{Theme.ACCENT_GREEN}]AI[/{Theme.ACCENT_GREEN}] [white]▸[/white] ", end="")
                
                full_response = ""
                actual_model = model  # Default to requested model

                async with client.stream(
                    "POST",
                    f"{endpoint}/v1/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_panel = Panel(
                            f"[bold red]✗ Server Error {response.status_code}[/bold red]\n\n"
                            f"[dim]{error_text.decode()[:200]}[/dim]",
                            title="[bold]Request Failed[/bold]",
                            border_style=Theme.ERROR,
                            padding=(1, 2)
                        )
                        console.print(error_panel)
                        return None, model

                    async for chunk in response.aiter_lines():
                        if chunk.startswith("data: "):
                            chunk_data = chunk[6:]
                            if chunk_data == "[DONE]":
                                break

                            try:
                                json_chunk = json.loads(chunk_data)
                                if "choices" in json_chunk and len(json_chunk["choices"]) > 0:
                                    # Extract actual model from response
                                    if "model" in json_chunk:
                                        actual_model = extract_actual_model(json_chunk["model"], model)
                                    
                                    delta = json_chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        console.print(content, end="")
                                        full_response += content
                            except json.JSONDecodeError:
                                continue

                console.print("\n")
                return full_response, actual_model
        else:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Professional loading animation
                with Status(
                    "[bold #a855f7]🤔 Processing your request...",
                    spinner="dots",
                    spinner_style=Theme.ACCENT_BLUE
                ) as status:
                    response = await client.post(
                        f"{endpoint}/v1/chat/completions",
                        headers=headers,
                        json=data
                    )

                if response.status_code != 200:
                    error_panel = Panel(
                        f"[bold red]✗ Server Error {response.status_code}[/bold red]\n\n"
                        f"[dim]{response.text[:200]}[/dim]",
                        title="[bold]Request Failed[/bold]",
                        border_style=Theme.ERROR,
                        padding=(1, 2)
                    )
                    console.print(error_panel)
                    return None, model

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extract actual model from response
                actual_model = extract_actual_model(result.get("model", ""), model)

                # Retro response display
                console.print()
                console.print(f"[{Theme.ACCENT_GREEN}]AI[/{Theme.ACCENT_GREEN}] [white]▸[/white] {content}")
                console.print()

                return content, actual_model

    except httpx.ConnectError:
        connection_panel = Panel(
            f"[bold red]✗ Cannot connect to server at {endpoint}[/bold red]\n\n"
            "[dim]Make sure the Chat2API server is running:[/dim]\n"
            "[bold]Start server:[/bold] [#a855f7]py app.py[/#a855f7]",
            title="[bold]Connection Failed[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(connection_panel)
        console.print()
        return None, model
    except Exception as e:
        error_panel = Panel(
            f"[bold red]✗ Unexpected error occurred[/bold red]\n\n"
            f"[dim]Error details: {str(e)}[/dim]",
            title="[bold]Error[/bold]",
            border_style=Theme.ERROR,
            padding=(1, 2)
        )
        console.print(error_panel)
        console.print()
        return None, model

def main():
    """Main CLI loop"""
    show_banner()

    # Initialize state
    current_model = config.get("default_model", "gpt-3.5-turbo")
    current_stream = True
    conversation_history = []

    # Show initial status
    show_status(current_model, current_stream, conversation_history)

    # Main loop
    while True:
        try:
            user_input = get_user_input()

            if not user_input.strip():
                continue

            # Exit commands
            if user_input.lower() in ["exit", "/exit", "bye"]:
                console.print()
                goodbye_panel = Panel(
                    "[bold white]Thanks for using Chat2API CLI![/bold white]\n\n"
                    "[dim]Professional AI Chat Interface • v2.0[/dim]\n"
                    "[dim]Made with ♥ by Kira[/dim]",
                    title="[bold]👋 Goodbye![/bold]",
                    border_style=Theme.PRIMARY,
                    padding=(1, 2),
                    title_align="center"
                )
                console.print(goodbye_panel)
                console.print()
                break

            # Handle slash commands
            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else None

                # Help
                if command == "/help":
                    show_help()
                    continue

                # Status
                elif command == "/status":
                    show_status(current_model, current_stream, conversation_history)
                    continue

                # Models
                elif command == "/models":
                    list_models()
                    continue

                elif command == "/use":
                    if arg:
                        current_model = arg
                        
                        # Verify the model is actually working
                        console.print(f"[dim]Verifying model '{current_model}'...[/dim]")
                        is_verified = asyncio.run(verify_model(current_model))
                        
                        if is_verified:
                            model_panel = Panel(
                                f"[bold green]✓ Model switched and verified successfully![/bold green]\n\n"
                                f"[bold]Active Model:[/bold] [yellow]{current_model}[/yellow]\n"
                                f"[bold]Status:[/bold] [green]✓ Verified working[/green]\n"
                                f"[dim]This model will be used for all future conversations.[/dim]",
                                title="[bold]Model Changed & Verified[/bold]",
                                border_style=Theme.SUCCESS,
                                padding=(1, 2)
                            )
                        else:
                            model_panel = Panel(
                                f"[bold yellow]⚠ Model switched but verification failed![/bold yellow]\n\n"
                                f"[bold]Active Model:[/bold] [yellow]{current_model}[/yellow]\n"
                                f"[bold]Status:[/bold] [yellow]⚠ Could not verify[/yellow]\n"
                                f"[dim]The model name was changed, but we couldn't confirm it's actually working.[/dim]\n"
                                f"[dim]Try sending a message to test if it's working correctly.[/dim]",
                                title="[bold]Model Changed (Unverified)[/bold]",
                                border_style=Theme.WARNING,
                                padding=(1, 2)
                            )
                        
                        console.print(model_panel)
                        console.print()
                    else:
                        usage_panel = Panel(
                            "[bold yellow]⚠ Usage: /use <model-name>[/bold yellow]\n\n"
                            "[bold]Examples:[/bold]\n"
                            "• [#a855f7]/use gpt-4[/#a855f7]\n"
                            "• [#a855f7]/use gpt-3.5-turbo[/#a855f7]\n"
                            "• [#a855f7]/use gpt-4o[/#a855f7]\n\n"
                            "[dim]Use [bold #a855f7]/models[/bold #a855f7] to see all available models.[/dim]",
                            title="[bold]Usage Help[/bold]",
                            border_style=Theme.WARNING,
                            padding=(1, 2)
                        )
                        console.print(usage_panel)
                        console.print()
                    continue

                # Stream toggle
                elif command == "/stream":
                    current_stream = not current_stream
                    status_emoji = "✓" if current_stream else "✗"
                    status_text = "enabled" if current_stream else "disabled"
                    status_color = Theme.SUCCESS if current_stream else Theme.WARNING
                    
                    stream_panel = Panel(
                        f"[bold {status_color}]{status_emoji} Streaming {status_text}[/bold {status_color}]\n\n"
                        f"[dim]Mode: {'Real-time responses' if current_stream else 'Batch responses'}[/dim]",
                        title="[bold]Streaming Mode[/bold]",
                        border_style=status_color,
                        padding=(1, 2)
                    )
                    console.print(stream_panel)
                    console.print()
                    continue

                # Clear conversation
                elif command == "/clear":
                    conversation_history = []
                    # Clear screen but keep header and status
                    os.system('cls' if os.name == 'nt' else 'clear')
                    show_banner()
                    show_status(current_model, current_stream, conversation_history)
                    continue

                # Open web interface
                elif command == "/web":
                    open_web_interface()
                    continue

                # Endpoint switching
                elif command == "/endpoint":
                    if arg:
                        switch_endpoint(arg)
                    else:
                        # Show current endpoint and usage
                        current_endpoint = config.get("api_endpoint", "http://localhost:5005")
                        usage_panel = Panel(
                            f"[bold yellow]⚠ Usage: /endpoint <url>[/bold yellow]\n\n"
                            f"[bold]Current Endpoint:[/bold] [yellow]{current_endpoint}[/yellow]\n\n"
                            f"[bold]Examples:[/bold]\n"
                            f"• [#a855f7]/endpoint http://localhost:5005[/#a855f7]\n"
                            f"• [#a855f7]/endpoint https://your-server.com[/#a855f7]\n"
                            f"• [#a855f7]/endpoint https://api.example.com:8080[/#a855f7]\n\n"
                            f"[dim]The endpoint will be tested before switching.[/dim]",
                            title="[bold]Endpoint Usage[/bold]",
                            border_style=Theme.WARNING,
                            padding=(1, 2)
                        )
                        console.print(usage_panel)
                        console.print()
                    continue

                # Reset
                elif command == "/reset":
                    if Confirm.ask(f"[{Theme.WARNING}]⚠ Reset all settings to defaults?[/{Theme.WARNING}]"):
                        # Reset session settings
                        conversation_history = []
                        current_model = "gpt-3.5-turbo"
                        current_stream = True
                        
                        # Reset tokens and API keys
                        config.tokens = {}
                        config.apikeys = {}
                        config.config['active_token'] = None
                        config.save_tokens()
                        config.save_apikeys()
                        config.save_config()
                        
                        # Clear server token file as well
                        try:
                            DATA_DIR.mkdir(exist_ok=True)
                            token_file = DATA_DIR / "token.txt"
                            with open(token_file, 'w') as f:
                                pass  # Clear the file
                        except Exception:
                            pass  # Ignore errors if file doesn't exist
                        
                        reset_panel = Panel(
                            "[bold green]✓ Reset complete![/bold green]\n\n"
                            "[dim]All settings, tokens, and API keys have been reset to defaults.[/dim]\n"
                            "[dim]You'll need to add new tokens with /token add[/dim]",
                            title="[bold]Complete Reset[/bold]",
                            border_style=Theme.SUCCESS,
                            padding=(1, 2)
                        )
                        console.print(reset_panel)
                        console.print()
                    continue


                # Token management
                elif command == "/token":
                    if not arg:
                        console.print()
                        console.print("[bright_yellow]🔑 Token Management Commands:[/bright_yellow]")
                        console.print("  [#a855f7]/token add[/#a855f7]             Add a new token")
                        console.print("  [#a855f7]/token list[/#a855f7]            List all tokens")
                        console.print("  [#a855f7]/token use <name>[/#a855f7]      Use a specific token")
                        console.print("  [#a855f7]/token remove <name>[/#a855f7]   Remove a token")
                        console.print()
                        continue

                    token_parts = arg.split(maxsplit=1)
                    token_cmd = token_parts[0].lower()
                    token_arg = token_parts[1] if len(token_parts) > 1 else None

                    if token_cmd == "add":
                        add_token_interactive()

                    elif token_cmd == "list":
                        list_tokens()

                    elif token_cmd == "use":
                        if token_arg:
                            if config.use_token(token_arg):
                                console.print(f"[bright_green]✓ Now using token '[bright_yellow]{token_arg}[/bright_yellow]'[/bright_green]")
                            else:
                                console.print(f"[bright_red]✗ Token '{token_arg}' not found![/bright_red]")
                                console.print("[dim bright_white]💡 Use [#a855f7]/token list[/#a855f7] to see available tokens[/dim bright_white]")
                        else:
                            console.print("[bright_yellow]⚠ Usage: /token use <name>[/bright_yellow]")

                    elif token_cmd == "remove":
                        if token_arg:
                            if config.remove_token(token_arg):
                                console.print(f"[bright_green]✓ Token '{token_arg}' removed successfully[/bright_green]")
                            else:
                                console.print(f"[bright_red]✗ Token '{token_arg}' not found![/bright_red]")
                        else:
                            console.print("[bright_yellow]⚠ Usage: /token remove <name>[/bright_yellow]")

                    else:
                        console.print(f"[bright_red]✗ Unknown token command: {token_cmd}[/bright_red]")
                        console.print("[dim bright_white]💡 Type [#a855f7]/token[/#a855f7] to see available commands[/dim bright_white]")

                    continue

                # API Key management
                elif command == "/apikey":
                    if not arg:
                        console.print()
                        console.print("[bright_yellow]🔐 API Key Generation Commands:[/bright_yellow]")
                        console.print("  [#a855f7]/apikey generate[/#a855f7]       Generate a new OpenAI-compatible API key")
                        console.print("  [#a855f7]/apikey list[/#a855f7]           List all generated API keys")
                        console.print("  [#a855f7]/apikey test <name>[/#a855f7]    Test a specific API key")
                        console.print("  [#a855f7]/apikey remove <name>[/#a855f7]  Remove an API key")
                        console.print()
                        console.print("[dim bright_white]💡 These API keys can be used in external programs like VS Code, Python, etc.[/dim bright_white]")
                        console.print()
                        continue

                    apikey_parts = arg.split(maxsplit=1)
                    apikey_cmd = apikey_parts[0].lower()
                    apikey_arg = apikey_parts[1] if len(apikey_parts) > 1 else None

                    if apikey_cmd == "generate" or apikey_cmd == "gen" or apikey_cmd == "add":
                        generate_apikey_interactive()

                    elif apikey_cmd == "list" or apikey_cmd == "ls":
                        list_apikeys()

                    elif apikey_cmd == "test":
                        if apikey_arg:
                            asyncio.run(test_apikey(apikey_arg, current_model))
                        else:
                            console.print("[bright_yellow]⚠ Usage: /apikey test <name>[/bright_yellow]")
                            console.print("[dim bright_white]💡 Example: /apikey test my-app[/dim bright_white]")

                    elif apikey_cmd == "remove" or apikey_cmd == "rm" or apikey_cmd == "delete":
                        if apikey_arg:
                            if config.remove_apikey(apikey_arg):
                                console.print(f"[bright_green]✓ API key '{apikey_arg}' removed successfully[/bright_green]")
                            else:
                                console.print(f"[bright_red]✗ API key '{apikey_arg}' not found![/bright_red]")
                        else:
                            console.print("[bright_yellow]⚠ Usage: /apikey remove <name>[/bright_yellow]")

                    else:
                        console.print(f"[bright_red]✗ Unknown apikey command: {apikey_cmd}[/bright_red]")
                        console.print("[dim bright_white]💡 Type [#a855f7]/apikey[/#a855f7] to see available commands[/dim bright_white]")

                    continue

                else:
                    console.print(f"[bright_red]✗ Unknown command: {command}[/bright_red]")
                    console.print("[dim bright_white]💡 Type [#a855f7]/help[/#a855f7] to see all available commands[/dim bright_white]")
                    continue

            # Regular chat message
            conversation_history.append({"role": "user", "content": user_input})

            response, actual_model = asyncio.run(send_message(user_input, current_model, conversation_history, current_stream))

            if response:
                conversation_history.append({"role": "assistant", "content": response})
                # Update current model with the actual model used by the server
                if actual_model != current_model:
                    current_model = actual_model
                    # Show a subtle notification about model change
                    console.print(f"[dim]{Theme.ACCENT_PURPLE}ℹ Model updated to: {actual_model}[/{Theme.ACCENT_PURPLE}][/dim]")
                    console.print()

        except KeyboardInterrupt:
            console.print("\n[bright_yellow]⚠ Interrupted. Type [#a855f7]/exit[/#a855f7] to quit.[/bright_yellow]\n")
            continue
        except EOFError:
            console.print("\n[#a855f7]👋 Goodbye![/#a855f7]\n")
            break
        except Exception as e:
            # Filter out the specific template tag error message
            error_msg = str(e)
            if "closing tag" in error_msg and "doesn't match any open tag" in error_msg:
                # Suppress the template tag error message
                pass
            else:
                # Escape any markup characters in other error messages to prevent markup errors
                error_msg = error_msg.replace('[', '\\[').replace(']', '\\]')
                console.print(f"\n[bright_red]✗ Error: {error_msg}[/bright_red]\n")

if __name__ == "__main__":
    main()
