#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create one with your GEMINI_API_KEY"
    exit 1
fi

# Start the Flask server
echo "Starting backend server..."
Python3 server.py 