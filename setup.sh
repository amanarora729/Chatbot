#!/bin/bash

echo "=========================================="
echo "   Humanli.ai Chatbot Project Setup"
echo "=========================================="

# 1. Check/Install uv
if ! command -v uv &> /dev/null; then
    echo "[INFO] 'uv' not found. Installing via pip..."
    pip install uv
else
    echo "[INFO] 'uv' is already installed."
fi

# 2. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    uv venv
else
    echo "[INFO] Virtual environment already exists."
fi

# 3. Install Dependencies
echo "[INFO] Installing dependencies..."
# We use the python executable inside .venv directly to ensure installation in the venv
# even if activation script sourcing varies by shell.
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    VENV_PYTHON=".venv/Scripts/python"
else
    VENV_PYTHON=".venv/bin/python"
fi

# Fallback if VENV_PYTHON doesn't exist (e.g. strict path issues)
if [ ! -f "$VENV_PYTHON" ]; then
    source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
    uv pip install -r requirements.txt
    uv pip install google-genai tantivy pylance sqlalchemy
else
    "$VENV_PYTHON" -m pip install -r requirements.txt
    "$VENV_PYTHON" -m pip install google-genai tantivy pylance sqlalchemy
fi

# 4. Setup .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[INFO] Creating .env from .env.example..."
        cp .env.example .env
        echo "[WARN] Please open .env and add your GOOGLE_API_KEY!"
    else
        echo "[WARN] .env.example not found. Creating empty .env..."
        echo "GOOGLE_API_KEY=" > .env
    fi
else
    echo "[INFO] .env file already exists."
fi

echo "=========================================="
echo "           Setup Complete!"
echo "=========================================="
echo "To run the project, open two terminals:"
echo "  1. Backend:  source .venv/bin/activate && python run_backend.py"
echo "  2. Frontend: source .venv/bin/activate && python run_frontend.py"
