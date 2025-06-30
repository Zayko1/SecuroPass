# ==================== controllers/password_controller.py ====================
from models.database import Database

class PasswordController:
    def __init__(self, user_data):
        self.user_data = user_data
        self.db = Database()
    
    def get_all_passwords(self) -> list[dict]:
        """Récupérer tous les mots de passe"""
        return self.db.get_passwords(
            self.user_data['user_id'],
            self.user_data['user_key']
        )
    
    def add_password(self, title: str, identifier: str, password: str,
                    site: str = "", notes: str = "") -> tuple[bool, str]:
        """Ajouter un mot de passe"""
        return self.db.add_password(
            self.user_data['user_id'],
            title,
            identifier,
            password,
            site,
            notes,
            self.user_data['user_key']
        )
    
    def update_password(self, entry_id: int, title: str, identifier: str,
                       password: str, site: str = "", notes: str = "") -> tuple[bool, str]:
        """Mettre à jour un mot de passe"""
        return self.db.update_password(
            entry_id,
            title,
            identifier,
            password,
            site,
            notes,
            self.user_data['user_key']
        )
    
    def delete_password(self, entry_id: int) -> tuple[bool, str]:
        """Supprimer un mot de passe"""
        return self.db.delete_password(entry_id)