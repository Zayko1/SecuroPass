#controller>controller.py
from model import model
from tkinter import messagebox
import customtkinter as ctk

class Controller:
    def __init__(self, model):
        self.model = model

    def connexion_controller(self, username, password, app):
        # model.verif_login renvoie (bool, message_ou_user_key)
        ok, result = self.model.verif_login(username, password)

        if not ok:
            # en cas d’erreur, renvoyez une chaîne "error::…"
            return False, result

        # en cas de succès, result est la user_key
        app.user_key = result
        return True, result
    
    def creer_compte_controller(self, username, password):
        """
        Renvoie (True, msg) si le compte est créé,
        ou (False, msg) sinon.
        """
        # 1) validation simple
        if not username or not password:
            return False, "Veuillez remplir tous les champs."

        # 2) génération de la clé de chiffrement
        key = self.model.generate_key()

        # 3) appel au modèle
        result = self.model.create_account(username, password, key)

        # 4) interprétation du message
        if "succès" in result.lower():
            return True, result
        else:
            return False, result




"""
def creer_compte_controller(username, password):
    if not username or not password:
        messagebox.showwarning("Erreur", "Veuillez remplir tous les champs.")
        return

    # On génère une clé de chiffrement sécurisée
    key = model.generate_key()

    result = model.create_account(username, password, key)

    if result == "L'utilisateur existe déjà.":
        messagebox.showerror("Erreur", "Ce nom d'utilisateur est déjà pris.")
    elif result == "Compte créé avec succès.":
        messagebox.showinfo("Succès", "Compte créé avec succès !")
    elif result.startswith("Erreur"):
        messagebox.showerror("Erreur", result)

def retour_accueil(app_actuel):
    app_actuel.destroy()
    new_app = ctk.CTk()
    MainPage(new_app)
    new_app.mainloop()
"""