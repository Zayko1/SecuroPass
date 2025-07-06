from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import model
from flask_jwt_extended import create_access_token
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Veuillez remplir tous les champs.', 'error')
            return render_template('login.html')

        ok, result = model.verif_login(username, password)
        if ok:
            session['user_id'] = result['user_id']
            session['username'] = result['username']
            session['user_key'] = result['user_key'].hex()
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            flash(result, 'error')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not username or not password:
            flash('Veuillez remplir tous les champs.', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash("Le nom d'utilisateur doit contenir au moins 3 caractères.", 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html')

        # Créer le compte
        user_key = model.generate_key()
        ok, msg = model.create_account(username, password, user_key)

        if ok:
            flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(msg, 'error')

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))


auth_bp.route('/api/auth', methods=['POST'])
def api_auth():
    # attend JSON { username, password }
    data = request.get_json() or {}
    user  = data.get('username','').strip()
    pwd   = data.get('password','')
    ok, result = model.verif_login(user, pwd)
    if not ok:
        return jsonify({'error': result}), 401
    # crée un token avec l’ID utilisateur
    token = create_access_token(identity=result['user_id'])
    return jsonify({'access_token': token}), 200
