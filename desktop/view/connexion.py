import customtkinter as ctk
from tkinter import messagebox
from controller.controller import Controller, retour_accueil
import model.model as model_module   # on importe le module, pas une classe
from config import db_config         # charge .env et fallback pour db_config

class ConnexionPage:
    def __init__(self, app):
        self.app = app

        # Instancie le Controller en lui passant le module model_module
        # qui expose create_account(), verif_login(), etc.
        self.controller = Controller(model_module)

        self.app.title("SécuroPass - Connexion")
        self.app.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self.app, text="Nom d'utilisateur").pack(pady=10)
        self.entry_username = ctk.CTkEntry(self.app, width=250)
        self.entry_username.pack(pady=5)

        ctk.CTkLabel(self.app, text="Mot de passe").pack(pady=10)
        self.entry_password = ctk.CTkEntry(self.app, show="*", width=250)
        self.entry_password.pack(pady=5)

        self.btn_connexion = ctk.CTkButton(
            self.app,
            text="Se connecter",
            width=250,
            command=self.se_connecter
        )
        self.btn_connexion.pack(pady=20)

        self.btn_annuler = ctk.CTkButton(
            self.app,
            text="Annuler",
            width=250,
            fg_color="red",
            command=lambda: retour_accueil(self.app)
        )
        self.btn_annuler.pack(pady=20)

    def se_connecter(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        # appel et récupération du tuple (ok, payload)
        ok, payload = self.controller.connexion_controller(username, password, self.app)

        if not ok:
            messagebox.showerror("Erreur de connexion", payload, parent=self.app)
            return

        # succès : payload contient la clé utilisateur décryptée
        self.app.user_key = payload
        messagebox.showinfo("Connexion réussie", "Bienvenue !", parent=self.app)

        # bascule vers l'écran principal
        if hasattr(self.app, "show_home"):
            self.app.show_home()
