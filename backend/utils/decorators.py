from functools import wraps
from flask import session, jsonify, redirect, url_for, request
from backend.models.user import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
            return redirect(url_for('auth_login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
                return redirect(url_for('auth_login'))
            
            user_role = session.get('role_name')
            if user_role not in roles:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Forbidden', 'message': f'Access denied for role: {user_role}'}), 403
                return redirect(url_for('index', error='Access denied'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None
