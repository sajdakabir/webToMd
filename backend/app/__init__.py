from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config
import os

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS with exposed headers - allow all origins for testing
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Disposition"],
             "max_age": 3600
         }},
         supports_credentials=False)
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Create output directory
    os.makedirs(app.config['OUTPUT_DIR'], exist_ok=True)
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
