# Building Chat2API CLI Executable

## Quick Build (Windows)

Simply double-click `build_cli.bat` or run:

```cmd
build_cli.bat
```

The executable will be created in the `dist` folder as `Chat2API-CLI.exe`.

## Manual Build

### 1. Install PyInstaller

```cmd
pip install pyinstaller
```

### 2. Build the executable

```cmd
pyinstaller Chat2API-CLI.spec
```

Or use the one-liner:

```cmd
pyinstaller --onefile --name=Chat2API-CLI --clean --noconfirm --add-data="tokens.json;." --add-data="config.json;." chat.py
```

### 3. Find your executable

The executable will be in: `dist\Chat2API-CLI.exe`

## Running the Executable

```cmd
dist\Chat2API-CLI.exe
```

Or simply double-click `Chat2API-CLI.exe` in the `dist` folder.

## Configuration

The executable will create configuration files in:
- Windows: `%USERPROFILE%\.chat2api_cli\`

You can also place `tokens.json` and `config.json` in the same directory as the executable.

## Troubleshooting

### "Python not found"
Make sure Python is installed and added to your PATH.

### "Module not found" errors
Install all required dependencies:
```cmd
pip install -r requirements.txt
```

### Large file size
The executable includes all dependencies. This is normal for Python executables (typically 20-50 MB).

## Distribution

You can distribute the single `Chat2API-CLI.exe` file. Users don't need Python installed to run it.
