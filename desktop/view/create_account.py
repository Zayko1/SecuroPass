#view>create_account.py
import customtkinter as ctk
from controller import controller
class CreationComptePage:
    def __init__(self, app):
        self.app = app
        self.app.title("SécuroPass - Création du compte")
        self.app.geometry("400x300")
        
        self.create_widgets()

    def create_widgets(self):
        # Label et champs de texte pour le nom d'utilisateur
        ctk.CTkLabel(self.app, text="Nom d'utilisateur").pack(pady=10)
        self.entry_username = ctk.CTkEntry(self.app, width=250)
        self.entry_username.pack(pady=5)

        # Label et champs de texte pour le mot de passe
        ctk.CTkLabel(self.app, text="Mot de passe").pack(pady=10)
        self.entry_password = ctk.CTkEntry(self.app, show="*", width=250)
        self.entry_password.pack(pady=5)

        # Bouton pour créer le compte
        self.btn_creer = ctk.CTkButton(self.app, text="Créer le compte", width=250, command=self.creer_compte)
        self.btn_creer.pack(pady=20)

        # Bouton pour annuler
        self.btn_annuler = ctk.CTkButton(self.app, text="Annuler", width=250, command=lambda: controller.retour_accueil(self.app), fg_color="red")
        self.btn_annuler.pack(pady=20)

    def creer_compte(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        from controller import controller
        controller.creer_compte_controller(username, password)



