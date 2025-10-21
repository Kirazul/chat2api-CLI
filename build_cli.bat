@echo off
echo ============================================================
echo Building Chat2API CLI Executable
echo ============================================================
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install PyInstaller if needed
echo Installing/Updating PyInstaller...
py -m pip install --upgrade pyinstaller

echo.
echo Building executable...
echo.

REM Build with PyInstaller
py -m PyInstaller --onefile --name=Chat2API-CLI --clean --noconfirm --add-data="tokens.json;." --add-data="config.json;." --hidden-import=rich --hidden-import=prompt_toolkit --hidden-import=httpx chat.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Build FAILED!
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build SUCCESSFUL!
echo ============================================================
echo.
echo Executable location: dist\Chat2API-CLI.exe
echo.

REM Show file size
if exist "dist\Chat2API-CLI.exe" (
    for %%A in ("dist\Chat2API-CLI.exe") do echo File size: %%~zA bytes
)

echo.
echo You can now run: dist\Chat2API-CLI.exe
echo.
pause
