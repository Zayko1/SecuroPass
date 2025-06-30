# models/database.py
import os
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import bcrypt
import string
import random
import re

class Database:
    @staticmethod
    def get_connection():
        """Obtenir une connexion à la base de données"""
        return mysql.connector.connect(**DB_CONFIG)
    
    @staticmethod
    def create_account(username: str, password: str) -> tuple[bool, str]:
        """Créer un compte utilisateur"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            # Vérifier si l'utilisateur existe
            cur.execute("SELECT 1 FROM cles_maitres WHERE username=%s", (username,))
            if cur.fetchone():
                return False, "L'utilisateur existe déjà."
            
            # Créer le compte
            pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
            user_key = os.urandom(32)  # Clé AES-256
            
            # Chiffrer la clé utilisateur
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
            return True, "Compte créé avec succès!"
            
        except Error as e:
            return False, f"Erreur de base de données : {str(e)}"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def verify_login(username: str, password: str) -> tuple[bool, dict|str]:
        """Vérifier les identifiants"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, mot_de_passe_hash, cle_chiffrement, kdf_salt, nonce, tag, encrypted_key
                FROM cles_maitres WHERE username=%s
            """, (username,))
            
            row = cur.fetchone()
            if not row:
                return False, "Utilisateur non trouvé."
            
            user_id, stored_hash, clear_key, kdf_salt, nonce, tag, ciphertext = row
            
            # Vérifier le mot de passe
            if not bcrypt.checkpw(password.encode(), stored_hash.encode("utf-8")):
                return False, "Mot de passe incorrect."
            
            # Déchiffrer la clé utilisateur
            try:
                enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
                cipher = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
                user_key = cipher.decrypt_and_verify(ciphertext, tag)
            except:
                # Fallback sur la clé en clair si le déchiffrement échoue
                user_key = clear_key
            
            return True, {
                "user_id": user_id,
                "username": username,
                "user_key": user_key
            }
            
        except Error as e:
            return False, f"Erreur de connexion à la base de données : {str(e)}"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def get_passwords(user_id: int, user_key: bytes) -> list[dict]:
        """Récupérer tous les mots de passe d'un utilisateur"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, titre, identifiant, mot_de_passe_chiffre,
                       site_web, notes, niveau_securite, date_ajout
                FROM mots_de_passe
                WHERE id_utilisateur=%s
                ORDER BY date_ajout DESC
            """, (user_id,))
            
            passwords = []
            for row in cur.fetchall():
                try:
                    pwd_id, title, ident, payload, site, notes, level, date = row
                    
                    # Déchiffrer le mot de passe
                    nonce, tag, ciphertext = payload[:12], payload[12:28], payload[28:]
                    cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
                    decrypted = cipher.decrypt_and_verify(ciphertext, tag).decode()
                    
                    passwords.append({
                        "id": pwd_id,
                        "titre": title,
                        "identifiant": ident,
                        "password": decrypted,
                        "site_web": site or "",
                        "notes": notes or "",
                        "niveau": level or "Inconnu",
                        "date_ajout": date
                    })
                except Exception as e:
                    print(f"Erreur lors du déchiffrement d'un mot de passe : {e}")
                    continue
            
            return passwords
            
        except Error as e:
            print(f"Erreur de base de données : {e}")
            return []
        except Exception as e:
            print(f"Erreur : {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def add_password(user_id: int, title: str, identifier: str, password: str,
                    site: str = "", notes: str = "", user_key: bytes = None) -> tuple[bool, str]:
        """Ajouter un mot de passe"""
        conn = None
        cur = None
        try:
            if not user_key:
                return False, "Clé utilisateur manquante"
            
            conn = Database.get_connection()
            cur = conn.cursor()
            
            # Chiffrer le mot de passe
            nonce = os.urandom(12)
            cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(password.encode())
            payload = nonce + tag + ciphertext
            
            # Évaluer la force
            level = Database.check_password_strength(password)
            
            cur.execute("""
                INSERT INTO mots_de_passe
                (id_utilisateur, titre, identifiant, mot_de_passe_chiffre,
                 site_web, notes, niveau_securite)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, title, identifier, payload, site, notes, level))
            
            conn.commit()
            return True, "Mot de passe ajouté avec succès!"
            
        except Error as e:
            return False, f"Erreur de base de données : {str(e)}"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def update_password(entry_id: int, title: str, identifier: str, password: str,
                       site: str, notes: str, user_key: bytes) -> tuple[bool, str]:
        """Mettre à jour un mot de passe"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            # Chiffrer le nouveau mot de passe
            nonce = os.urandom(12)
            cipher = AES.new(user_key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(password.encode())
            payload = nonce + tag + ciphertext
            
            level = Database.check_password_strength(password)
            
            cur.execute("""
                UPDATE mots_de_passe
                SET titre=%s, identifiant=%s, mot_de_passe_chiffre=%s,
                    site_web=%s, notes=%s, niveau_securite=%s
                WHERE id=%s
            """, (title, identifier, payload, site, notes, level, entry_id))
            
            conn.commit()
            return True, "Mot de passe mis à jour!"
            
        except Error as e:
            return False, f"Erreur de base de données : {str(e)}"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def delete_password(entry_id: int) -> tuple[bool, str]:
        """Supprimer un mot de passe"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM mots_de_passe WHERE id=%s", (entry_id,))
            conn.commit()
            
            return True, "Mot de passe supprimé!"
            
        except Error as e:
            return False, f"Erreur de base de données : {str(e)}"
        except Exception as e:
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()
    
    @staticmethod
    def generate_password(length: int = 16, include_lower=True, include_upper=True,
                         include_digits=True, include_special=True) -> str:
        """Générer un mot de passe aléatoire"""
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
        
        # Assurer qu'au moins un caractère de chaque type demandé est présent
        password = []
        if include_lower and string.ascii_lowercase:
            password.append(random.choice(string.ascii_lowercase))
        if include_upper and string.ascii_uppercase:
            password.append(random.choice(string.ascii_uppercase))
        if include_digits and string.digits:
            password.append(random.choice(string.digits))
        if include_special:
            password.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        # Compléter avec des caractères aléatoires
        for _ in range(length - len(password)):
            password.append(random.choice(pool))
        
        # Mélanger
        random.shuffle(password)
        return ''.join(password)
    
    @staticmethod
    def check_password_strength(password: str) -> str:
        """Évaluer la force d'un mot de passe"""
        if not password:
            return "Très faible"
        
        if len(password) < 8:
            return "Faible"
        
        score = 0
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        if score < 2:
            return "Faible"
        elif score < 4:
            return "Moyen"
        elif score < 5:
            return "Fort"
        else:
            return "Très Fort"