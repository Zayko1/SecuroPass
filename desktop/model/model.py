import mysql.connector
from mysql.connector import Error
import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64, os, random, string, re

# ---- Configuration BDD ----
db_config = {
    "host": "localhost",
    "user": "app",
    "password": "dev",
    "database": "securopass"
}

# ---- Gestion des comptes ----
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def verif_login(username, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT mot_de_passe_hash FROM cles_maitres WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            stored_hashed_password = result[0]
            if bcrypt.checkpw(password.encode(), stored_hashed_password.encode('utf-8')):
                return "Connexion réussie"
            else:
                return "Mot de passe incorrect"
        else:
            return "Utilisateur non trouvé"

    except Error as e:
        return f"error::{str(e)}"
    finally:
        if conn:
            conn.close()

# ---- Fonctions de sécurité ----
def generate_password(length):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    mdp = random.sample(chars, length)
    return ''.join(mdp)

def verif_niveau_mdp(mdp):
    if len(mdp) < 8:
        return "Faible"
    if re.search(r"[A-Za-z]", mdp) and re.search(r"\d", mdp):
        if len(mdp) >= 12 and re.search(r"[!@#$%^&*(),.?\":{}|<>]", mdp):
            return "Fort"
        return "Moyen"
    return "Faible"

def generate_key():
    return os.urandom(32)

def encrypt(data, key):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def decrypt(encrypted_data, key):
    raw = base64.b64decode(encrypted_data)
    iv = raw[:16]
    ciphertext = raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()

def get_passwords(user_id, cle):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT titre, identifiant, mot_de_passe_chiffre, site_web, niveau_securite FROM mots_de_passe WHERE id_utilisateur = %s", (user_id,))
        rows = cursor.fetchall()
        decrypted = []

        for row in rows:
            titre, identifiant, mot_de_passe_chiffre, site_web, niveau = row
            mot_de_passe = decrypt(mot_de_passe_chiffre, cle)
            decrypted.append((titre, identifiant, mot_de_passe, site_web, niveau))

        return decrypted
    except Error as e:
        print("Erreur BDD :", e)
        return []
    finally:
        if conn:
            conn.close()
