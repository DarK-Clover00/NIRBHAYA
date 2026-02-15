#!/bin/bash
# Script to run the mobile client

echo "Starting NIRBHAYA Mobile Client..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the mobile client
python mobile/main.py
