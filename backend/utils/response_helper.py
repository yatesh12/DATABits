from flask import jsonify
from datetime import datetime

def standardize_response(success=True, data=None, message="", error=None, status_code=200):
    """Standardize all API responses"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        response["data"] = data
    else:
        response["error"] = error or message
        
    return jsonify(response), status_code
