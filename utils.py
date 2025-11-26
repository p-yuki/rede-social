from functools import wraps
from flask import session, redirect, url_for, flash
from typing import Optional

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('usuarios_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename: Optional[str]) -> bool:
    if filename is None:
        return False
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp']
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
