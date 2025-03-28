#!/bin/bash

# Make scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh

# Start backend server in the background
echo "Starting backend server..."
./start_backend.sh &

# Wait a moment for the backend to initialize
sleep 2

# Start frontend server
echo "Starting frontend server..."
./start_frontend.sh

# Trap SIGINT to kill background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT 