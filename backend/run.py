#!/usr/bin/env python3
"""
Simple Flask runner without debug mode for background execution
"""
from app import app

if __name__ == '__main__':
    print("Starting Concierge API on http://127.0.0.1:5001")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
