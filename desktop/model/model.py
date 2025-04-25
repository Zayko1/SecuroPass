import mysql.connector
from mysql.connector import Error
import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64, os, random, string, re

# ---- Configuration BDD ----
db_config = {
    "host": "",
    "user": "",
    "password": "",
    "database": ""
}

# ---- Gestion des comptes ----
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def enregistrer_compte(username, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM comptes_maitres WHERE username = %s", (username,))
        if cursor.fetchone():
            return "exists"

        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO comptes_maitres (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        conn.close()
        return "success"

    except Error as e:
        return f"error::{str(e)}"

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
