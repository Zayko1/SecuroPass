#controller>controller.py
from model import model
from tkinter import messagebox
import customtkinter as ctk

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

class Controller:
    def __init__(self, model):
        self.model = model

    def connexion_controller(self, username, password, app):
        # model.verif_login renvoie (bool, message_ou_user_key)
        ok, payload = self.model.verif_login(username, password)

        if not ok:
            # en cas d’erreur, renvoyez une chaîne "error::…"
            return f"error::{payload}"

        # en cas de succès, payload est la user_key décryptée
        app.user_key = payload

        # vous pouvez soit renvoyer "OK", soit un message personnalisé
        return "OK"
