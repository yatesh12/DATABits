import bcrypt
import uuid
from datetime import datetime
import threading

class User:
    """User model for handling user data and operations"""
    
    def __init__(self, username, email, password):
        self.id = str(uuid.uuid4())
        self.username = username.strip()
        self.email = email.lower().strip()
        self.password = self._hash_password(password)
        self.created_at = datetime.now().isoformat()
        self.last_login = None
    
    def _hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now().isoformat()
    
    def to_dict(self, include_password=False):
        """Convert user to dictionary"""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
        if include_password:
            user_dict['password'] = self.password
        return user_dict

class UserStorage:
    """Thread-safe user storage"""
    
    def __init__(self):
        self.users = {}
        self.lock = threading.Lock()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        with self.lock:
            # Check if user already exists
            for user in self.users.values():
                if (user.username.lower() == username.lower() or 
                    user.email == email.lower()):
                    raise ValueError("Username or email already exists")
            
            user = User(username, email, password)
            self.users[user.id] = user
            return user
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_credentials(self, username):
        """Get user by username or email"""
        username_lower = username.lower()
        for user in self.users.values():
            if (user.username.lower() == username_lower or 
                user.email == username_lower):
                return user
        return None
    
    def get_all_users(self):
        """Get all users"""
        with self.lock:
            return list(self.users.values())
    
    def delete_user(self, user_id):
        """Delete user by ID"""
        with self.lock:
            if user_id in self.users:
                del self.users[user_id]
                return True
            return False

# Global user storage instance
user_storage = UserStorage()
