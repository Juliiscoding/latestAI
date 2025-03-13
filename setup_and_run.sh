#!/bin/bash

# Setup and Run Script for Predictive Inventory Management System

echo "Setting up Predictive Inventory Management System..."

# Create data directory if it doesn't exist
mkdir -p data
mkdir -p models

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if data files exist
if [ ! -f "data/article.json" ] || [ ! -f "data/sale.json" ] || [ ! -f "data/inventory.json" ]; then
  echo "Data files not found. Running data fetching script..."
  python fetch_working_data.py
else
  echo "Data files found. Skipping data fetching."
fi

# Start the API server
echo "Starting API server..."
python api_server.py &
API_PID=$!

# Wait for API server to start
echo "Waiting for API server to start..."
sleep 5

# Start a simple HTTP server for the dashboard
echo "Starting HTTP server for dashboard..."
python -m http.server 8080 &
HTTP_PID=$!

# Open the dashboard in the default browser
echo "Opening dashboard in browser..."
open http://localhost:8080/earth_dashboard.html

# Function to handle script termination
function cleanup {
  echo "Shutting down servers..."
  kill $API_PID
  kill $HTTP_PID
  echo "Servers stopped."
}

# Register the cleanup function to be called on exit
trap cleanup EXIT

# Keep the script running
echo "System is running. Press Ctrl+C to stop."
wait
