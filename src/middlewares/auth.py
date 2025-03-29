from functools import wraps
from flask import request, jsonify
from src.config.config import Config

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check API key in headers or request body
        api_key = request.headers.get("X-API-KEY") or (request.json.get('api_key') if request.json else None)
        
        if not api_key:
            return jsonify({
                "status": "error",
                "error": "Unauthorized",
                "message": "API key is missing",
                "suggestion": "Include API key in X-API-KEY header or request body"
            }), 401
        
        if api_key not in Config.API_KEYS:
            return jsonify({
                "status": "error",
                "error": "Unauthorized",
                "message": "Invalid API key",
                "suggestion": f"Valid keys are: {', '.join(Config.API_KEYS.keys())}"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
