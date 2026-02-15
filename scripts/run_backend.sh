#!/bin/bash
# Script to run the backend API server

echo "Starting NIRBHAYA Backend API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the backend
python backend/main.py
