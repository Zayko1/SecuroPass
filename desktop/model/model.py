import mysql.connector
from mysql.connector import Error
import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64, os, random, string, re

# ---- Configuration BDD ----
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
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

        # Vérifier si l'utilisateur existe
        cursor.execute("SELECT mot_de_passe_hash FROM cles_maitres WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            # L'utilisateur existe, vérifier le mot de passe
            stored_hashed_password = result[0]
            if bcrypt.checkpw(password.encode(), stored_hashed_password):
                return "Connexion réussie"
            else:
                return "Mot de passe incorrect"
        else:
            # L'utilisateur n'existe pas, créer un nouvel utilisateur
            hashed_password = hash_password(password)
            cursor.execute("INSERT INTO cles_maitres (username, mot_de_passe_hash) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            return "Compte créé avec succès"

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

def create_account(username, key, email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT * FROM cles_maitres WHERE username = %s", (username,))
        if cursor.fetchone():
            return "L'utilisateur existe déjà."

        # Hacher la clé (ou mot de passe) pour le stockage
        hashed_key = hash_password(key)

        # Insérer le nouvel utilisateur
        cursor.execute(
            "INSERT INTO cles_maitres (username, mot_de_passe_hash, cle_chiffrement) VALUES (%s, %s, %s)",
            (username, hashed_key, key)
        )
        conn.commit()
        conn.close()
        return "Compte créé avec succès."

    except Error as e:
        return f"Erreur : {str(e)}"