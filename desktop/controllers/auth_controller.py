# controllers/auth_controller.py
from models.database import Database

class AuthController:
    def __init__(self):
        pass  # Pas besoin d'initialiser Database ici
    
    def login(self, username: str, password: str) -> tuple[bool, dict|str]:
        """Gérer la connexion"""
        try:
            return Database.verify_login(username, password)
        except Exception as e:
            return False, f"Erreur de connexion : {str(e)}"
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """Gérer l'inscription"""
        try:
            return Database.create_account(username, password)
        except Exception as e:
            return False, f"Erreur lors de l'inscription : {str(e)}"