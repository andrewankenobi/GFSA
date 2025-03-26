#!/usr/bin/env python3
"""
Script to run the Startup Analyzer web application.
"""

import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.web_app import app

if __name__ == "__main__":
    # Make sure GEMINI_API_KEY is set
    if "GEMINI_API_KEY" not in os.environ:
        print("Warning: GEMINI_API_KEY environment variable is not set.")
        print("The chat functionality will not work without an API key.")
        print("Please set it using: export GEMINI_API_KEY='your-api-key'")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 