from flask import Blueprint, render_template, request, jsonify, session
from models import model
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

password_bp = Blueprint('password', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Non authentifié'}), 401
        return f(*args, **kwargs)
    return decorated_function

@password_bp.route('/passwords')
@login_required
def dashboard():
    return render_template('passwords.html', username=session.get('username'))

@password_bp.route('/api/passwords', methods=['GET'])
@login_required
def get_passwords():
    user_id = session['user_id']
    user_key = bytes.fromhex(session['user_key'])

    search_query = request.args.get('search', '')

    if search_query:
        passwords = model.search_passwords(user_id, search_query, user_key)
    else:
        passwords = model.get_passwords(user_id, user_key)

    # Masquer les mots de passe pour l'affichage
    for p in passwords:
        p['masked_password'] = '*' * 8
        p['date_ajout'] = p['date_ajout'].strftime('%Y-%m-%d %H:%M')

    return jsonify(passwords)

@password_bp.route('/api/passwords', methods=['POST'])
@login_required
def add_password():
    user_id = session['user_id']
    user_key = bytes.fromhex(session['user_key'])

    data = request.get_json()
    title = data.get('title', '').strip()
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')
    site = data.get('site', '').strip()
    notes = data.get('notes', '').strip()

    if not title or not identifier or not password:
        return jsonify({'error': 'Titre, identifiant et mot de passe requis'}), 400

    level = model.verif_niveau_mdp(password)
    ok, msg = model.add_password(user_id, title, identifier, password,
                                site, notes, level, user_key)

    if ok:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'error': msg}), 400

@password_bp.route('/api/passwords/<int:entry_id>', methods=['PUT'])
@login_required
def update_password(entry_id):
    user_id = session['user_id']
    user_key = bytes.fromhex(session['user_key'])

    data = request.get_json()
    title = data.get('title', '').strip()
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')
    site = data.get('site', '').strip()
    notes = data.get('notes', '').strip()

    if not title or not identifier or not password:
        return jsonify({'error': 'Titre, identifiant et mot de passe requis'}), 400

    ok, msg = model.update_password(entry_id, title, identifier, password,
                                   site, notes, user_key)

    if ok:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'error': msg}), 400

@password_bp.route('/api/passwords/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_password(entry_id):
    ok, msg = model.delete_password(entry_id)

    if ok:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'error': msg}), 400

@password_bp.route('/api/generate-password', methods=['POST'])
@login_required
def generate_password():
    data = request.get_json()
    length = data.get('length', 16)
    include_lower = data.get('include_lower', True)
    include_upper = data.get('include_upper', True)
    include_digits = data.get('include_digits', True)
    include_special = data.get('include_special', True)

    password = model.generate_password(length, include_lower, include_upper,
                                     include_digits, include_special)
    level = model.verif_niveau_mdp(password)

    return jsonify({
        'password': password,
        'level': level
    })

@password_bp.route('/api/password-strength', methods=['POST'])
@login_required
def check_password_strength():
    data = request.get_json()
    password = data.get('password', '')
    level = model.verif_niveau_mdp(password)
    return jsonify({'level': level})(venv)

password_bp.route('/api/passwords', methods=['GET'])
@jwt_required()
def api_get_passwords():
    user_id  = get_jwt_identity()
    user_key = bytes.fromhex(session.get('user_key'))
    pwds     = model.get_passwords(user_id, user_key)
    # formate la date
    for p in pwds:
        if hasattr(p.get('date_ajout'), 'strftime'):
            p['date_ajout'] = p['date_ajout'].strftime('%Y-%m-%d %H:%M')
    return jsonify({'passwords': pwds})
