@echo off
echo ==========================================
echo    Humanli.ai Chatbot Project Setup
echo ==========================================

REM 1. Check/Install uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 'uv' not found. Installing via pip...
    pip install uv
) else (
    echo [INFO] 'uv' is already installed.
)

REM 2. Create Virtual Environment
if not exist .venv (
    echo [INFO] Creating virtual environment...
    uv venv
) else (
    echo [INFO] Virtual environment already exists.
)

REM 3. Install Dependencies
echo [INFO] Installing dependencies...
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
uv pip install google-genai tantivy pylance sqlalchemy

REM 4. Setup .env
if not exist .env (
    if exist .env.example (
        echo [INFO] Creating .env from .env.example...
        copy .env.example .env
        echo [WARN] Please open .env and add your GOOGLE_API_KEY!
    ) else (
        echo [WARN] .env.example not found. Creating empty .env...
        echo GOOGLE_API_KEY= > .env
    )
) else (
    echo [INFO] .env file already exists.
)

echo ==========================================
echo            Setup Complete!
echo ==========================================
echo To run the project:
echo 1. Backend:  .venv\Scripts\python run_backend.py
echo 2. Frontend: .venv\Scripts\python run_frontend.py
pause
