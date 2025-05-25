import mysql.connector
from mysql.connector import Error
import bcrypt
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
import base64, os, random, string, re

# ---- Configuration BDD ----
db_config = {
    "host": "",
    "user": "",
    "port": "3306",
    "password": "",
    "database": ""
}

# ---- Gestion des comptes ----

def create_account(username, password, email):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 1) unicité
        cursor.execute("SELECT 1 FROM cles_maitres WHERE username = %s", (username,))
        if cursor.fetchone():
            return "L'utilisateur existe déjà."

        # 2) hash bcrypt
        pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # 3) clé utilisateur, sel KDF, dérivation
        user_key = os.urandom(32)
        kdf_salt = os.urandom(16)
        enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
        

        # 4) chiffrement AES-GCM de user_key
        cipher = AES.new(enc_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(user_key)

        # 5) insertion
        cursor.execute(
            """
            INSERT INTO cles_maitres
              (username,
               mot_de_passe_hash,
               cle_chiffrement,
               kdf_salt,
               nonce,
               tag,
               encrypted_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                username,
                pwd_hash,
                user_key,
                kdf_salt,
                cipher.nonce,
                tag,
                ciphertext
            )
        )
        conn.commit()
        return "Compte créé avec succès."
    except Error as e:
        return f"Erreur BDD : {e}"
    finally:
        if conn:
            conn.close()

def verif_login(username, password):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mot_de_passe_hash, kdf_salt, nonce, tag, encrypted_key
            FROM cles_maitres
            WHERE username = %s
        """, (username,))
        row = cursor.fetchone()
        if not row:
            return False, "Utilisateur non trouvé"

        stored_hash, kdf_salt, nonce, tag, ciphertext = row
        # 1) check bcrypt
        if not bcrypt.checkpw(password.encode(), stored_hash):
            return False, "Mot de passe incorrect"

        # 2) re-dériver la clé et déchiffrer
        enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
        cipher = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
        user_key = cipher.decrypt_and_verify(ciphertext, tag)

        return True, user_key

    except (Error, ValueError) as e:
        return False, f"Erreur lors de la connexion : {e}"
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
