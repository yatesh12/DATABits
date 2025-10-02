from flask import Blueprint, request, session
from services.auth_service import AuthService
from utils.response_utils import standardize_response
from utils.decorators import handle_errors
from backend.middleware.auth import require_auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@handle_errors
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data:
        return standardize_response(False, error="No data provided", status_code=400)
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    try:
        user = AuthService.register_user(username, email, password)
        
        # Create session
        session['user_id'] = user.id
        session.permanent = True
        
        return standardize_response(True, {
            'user': user.to_dict()
        }, "Account created successfully! You can now sign in.", status_code=201)
        
    except ValueError as e:
        return standardize_response(False, error=str(e), status_code=400)

@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data:
        return standardize_response(False, error="No data provided", status_code=400)
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    try:
        user = AuthService.login_user(username, password)
        
        # Create session
        session['user_id'] = user.id
        session.permanent = True
        
        return standardize_response(True, {
            'user': user.to_dict()
        }, "Login successful! Welcome back.")
        
    except ValueError as e:
        return standardize_response(False, error=str(e), status_code=401)

@auth_bp.route('/logout', methods=['POST'])
@handle_errors
def logout():
    """User logout endpoint"""
    session.clear()
    return standardize_response(True, message="Logged out successfully")

@auth_bp.route('/me', methods=['GET'])
@require_auth
@handle_errors
def get_current_user():
    """Get current user information"""
    user_data = request.current_user.to_dict()
    return standardize_response(True, {'user': user_data}, "User information retrieved")

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
@handle_errors
def change_password():
    """Change user password"""
    data = request.get_json()
    
    if not data:
        return standardize_response(False, error="No data provided", status_code=400)
    
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    try:
        AuthService.change_password(session['user_id'], current_password, new_password)
        return standardize_response(True, message="Password changed successfully")
        
    except ValueError as e:
        return standardize_response(False, error=str(e), status_code=400)
