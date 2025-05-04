#!/bin/bash

# Kill any existing processes on ports 4200 (Angular) and 8000 (FastAPI)
echo "Stopping any existing servers..."
pkill -f "ng serve" || true
pkill -f "uvicorn" || true

# Start the backend server
echo "Starting backend server..."
cd ../..
export ENV="development"
export DEPLOYED_CLOUD_SERVICE_URL="http://localhost:4200"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start the frontend server
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 10

echo "Both servers are running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

# Function to kill both servers on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID
    exit 0
}

# Set trap for Ctrl+C
trap cleanup INT

# Keep script running
echo "Press Ctrl+C to stop servers"
wait
