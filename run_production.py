#!/usr/bin/env python3
"""
Production server for Voice Cloning Web Interface
Uses Waitress instead of Flask's development server
"""

from waitress import serve
from web_app import app

if __name__ == '__main__':
    PORT = 5001

    print("=" * 60)
    print("🎙️  XTTS v2 Voice Cloning - Production Server")
    print("=" * 60)
    print(f"\nStarting production server on port {PORT}...")
    print(f"Access at: http://localhost:{PORT}")
    print(f"Or: http://192.168.1.189:{PORT}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    print()

    # Run with Waitress (production WSGI server)
    # No debug mode, no auto-reloader, no zombie processes
    serve(app, host='0.0.0.0', port=PORT, threads=4)
