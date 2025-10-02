from functools import wraps
from flask import request, jsonify

def validate_dataset_id(f):
    """Middleware to validate dataset ID"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        dataset_id = kwargs.get('dataset_id')
        if not dataset_id:
            return jsonify({
                "success": False,
                "error": "Dataset ID is required",
                "timestamp": "2025-06-06T11:56:10.000Z"
            }), 400
        return f(*args, **kwargs)
    return decorated_function
