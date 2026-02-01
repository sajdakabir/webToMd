"""
Vercel serverless handler for the Flask application
"""
from app import create_app

app = create_app()

# Export the Flask app for Vercel to use as WSGI handler
