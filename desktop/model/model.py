# desktop/model/model.py

import os
import string
import random
import re
from dotenv import load_dotenv, find_dotenv
import mysql.connector
from mysql.connector import Error
import bcrypt
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

# ─── Chargement des variables d’environnement ──────────────────────────────────
load_dotenv(find_dotenv())
DB_HOST     = os.environ["DB_HOST"]
DB_USER     = os.environ["DB_USER"]
DB_PORT     = int(os.environ["DB_PORT"])
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME     = os.environ["DB_NAME"]

db_config = {
    "host":     DB_HOST,
    "user":     DB_USER,
    "port":     DB_PORT,
    "password": DB_PASSWORD,
    "database": DB_NAME
}

def _get_connection():
    """Ouvre une connexion MySQL avec la config."""
    return mysql.connector.connect(**db_config)


# ─── Gestion du compte maître ─────────────────────────────────────────────────

def create_account(username: str, password: str, user_key: bytes) -> tuple[bool,str]:
    """
    Crée un compte :
      - hash bcrypt du mot de passe
      - dérivation PBKDF2 du mot de passe pour chiffrer user_key
      - AES-GCM de user_key (nonce 12 octets) → encrypted_key
      - INSERT (username, mot_de_passe_hash, cle_chiffrement, kdf_salt, nonce, tag, encrypted_key)
    """
    try:
        conn = _get_connection()
        cur  = conn.cursor()

        # unicité
        cur.execute("SELECT 1 FROM cles_maitres WHERE username=%s", (username,))
        if cur.fetchone():
            return False, "L'utilisateur existe déjà."

        # 1) hash bcrypt
        pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

        # 2) dérivation PBKDF2 pour la clé de chiffrement
        kdf_salt = os.urandom(16)
        enc_key  = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)

        # 3) chiffrement AES-GCM de user_key (nonce 12 octets)
        nonce          = os.urandom(12)
        cipher         = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(user_key)

        # 4) INSERT en base, en réinjectant cle_chiffrement pour le fallback
        cur.execute("""
            INSERT INTO cles_maitres
              (username,
               mot_de_passe_hash,
               cle_chiffrement,
               kdf_salt,
               nonce,
               tag,
               encrypted_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            username,
            pwd_hash,
            user_key,    # ON STOCKE la clé claire ici
            kdf_salt,
            nonce,
            tag,
            ciphertext
        ))
        conn.commit()
        return True, "Compte créé avec succès."
    except Error as e:
        return False, f"Erreur BDD (create_account) : {e}"
    finally:
        conn.close()

def verif_login(username: str, password: str) -> tuple[bool,dict|str]:
    """
    Vérifie login et déchiffre la clé utilisateur :
      - on récupère id, mot_de_passe_hash, cle_chiffrement (clear), kdf_salt, nonce, tag, encrypted_key
      - si bcrypt OK, on tente decrypt GCM
      - fallback : si tag invalide, on renvoie la valeur clear dans cle_chiffrement
    """
    try:
        conn = _get_connection()
        cur  = conn.cursor()
        cur.execute("""
           SELECT id,
                  mot_de_passe_hash,
                  cle_chiffrement,
                  kdf_salt,
                  nonce,
                  tag,
                  encrypted_key
             FROM cles_maitres
            WHERE username=%s
        """, (username,))
        row = cur.fetchone()
        if not row:
            return False, "Utilisateur non trouvé."

        user_id, stored_hash, clear_key, kdf_salt, nonce, tag, ciphertext = row

        # 1) bcrypt
        if not bcrypt.checkpw(password.encode(), stored_hash.encode("utf-8")):
            return False, "Mot de passe incorrect."

        # 2) PBKDF2 puis AES-GCM
        enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
        cipher  = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
        try:
            user_key = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            # MAC check failed → on retombe sur la clé stockée en clair (legacy)
            user_key = clear_key

        return True, {"user_key": user_key, "user_id": user_id}

    except (Error, ValueError) as e:
        return False, f"Erreur connexion : {e}"
    finally:
        conn.close()


# ─── Fonctions utilitaires ───────────────────────────────────────────────────

def generate_key() -> bytes:
    """Génère une clé AES-256 (32 octets)."""
    return os.urandom(32)

def generate_password(length: int = 16) -> str:
    """Génère un mot de passe aléatoire sécurisé."""
    pool = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(random.choice(pool) for _ in range(length))

def verif_niveau_mdp(mdp: str) -> str:
    """Évalue la force d’un mot de passe."""
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


# ─── CRUD des mots de passe utilisateur ───────────────────────────────────────

def add_password(user_id: int,
                 title: str,
                 ident: str,
                 clear_pwd: str,
                 site: str = "",
                 notes: str = "",
                 level: str = "",
                 user_key: bytes = None) -> tuple[bool,str]:
    """
    Chiffre clear_pwd avec user_key (AES-GCM nonce 12 octets)
    et insère une nouvelle ligne dans mots_de_passe.
    """
    try:
        if user_key is None:
            raise ValueError("user_key manquant pour le chiffrement")

        conn = _get_connection()
        cur  = conn.cursor()

        nonce      = os.urandom(12)
        cipher     = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(clear_pwd.encode())
        payload    = nonce + tag + ciphertext

        cur.execute("""
            INSERT INTO mots_de_passe
              (id_utilisateur,
               titre,
               identifiant,
               mot_de_passe_chiffre,
               site_web,
               notes,
               niveau_securite)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, title, ident, payload, site, notes, level))
        conn.commit()
        return True, "Mot de passe ajouté !"
    except Exception as e:
        conn.rollback()
        return False, f"Erreur BDD (add_password) : {e}"
    finally:
        conn.close()


