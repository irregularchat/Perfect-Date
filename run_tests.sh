#!/bin/bash

# Exit on any error
set -e

echo "=== Setting up virtual environment ==="
# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Setting environment variables ==="
# Export environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Using default environment variables."
    export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
    export GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY:-""}
    export PORT=${PORT:-7860}
fi

# Echo environment variables (without sensitive values)
echo "PORT=${PORT}"
echo "OPENAI_API_KEY=***" # Masking for security
echo "GOOGLE_MAPS_API_KEY=***" # Masking for security

# Check if we should use pytest or unittest
if [ "$1" == "--pytest" ]; then
    echo "=== Running tests with pytest ==="
    python -m pytest
else
    echo "=== Running tests with unittest ==="
    python3 tests/run_tests.py
fi

# Print success message
if [ $? -eq 0 ]; then
    echo "=== Tests completed successfully ==="
else
    echo "=== Tests failed with errors ==="
    exit 1
fi 