#!/bin/bash

# Check if Python's http.server is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Start the frontend server
echo "Starting frontend server..."
python3 -m http.server 8000 