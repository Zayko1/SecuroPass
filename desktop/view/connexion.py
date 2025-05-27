import customtkinter as ctk
from tkinter import messagebox
from controller.controller import Controller
import model.model as model_module

class ConnexionPage:
    def __init__(self, app):
        self.app = app
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
            command=self.app.show_main
        )
        self.btn_annuler.pack(pady=20)

    def se_connecter(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        # Récupère (ok, msg) : le contrôleur a déjà stocké user_key et user_id
        ok, msg = self.controller.connexion_controller(username, password, self.app)

        if not ok:
            messagebox.showerror("Erreur de connexion", msg, parent=self.app)
            return

        # Succès
        messagebox.showinfo("Connexion réussie", msg, parent=self.app)
        # Bascule vers l'écran principal
        self.app.show_home()
