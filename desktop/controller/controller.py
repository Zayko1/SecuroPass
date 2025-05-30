# desktop/controller/controller.py

from model import model

class Controller:
    def __init__(self, model):
        self.model = model

    def connexion_controller(self, username: str, password: str, app) -> tuple[bool,str]:
        """
        Authentifie l'utilisateur, stocke user_id et user_key dans app,
        puis renvoie (True, message) ou (False, message).
        """
        ok, payload = self.model.verif_login(username, password)
        if not ok:
            return False, payload

        # payload est un dict {'user_key':..., 'user_id':...}
        app.user_key = payload["user_key"]
        app.user_id  = payload["user_id"]
        return True, "Connexion réussie"

    def creer_compte_controller(self, username: str, password: str) -> tuple[bool,str]:
        """
        Crée un compte : renvoie (True, msg) si OK, (False, msg) sinon.
        """
        if not username or not password:
            return False, "Veuillez remplir tous les champs."

        key = self.model.generate_key()
        ok, msg = self.model.create_account(username, password, key)
        return ok, msg

    def add_password_controller(self,
                                user_id: int,
                                title: str,
                                ident: str,
                                pwd: str,
                                site: str,
                                notes: str,
                                niveau: str,
                                user_key: bytes) -> tuple[bool,str]:
        """
        Ajoute un mot de passe : renvoie (True, msg) ou (False, msg).
        """
        ok, msg = self.model.add_password(
            user_id, title, ident, pwd, site, notes, niveau, user_key
        )
        return ok, msg

    def get_passwords_controller(self,
                                 user_id: int,
                                 user_key: bytes) -> list[dict]:
        """
        Récupère et renvoie la liste des mots de passe décryptés.
        """
        return self.model.get_passwords(user_id, user_key)

    def update_password_controller(self,
                                   entry_id: int,
                                   new_pwd: str,
                                   user_key: bytes) -> tuple[bool,str]:
        """
        Met à jour un mot de passe existant : renvoie (True, msg) ou (False, msg).
        """
        ok, msg = self.model.update_password(entry_id, new_pwd, user_key)
        return ok, msg

    def delete_password_controller(self, entry_id: int) -> tuple[bool,str]:
        """
        Supprime un mot de passe : renvoie (True, msg) ou (False, msg).
        """
        ok, msg = self.model.delete_password(entry_id)
        return ok, msg

    def update_entry_controller(self,
                                entry_id: int,
                                title: str,
                                ident: str,
                                pwd: str,
                                note: str,
                                user_key: bytes) -> tuple[bool,str]:
        """
        Met à jour titre/identifiants/mot de passe/note.
        """
        # 1) mise à jour du mot de passe chiffré
        ok, msg = self.model.update_password(entry_id, pwd, user_key)
        if not ok:
            return False, msg

        # 2) mise à jour du reste des métadonnées
        ok2, msg2 = self.model.update_entry(entry_id, title, ident, note)
        if not ok2:
            return False, msg2

        return True, "Entrée mise à jour."