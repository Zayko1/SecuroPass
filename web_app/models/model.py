import os
import string
import random
import re
import mysql.connector
from mysql.connector import Error
import bcrypt
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from config import db_config

def _get_connection():
    """Ouvre une connexion MySQL avec la config."""
    return mysql.connector.connect(**db_config)

def create_account(username: str, password: str, user_key: bytes) -> tuple[bool, str]:
    """Crée un compte utilisateur avec chiffrement de la clé."""
    try:
        conn = _get_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM cles_maitres WHERE username=%s", (username,))
        if cur.fetchone():
            return False, "L'utilisateur existe déjà."

        pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
        kdf_salt = os.urandom(16)
        enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
        
        nonce = os.urandom(12)
        cipher = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(user_key)

        cur.execute("""
            INSERT INTO cles_maitres
              (username, mot_de_passe_hash, cle_chiffrement, kdf_salt, nonce, tag, encrypted_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, pwd_hash, user_key, kdf_salt, nonce, tag, ciphertext))
        
        conn.commit()
        return True, "Compte créé avec succès."
    except Error as e:
        return False, f"Erreur BDD : {e}"
    finally:
        if conn:
            conn.close()

def verif_login(username: str, password: str) -> tuple[bool, dict|str]:
    """Vérifie les credentials et retourne les infos utilisateur."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("""
           SELECT id, mot_de_passe_hash, cle_chiffrement, kdf_salt, nonce, tag, encrypted_key
           FROM cles_maitres WHERE username=%s
        """, (username,))
        row = cur.fetchone()
        
        if not row:
            return False, "Utilisateur non trouvé."

        user_id, stored_hash, clear_key, kdf_salt, nonce, tag, ciphertext = row

        if not bcrypt.checkpw(password.encode(), stored_hash.encode("utf-8")):
            return False, "Mot de passe incorrect."

        enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
        cipher = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
        try:
            user_key = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            user_key = clear_key

        return True, {"user_key": user_key, "user_id": user_id, "username": username}
    except (Error, ValueError) as e:
        return False, f"Erreur connexion : {e}"
    finally:
        if conn:
            conn.close()

def generate_key() -> bytes:
    """Génère une clé AES-256."""
    return os.urandom(32)

def generate_password(length: int = 16, include_lower=True, include_upper=True, 
                     include_digits=True, include_special=True) -> str:
    """Génère un mot de passe aléatoire."""
    pool = ""
    if include_lower:
        pool += string.ascii_lowercase
    if include_upper:
        pool += string.ascii_uppercase
    if include_digits:
        pool += string.digits
    if include_special:
        pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not pool:
        pool = string.ascii_letters + string.digits
    
    return ''.join(random.choice(pool) for _ in range(length))

def verif_niveau_mdp(mdp: str) -> str:
    """Évalue la force d'un mot de passe."""
    if len(mdp) < 8:
        return "Faible"
    score = sum([
        bool(re.search(r"[a-z]", mdp)),
        bool(re.search(r"[A-Z]", mdp)),
        bool(re.search(r"\d", mdp)),
        bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", mdp)),
        len(mdp) >= 12
    ])
    return ["Faible", "Moyen", "Moyen", "Fort", "Fort", "Très Fort"][score]

def add_password(user_id: int, title: str, ident: str, clear_pwd: str,
                 site: str = "", notes: str = "", level: str = "", 
                 user_key: bytes = None) -> tuple[bool, str]:
    """Ajoute un nouveau mot de passe chiffré."""
    try:
        if user_key is None:
            raise ValueError("user_key manquant")

        conn = _get_connection()
        cur = conn.cursor()

        nonce = os.urandom(12)
        cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(clear_pwd.encode())
        payload = nonce + tag + ciphertext

        cur.execute("""
            INSERT INTO mots_de_passe
              (id_utilisateur, titre, identifiant, mot_de_passe_chiffre,
               site_web, notes, niveau_securite)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, title, ident, payload, site, notes, level))
        
        conn.commit()
        return True, "Mot de passe ajouté !"
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        if conn:
            conn.close()

def get_passwords(user_id: int, user_key: bytes) -> list[dict]:
    """Récupère tous les mots de passe d'un utilisateur."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, titre, identifiant, mot_de_passe_chiffre,
                   site_web, notes, niveau_securite, date_ajout
            FROM mots_de_passe
            WHERE id_utilisateur=%s
            ORDER BY date_ajout DESC
        """, (user_id,))
        
        result = []
        for pid, t, ident, payload, site, notes, lvl, date in cur.fetchall():
            try:
                nonce, tag, ct = payload[:12], payload[12:28], payload[28:]
                cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
                pwd = cipher.decrypt_and_verify(ct, tag).decode()
                result.append({
                    "id": pid,
                    "titre": t,
                    "identifiant": ident,
                    "password": pwd,
                    "site_web": site,
                    "notes": notes,
                    "niveau": lvl,
                    "date_ajout": date
                })
            except:
                continue
        return result
    finally:
        if conn:
            conn.close()

def update_password(entry_id: int, title: str, ident: str, new_clear_pwd: str,
                   site: str, notes: str, user_key: bytes) -> tuple[bool, str]:
    """Met à jour une entrée complète."""
    try:
        conn = _get_connection()
        cur = conn.cursor()

        nonce = os.urandom(12)
        cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(new_clear_pwd.encode())
        payload = nonce + tag + ciphertext
        
        level = verif_niveau_mdp(new_clear_pwd)

        cur.execute("""
            UPDATE mots_de_passe 
            SET titre=%s, identifiant=%s, mot_de_passe_chiffre=%s,
                site_web=%s, notes=%s, niveau_securite=%s
            WHERE id=%s
        """, (title, ident, payload, site, notes, level, entry_id))
        
        conn.commit()
        return True, "Mot de passe mis à jour."
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        if conn:
            conn.close()

def delete_password(entry_id: int) -> tuple[bool, str]:
    """Supprime un mot de passe."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM mots_de_passe WHERE id=%s", (entry_id,))
        conn.commit()
        return True, "Mot de passe supprimé."
    except Exception as e:
        return False, f"Erreur : {e}"
    finally:
        if conn:
            conn.close()

def search_passwords(user_id: int, query: str, user_key: bytes) -> list[dict]:
    """Recherche dans les mots de passe."""
    passwords = get_passwords(user_id, user_key)
    query_lower = query.lower()
    return [p for p in passwords if query_lower in p['titre'].lower() or 
            query_lower in p['identifiant'].lower() or 
            query_lower in p.get('site_web', '').lower()]