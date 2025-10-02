from flask import jsonify
from werkzeug.exceptions import RequestEntityTooLarge
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return jsonify({
            "success": False,
            "error": "File too large. Maximum size is 50MB.",
            "timestamp": datetime.now().isoformat()
        }), 413

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "success": False,
            "error": "Endpoint not found",
            "timestamp": datetime.now().isoformat()
        }), 404

    @app.errorhandler(500)
    def handle_internal_error(e):
        logger.error(f"Internal server error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }), 500
