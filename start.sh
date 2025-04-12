#!/bin/bash

# Ensure logs directory exists
mkdir -p logs

# Kill any existing backend/frontend processes BY NAME (less reliable but safer than port killing)
echo "Attempting to stop existing backend/frontend processes by name..."
pkill -f "python3 server.py" || true
pkill -f "python3 -m http.server 8000" || true
sleep 1

# Kill processes listening on target ports (USE WITH CAUTION)
BACKEND_PORT=5002
FRONTEND_PORT=8000
echo "Attempting to kill processes listening on ports $BACKEND_PORT and $FRONTEND_PORT..."
lsof -t -i :$BACKEND_PORT | xargs kill -9 2>/dev/null || echo "No process found on port $BACKEND_PORT or kill failed."
lsof -t -i :$FRONTEND_PORT | xargs kill -9 2>/dev/null || echo "No process found on port $FRONTEND_PORT or kill failed."
sleep 1 # Give OS a moment after killing

# Remove old execution permissions if needed (not strictly necessary anymore)
# chmod +x start_backend.sh
# chmod +x start_frontend.sh

# Start backend server in the background, redirecting output
echo "Starting backend server (port $BACKEND_PORT, output to logs/backend_output.log)..."
python3 server.py > logs/backend_output.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for the backend to initialize
sleep 2

# Start frontend server in the background, redirecting output
echo "Starting frontend server (port $FRONTEND_PORT, output to logs/frontend_output.log)..."
python3 -m http.server $FRONTEND_PORT > logs/frontend_output.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Check if frontend started successfully
sleep 2
if ! nc -z localhost $FRONTEND_PORT 2>/dev/null; then
    echo "ERROR: Frontend server failed to start on port $FRONTEND_PORT"
    cleanup
    exit 1
fi

# Function to clean up background processes
cleanup() {
    echo "\nCleaning up background processes..."
    # Check if PIDs exist before killing
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Killing backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    else
        echo "Backend server (PID: $BACKEND_PID) already stopped."
    fi
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Killing frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    else
        echo "Frontend server (PID: $FRONTEND_PID) already stopped."
    fi
    # Kill the tail process as well
    echo "Stopping log tailing..."
    kill $(jobs -p | grep tail) 2>/dev/null || true
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM to run the cleanup function
trap cleanup SIGINT SIGTERM

# Tail all relevant log files (check if they exist first)
LOG_FILES=""
[ -f logs/server.log ] && LOG_FILES+=" logs/server.log"
[ -f logs/chat_agent.log ] && LOG_FILES+=" logs/chat_agent.log"
[ -f logs/backend_output.log ] && LOG_FILES+=" logs/backend_output.log"
[ -f logs/frontend_output.log ] && LOG_FILES+=" logs/frontend_output.log"

if [ -n "$LOG_FILES" ]; then
    echo "Tailing logs (Ctrl+C to stop all)..."
    echo "Log files:$LOG_FILES"
    tail -f $LOG_FILES &
else
    echo "No log files found yet to tail."
fi


# Keep the script running while tail is in background, wait for PIDs
# Wait specifically for the backend and frontend PIDs to exit.
# This allows the script to exit cleanly if the servers crash.
wait $BACKEND_PID $FRONTEND_PID
echo "Backend/Frontend process exited. Cleaning up tail..."
# Kill the tail process explicitly if the script exits normally
cleanup # Call cleanup to ensure tail is stopped if servers exit normally 