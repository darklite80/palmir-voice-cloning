#!/bin/bash
# Start the Voice Cloning Web Interface

cd "/home/distiller/projects/voice cloning"

# Activate virtual environment
source venv/bin/activate

# Start Flask app
echo "Starting Voice Cloning Web Interface..."
echo "Open your browser to: http://localhost:5001"
echo "Or from another device: http://$(hostname -I | awk '{print $1}'):5001"
echo ""
echo "Press Ctrl+C to stop"

python web_app.py
