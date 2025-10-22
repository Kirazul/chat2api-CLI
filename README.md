# Chat2API CLI

<div align="center">

![Chat2API CLI Preview](assets/preview.png)

**Transform ChatGPT into a powerful OpenAI-compatible API with a professional CLI interface**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

</div>

---

## Overview

Chat2API CLI is a fork of [Niansuh/chat2api](https://github.com/Niansuh/chat2api) that adds a comprehensive command-line interface for managing ChatGPT access tokens, generating OpenAI-compatible API keys, and interacting with the Chat2API server. This project bridges the gap between ChatGPT's web interface and standard OpenAI API clients.

## What We Added

### 🎨 Professional CLI Interface
- **Modern Terminal UI** - Built with Rich library for beautiful, colorful output
- **Interactive Commands** - Intuitive slash commands with auto-completion
- **Real-time Status** - Live connection monitoring and server health checks
- **Smart Prompts** - Context-aware input with helpful suggestions

### 🔑 Token Management System
- **Multi-Token Support** - Store and manage multiple ChatGPT access tokens
- **Token Labeling** - Organize tokens with custom names
- **Active Token Switching** - Seamlessly switch between different accounts
- **Secure Storage** - Tokens stored locally in JSON format

### 🔐 API Key Generation
- **OpenAI-Compatible Keys** - Generate `sk-xxx` format API keys
- **Token Mapping** - Automatically map API keys to ChatGPT tokens
- **External Integration** - Use with any OpenAI-compatible client
- **Key Management** - List, test, and revoke API keys easily

### 🌐 Server Synchronization
- **CLI-to-Server Sync** - Automatically sync tokens and API keys to any remote server
- **Middleware Integration** - Transparent API key mapping at the server level
- **Multi-Environment Support** - Works with local and remote endpoints (any hosting provider)

### 🛠️ Enhanced Features
- **Endpoint Switching** - Connect to different Chat2API servers on the fly
- **Model Selection** - Choose from GPT-3.5, GPT-4, GPT-4o, O1, and more
- **Streaming Support** - Toggle streaming mode for real-time responses
- **Web Interface Launcher** - Quick access to ChatGPT web UI
- **Health Monitoring** - Built-in server health checks and diagnostics

## Features

### Core Functionality
- ✅ Convert ChatGPT web access to OpenAI API format
- ✅ Support for all GPT models (3.5, 4, 4o, O1, etc.)
- ✅ Streaming and non-streaming responses
- ✅ Token rotation and management
- ✅ API key authentication
- ✅ CORS support for web applications
- ✅ Cloud deployment ready

### CLI Commands

#### Chat & Navigation
- `/help` - Show command reference
- `/status` - Display system status and configuration
- `/clear` - Clear conversation history
- `/web` - Open ChatGPT web interface
- `/exit` - Exit the application

#### Model Management
- `/models` - List available AI models
- `/use <model>` - Switch to a different model
- `/stream` - Toggle streaming mode

#### Authentication
- `/token add` - Add a new access token
- `/token list` - List all saved tokens
- `/token use <name>` - Switch to a specific token
- `/token remove <name>` - Remove a token

#### API Integration
- `/endpoint <url>` - Switch API endpoint
- `/apikey generate` - Generate OpenAI-compatible API key
- `/apikey list` - List all generated API keys
- `/apikey test <name>` - Test a specific API key
- `/apikey remove <name>` - Remove an API key

#### System
- `/reset` - Reset all settings, tokens, and API keys

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Kirazul/chat2api-cli.git
cd chat2api-cli
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

4. **Start the server**
```bash
python start.py
```

5. **Launch the CLI** (in a new terminal)
```bash
python chat.py
```

## Usage

### Getting Your Access Token

1. Visit [https://chatgpt.com/api/auth/session](https://chatgpt.com/api/auth/session)
2. Copy the `accessToken` value
3. In the CLI, run `/token add` and paste your token

### Generating API Keys

1. Add a ChatGPT access token first
2. Run `/apikey generate` in the CLI
3. Give your API key a name (e.g., "my-app")
4. Copy the generated `sk-xxx` key
5. Use it with any OpenAI-compatible client

### Using with External Applications

#### Continue.dev (VS Code Extension)
```json
{
  "models": [
    {
      "apiKey": "sk-your-generated-key",
      "apiBase": "http://localhost:5005/v1",
      "model": "gpt-4"
    }
  ]
}
```

#### Python OpenAI Library
```python
import openai

openai.api_key = "sk-your-generated-key"
openai.api_base = "http://localhost:5005/v1"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### cURL
```bash
curl http://localhost:5005/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-generated-key" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Configuration

### Environment Variables

```bash
# Server Configuration
HOST=0.0.0.0
PORT=5005
ENVIRONMENT=development

# Security
API_PREFIX=
AUTHORIZATION=
AUTH_KEY=

# ChatGPT Settings
CHATGPT_BASE_URL=https://chatgpt.com
PROXY_URL=
HISTORY_DISABLED=true
RANDOM_TOKEN=true

# Gateway
ENABLE_GATEWAY=false
```

### CLI Configuration

The CLI stores its configuration in:
- `config.json` - General settings and active token
- `tokens.json` - Stored ChatGPT access tokens
- `apikeys.json` - Generated API keys and mappings

## Deployment

The CLI sync feature works with any hosting provider. Simply deploy the server and configure the CLI endpoint:

**Examples:**
```bash
# Heroku
/endpoint https://your-app.herokuapp.com

# DigitalOcean / VPS
/endpoint https://your-domain.com

# Render
/endpoint https://your-app.onrender.com

# Railway
/endpoint https://your-app.up.railway.app
```

The CLI will automatically sync tokens and API keys to any configured endpoint.

### Docker

```bash
# Build the image
docker build -t chat2api-cli .

# Run the container
docker run -p 5005:5005 -v $(pwd)/data:/app/data chat2api-cli
```

## Architecture

### Server Components
- **FastAPI Application** - Main API server (`app.py`)
- **Chat Service** - ChatGPT interaction handler (`chatgpt/ChatService.py`)
- **API Key Mapper** - Middleware for key-to-token mapping (`middleware/apikey_mapper.py`)
- **Sync API** - CLI-to-server synchronization (`api/sync.py`)
- **Token Management** - Token rotation and validation (`chatgpt/authorization.py`)

### CLI Components
- **Interactive Interface** - Rich-based terminal UI (`chat.py`)
- **Configuration Manager** - Settings and storage (`Config` class)
- **API Client** - HTTP client for server communication
- **Command System** - Slash command parser and executor

### Data Flow
```
External App → API Key → Middleware → Token Mapping → ChatGPT Token → ChatGPT API
     ↓
CLI → Token Management → Server Sync → API Key Generation
```

## API Endpoints

### Chat Completions
```
POST /v1/chat/completions
```

### Token Management
```
GET  /tokens
POST /tokens/upload
POST /tokens/clear
POST /tokens/error
GET  /tokens/add/{token}
```

### Admin & Sync
```
POST /admin/sync/tokens
POST /admin/sync/apikeys
GET  /admin/sync/status
GET  /admin/debug/apikey/{api_key}
```

### Health & Status
```
GET /
GET /health
GET /test
```

## Supported Models

- **GPT-3.5**: `gpt-3.5-turbo`
- **GPT-4**: `gpt-4`, `gpt-4-mobile`, `gpt-4-gizmo`
- **GPT-4o**: `gpt-4o`, `gpt-4o-mini`, `gpt-4o-canmore`, `gpt-4.5o`
- **GPT-5**: `gpt-5`
- **O1 Series**: `o1-preview`, `o1-mini`, `o1`
- **Auto**: `auto` (automatic model selection)

## Troubleshooting

### CLI won't connect to server
```bash
# Check if server is running
curl http://localhost:5005/health

# Verify endpoint in CLI
/status
/endpoint http://localhost:5005
```

### API key not working
```bash
# Test the API key
/apikey test <name>

# Check server logs for mapping issues
# Verify token is valid
/token list
```

### Token expired
```bash
# Remove old token
/token remove <name>

# Add new token
/token add
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original project: [Niansuh/chat2api](https://github.com/Niansuh/chat2api)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- CLI powered by [Rich](https://github.com/Textualize/rich)
- Inspired by the OpenAI API

## Support

- 📫 Issues: [GitHub Issues](https://github.com/Kirazul/chat2api-cli/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Kirazul/chat2api-cli/discussions)

---

<div align="center">

[⭐ Star us on GitHub](https://github.com/Kirazul/chat2api-cli) | [🐛 Report Bug](https://github.com/Kirazul/chat2api-cli/issues) | [✨ Request Feature](https://github.com/Kirazul/chat2api-cli/issues)

</div>
