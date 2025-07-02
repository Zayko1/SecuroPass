# models/database.py
import os
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from datetime import datetime
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

    @staticmethod
    def change_username(user_id: int, current_username: str, password: str, new_username: str) -> tuple[bool, str]:
        """Changer le nom d'utilisateur"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            # Debug
            print(f"Debug change_username: user_id={user_id}, current_username={current_username}, new_username={new_username}")
            
            # Vérifier que le nouveau nom d'utilisateur n'existe pas déjà
            query1 = "SELECT 1 FROM cles_maitres WHERE username=%s AND id!=%s"
            params1 = (new_username, user_id)
            print(f"Query1: {query1}")
            print(f"Params1: {params1}")
            cur.execute(query1, params1)
            
            if cur.fetchone():
                return False, "Ce nom d'utilisateur est déjà pris."
            
            # Vérifier le mot de passe actuel
            query2 = "SELECT mot_de_passe_hash FROM cles_maitres WHERE id=%s"
            params2 = (user_id,)
            print(f"Query2: {query2}")
            print(f"Params2: {params2}")
            cur.execute(query2, params2)
            
            row = cur.fetchone()
            if not row:
                return False, "Utilisateur non trouvé."
            
            stored_hash = row[0]
            if not bcrypt.checkpw(password.encode(), stored_hash.encode("utf-8")):
                return False, "Mot de passe incorrect."
            
            # Mettre à jour le nom d'utilisateur
            query3 = "UPDATE cles_maitres SET username=%s WHERE id=%s"
            params3 = (new_username, user_id)
            print(f"Query3: {query3}")
            print(f"Params3: {params3}")
            cur.execute(query3, params3)
            
            conn.commit()
            return True, "Nom d'utilisateur modifié avec succès!"
            
        except Exception as e:
            print(f"Erreur dans change_username: {e}")
            if conn:
                conn.rollback()
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def change_password(user_id: int, username: str, current_password: str, new_password: str) -> tuple[bool, str]:
        """Changer le mot de passe de l'utilisateur"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            print(f"Debug change_password: user_id={user_id}, username={username}")
            
            # Récupérer les informations actuelles - requête simplifiée
            query = "SELECT mot_de_passe_hash, cle_chiffrement, kdf_salt, nonce, tag, encrypted_key FROM cles_maitres WHERE id=%s"
            params = (user_id,)
            print(f"Query: {query}")
            print(f"Params: {params}")
            cur.execute(query, params)
            
            row = cur.fetchone()
            if not row:
                return False, "Utilisateur non trouvé."
            
            mot_de_passe_hash = row[0]
            cle_chiffrement = row[1]
            kdf_salt = row[2]
            nonce = row[3]
            tag = row[4]
            encrypted_key = row[5]
            
            # Vérifier l'ancien mot de passe
            if not bcrypt.checkpw(current_password.encode(), mot_de_passe_hash.encode("utf-8")):
                return False, "Mot de passe actuel incorrect."
            
            # Récupérer la clé utilisateur
            try:
                if kdf_salt and nonce and tag and encrypted_key:
                    enc_key = PBKDF2(current_password, kdf_salt, dkLen=32, count=200_000)
                    cipher = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
                    user_key = cipher.decrypt_and_verify(encrypted_key, tag)
                else:
                    user_key = cle_chiffrement
            except Exception as e:
                print(f"Erreur déchiffrement, utilisation clé de secours: {e}")
                user_key = cle_chiffrement
            
            # Créer le nouveau hash
            new_pwd_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode("utf-8")
            
            # Re-chiffrer la clé utilisateur avec le nouveau mot de passe
            new_kdf_salt = os.urandom(16)
            new_enc_key = PBKDF2(new_password, new_kdf_salt, dkLen=32, count=200_000)
            
            new_nonce = os.urandom(12)
            new_cipher = AES.new(new_enc_key, AES.MODE_GCM, nonce=new_nonce)
            new_ciphertext, new_tag = new_cipher.encrypt_and_digest(user_key)
            
            # Mettre à jour en base
            update_query = "UPDATE cles_maitres SET mot_de_passe_hash=%s, kdf_salt=%s, nonce=%s, tag=%s, encrypted_key=%s WHERE id=%s"
            update_params = (new_pwd_hash, new_kdf_salt, new_nonce, new_tag, new_ciphertext, user_id)
            print(f"Update query: {update_query}")
            print(f"Update params count: {len(update_params)}")
            cur.execute(update_query, update_params)
            
            conn.commit()
            return True, "Mot de passe modifié avec succès!"
            
        except Exception as e:
            print(f"Erreur dans change_password: {e}")
            if conn:
                conn.rollback()
            return False, f"Erreur : {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_user_stats(user_id: int) -> dict:
        """Obtenir les statistiques de l'utilisateur"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            stats = {}
            
            # Date de création du compte
            cur.execute("SELECT date_creation FROM cles_maitres WHERE id=%s", (user_id,))
            row = cur.fetchone()
            if row:
                stats['created_date'] = row[0].strftime("%d/%m/%Y") if row[0] else "N/A"
            
            # Total de mots de passe
            cur.execute("SELECT COUNT(*) FROM mots_de_passe WHERE id_utilisateur=%s", (user_id,))
            row = cur.fetchone()
            stats['total_passwords'] = row[0] if row else 0
            
            # Répartition par force
            cur.execute("""
                SELECT niveau_securite, COUNT(*) as count 
                FROM mots_de_passe 
                WHERE id_utilisateur=%s 
                GROUP BY niveau_securite
            """, (user_id,))
            
            strength_map = {
                'Très Fort': 'very_strong',
                'Fort': 'strong',
                'Moyen': 'medium',
                'Faible': 'weak'
            }
            
            stats.update({
                'very_strong': 0,
                'strong': 0,
                'medium': 0,
                'weak': 0
            })
            
            for row in cur.fetchall():
                niveau = row[0]
                count = row[1]
                if niveau in strength_map:
                    stats[strength_map[niveau]] = count
            
            # Sites les plus utilisés
            cur.execute("""
                SELECT site_web, COUNT(*) as count 
                FROM mots_de_passe 
                WHERE id_utilisateur=%s AND site_web IS NOT NULL AND site_web != ''
                GROUP BY site_web 
                ORDER BY count DESC 
                LIMIT 5
            """, (user_id,))
            
            stats['top_sites'] = [(row[0], row[1]) for row in cur.fetchall()]
            
            # Dernier mot de passe ajouté
            cur.execute("""
                SELECT date_ajout 
                FROM mots_de_passe 
                WHERE id_utilisateur=%s 
                ORDER BY date_ajout DESC 
                LIMIT 1
            """, (user_id,))
            
            row = cur.fetchone()
            if row and row[0]:
                stats['last_added'] = row[0].strftime("%d/%m/%Y %H:%M")
            else:
                stats['last_added'] = "Aucun"
            
            return stats
            
        except Exception as e:
            print(f"Erreur lors de la récupération des stats : {e}")
            return {
                'created_date': 'N/A',
                'total_passwords': 0,
                'very_strong': 0,
                'strong': 0,
                'medium': 0,
                'weak': 0,
                'top_sites': [],
                'last_added': 'Aucun'
            }
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def check_login_attempts(username: str) -> tuple[bool, int, str]:
        """
        Vérifier si l'utilisateur peut tenter de se connecter
        Retourne (peut_essayer, tentatives_restantes, message)
        """
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            # Nettoyer les anciennes tentatives (plus de 3 minutes)
            cur.execute("""
                DELETE FROM login_attempts 
                WHERE username=%s AND attempt_time < DATE_SUB(NOW(), INTERVAL 3 MINUTE)
            """, (username,))
            conn.commit()
            
            # Compter les tentatives échouées dans les 3 dernières minutes
            cur.execute("""
                SELECT COUNT(*) 
                FROM login_attempts 
                WHERE username=%s 
                AND success=FALSE 
                AND attempt_time >= DATE_SUB(NOW(), INTERVAL 3 MINUTE)
            """, (username,))
            
            failed_attempts = cur.fetchone()[0]
            
            if failed_attempts >= 5:
                # Calculer le temps restant avant de pouvoir réessayer
                cur.execute("""
                    SELECT TIMESTAMPDIFF(SECOND, NOW(), DATE_ADD(MIN(attempt_time), INTERVAL 3 MINUTE))
                    FROM login_attempts 
                    WHERE username=%s 
                    AND success=FALSE 
                    AND attempt_time >= DATE_SUB(NOW(), INTERVAL 3 MINUTE)
                """, (username,))
                
                seconds_left = cur.fetchone()[0]
                if seconds_left and seconds_left > 0:
                    minutes = seconds_left // 60
                    seconds = seconds_left % 60
                    return False, 0, f"Trop de tentatives échouées. Réessayez dans {minutes}m {seconds}s."
            
            tentatives_restantes = 5 - failed_attempts
            return True, tentatives_restantes, ""
            
        except Exception as e:
            print(f"Erreur check_login_attempts: {e}")
            return True, 5, ""  # En cas d'erreur, on laisse passer
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def record_login_attempt(username: str, success: bool, ip_address: str = None) -> None:
        """Enregistrer une tentative de connexion"""
        conn = None
        cur = None
        try:
            conn = Database.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO login_attempts (username, ip_address, success)
                VALUES (%s, %s, %s)
            """, (username, ip_address, success))
            
            conn.commit()
            
        except Exception as e:
            print(f"Erreur record_login_attempt: {e}")
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def verify_login(username: str, password: str) -> tuple[bool, dict|str]:
        """Vérifier les identifiants avec limitation des tentatives"""
        # D'abord vérifier si l'utilisateur peut tenter de se connecter
        can_try, attempts_left, message = Database.check_login_attempts(username)
        if not can_try:
            return False, message
        
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
                # Enregistrer la tentative échouée
                Database.record_login_attempt(username, False)
                if attempts_left > 1:
                    return False, f"Utilisateur non trouvé. ({attempts_left - 1} tentatives restantes)"
                else:
                    return False, "Utilisateur non trouvé. Prochaine tentative bloquera le compte pour 3 minutes."
            
            user_id, stored_hash, clear_key, kdf_salt, nonce, tag, ciphertext = row
            
            # Vérifier le mot de passe
            if not bcrypt.checkpw(password.encode(), stored_hash.encode("utf-8")):
                # Enregistrer la tentative échouée
                Database.record_login_attempt(username, False)
                if attempts_left > 1:
                    return False, f"Mot de passe incorrect. ({attempts_left - 1} tentatives restantes)"
                else:
                    return False, "Mot de passe incorrect. Prochaine tentative bloquera le compte pour 3 minutes."
            
            # Connexion réussie - enregistrer et nettoyer les tentatives
            Database.record_login_attempt(username, True)
            
            # Nettoyer toutes les tentatives échouées pour cet utilisateur
            conn2 = Database.get_connection()
            cur2 = conn2.cursor()
            cur2.execute("DELETE FROM login_attempts WHERE username=%s AND success=FALSE", (username,))
            conn2.commit()
            cur2.close()
            conn2.close()
            
            # Déchiffrer la clé utilisateur
            try:
                enc_key = PBKDF2(password, kdf_salt, dkLen=32, count=200_000)
                cipher = AES.new(enc_key, AES.MODE_GCM, nonce=nonce)
                user_key = cipher.decrypt_and_verify(ciphertext, tag)
            except:
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
