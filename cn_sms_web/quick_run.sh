#!/bin/bash

# ONE-CLICK SETUP & RUN SCRIPT FOR CNSMS
# USAGE: ./quick_run.sh

echo "=========================================="
echo "    CNSMS PROJECT - QUICK START"
echo "=========================================="

# 1. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment..."
    python -m venv .venv
fi

# Activate venv (Unix/Windows handling)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# 2. Install Dependencies
echo "[*] Installing dependencies..."
pip install -r requirements.txt

# 3. Initialize Database
echo "[*] Initializing Database..."
if [ -f "instance/cnsms.db" ]; then
    echo "    (Database already exists, skipping init)"
else
    python db_init.py
    python seed.py
    echo "    (Database initialized and seeded)"
fi

# 4. Run Tests
echo "[*] Running Tests..."
pytest
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "[+] All tests passed!"
else
    echo "[-] Some tests failed. Proceeding anyway..."
fi

# 5. Start Server
echo "[*] Starting Flask Server..."
echo "    Access at: http://127.0.0.1:5000"
echo "    Press Ctrl+C to stop."
python app.py