def get_passwords(user_id: int, user_key: bytes) -> list[dict]:
    """
    Récupère et déchiffre tous les mots de passe pour un utilisateur.
    """
    try:
        conn = _get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, titre, identifiant, mot_de_passe_chiffre,
                   site_web, notes, niveau_securite, date_ajout
              FROM mots_de_passe
             WHERE id_utilisateur=%s
          ORDER BY date_ajout DESC
        """, (user_id,))
        result = []
        for pid, t, ident, payload, site, notes, lvl, date in cur.fetchall():
            nonce, tag, ct = payload[:12], payload[12:28], payload[28:]
            cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
            pwd    = cipher.decrypt_and_verify(ct, tag).decode()
            result.append({
                "id":           pid,
                "titre":        t,
                "identifiant":  ident,
                "password":     pwd,
                "site_web":     site,
                "notes":        notes,
                "niveau":       lvl,
                "date_ajout":   date
            })
        return result
    finally:
        conn.close()


def update_password(entry_id: int,
                    new_clear_pwd: str,
                    user_key: bytes) -> tuple[bool,str]:
    """
    Ré-encrypte new_clear_pwd avec user_key (AES-GCM nonce 12 octets)
    et met à jour l’entry.
    """
    try:
        conn = _get_connection()
        cur  = conn.cursor()

        nonce      = os.urandom(12)
        cipher     = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(new_clear_pwd.encode())
        payload    = nonce + tag + ciphertext

        cur.execute(
            "UPDATE mots_de_passe SET mot_de_passe_chiffre=%s WHERE id=%s",
            (payload, entry_id)
        )
        conn.commit()
        return True, "Mot de passe mis à jour."
    except Exception as e:
        conn.rollback()
        return False, f"Erreur BDD (update_password) : {e}"
    finally:
        conn.close()


def delete_password(entry_id: int) -> tuple[bool,str]:
    """Supprime l’entrée mots_de_passe d’ID entry_id."""
    try:
        conn = _get_connection()
        cur  = conn.cursor()
        cur.execute("DELETE FROM mots_de_passe WHERE id=%s", (entry_id,))
        conn.commit()
        return True, "Mot de passe supprimé."
    except Exception as e:
        conn.rollback()
        return False, f"Erreur BDD (delete_password) : {e}"
    finally:
        conn.close()

def update_entry(entry_id: int,
                 title: str,
                 ident: str,
                 note: str) -> tuple[bool,str]:
    """
    Met à jour titre, identifiant et notes d'une entrée mots_de_passe.
    """
    try:
        conn = _get_connection()
        cur  = conn.cursor()
        cur.execute("""
            UPDATE mots_de_passe
               SET titre=%s,
                   identifiant=%s,
                   notes=%s
             WHERE id=%s
        """, (title, ident, note, entry_id))
        conn.commit()
        return True, "Métadonnées mises à jour."
    except Error as e:
        conn.rollback()
        return False, f"Erreur BDD (update_entry) : {e}"
    finally:
        conn.close()