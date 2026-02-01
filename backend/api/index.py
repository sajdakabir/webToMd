"""
Vercel serverless handler for the Flask application
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

try:
    app = create_app()
except Exception as e:
    print(f"Error creating Flask app: {e}")
    import traceback
    traceback.print_exc()
    raise
