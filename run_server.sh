#!/bin/bash

# Kill any existing servers
echo "Stopping any existing servers..."
sudo pkill -9 -f "web_app.py"
sudo fuser -k 5001/tcp 2>/dev/null
sleep 2

# Start fresh server
cd "/home/distiller/projects/voice cloning"
source venv/bin/activate

echo ""
echo "Starting Voice Cloning Web Server..."
echo "============================================================"
echo "Access at: http://localhost:5001"
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

python web_app.py
