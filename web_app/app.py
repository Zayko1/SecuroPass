import os
from flask import Flask, render_template, redirect, url_for, session, request, jsonify, flash
from flask_cors import CORS
from flask_session import Session
from functools import wraps
from datetime import timedelta
from flask_jwt_extended import JWTManager
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE']   = True   # car on tourne en HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['JWT_SECRET_KEY'] = secrets.token_hex(16)

Session(app)

# --- CORS : support des cookies + toutes origines moz-extension ---
CORS(app,
     supports_credentials=True,
     resources={r"/*": {
         "origins": [
           "https://217.154.24.244:5000",
           r"moz-extension://.*"
         ],
         "allow_headers": ["Content-Type", "Authorization"],
         "methods": ["GET", "POST", "OPTIONS"]
     }})

jwt = JWTManager(app)

from controllers.auth_controller import auth_bp
from controllers.password_controller import password_bp

app.register_blueprint(auth_bp)
app.register_blueprint(password_bp)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('password.dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context='adhoc')
