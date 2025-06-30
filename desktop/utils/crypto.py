# ==================== utils/crypto.py ====================
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import bcrypt

class Crypto:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe avec bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Vérifier un mot de passe contre son hash"""
        return bcrypt.checkpw(password.encode(), hashed.encode("utf-8"))
    
    @staticmethod
    def generate_key() -> bytes:
        """Générer une clé AES-256"""
        return os.urandom(32)
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Dériver une clé à partir du mot de passe"""
        return PBKDF2(password, salt, dkLen=32, count=200_000)
    
    @staticmethod
    def encrypt_password(password: str, key: bytes) -> tuple[bytes, bytes, bytes]:
        """Chiffrer un mot de passe avec AES-GCM"""
        nonce = os.urandom(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode())
        return nonce, tag, ciphertext
    
    @staticmethod
    def decrypt_password(payload: bytes, key: bytes) -> str:
        """Déchiffrer un mot de passe"""
        nonce, tag, ciphertext = payload[:12], payload[12:28], payload[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()