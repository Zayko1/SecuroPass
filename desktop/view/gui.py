import customtkinter as ctk
from tkinter import messagebox
from view.connexion import ConnexionPage
from view.create_account import CreationComptePage
ctk.set_appearance_mode("dark")  # Thème sombre

class MainPage:
    def __init__(self, app):
        self.app = app
        self.app.title("SécuroPass")
        self.app.geometry("400x300")
        
        self.create_widgets()

    def create_widgets(self):
        # Titre de la page principale
        ctk.CTkLabel(self.app, text="Bienvenue sur SécuroPass", font=("Arial", 20)).pack(pady=30)

        # Bouton pour se connecter
        btn_se_connecter = ctk.CTkButton(self.app, text="Se connecter", width=250, command=self.se_connecter)
        btn_se_connecter.pack(pady=10)

        # Bouton pour créer un compte
        btn_creer_compte = ctk.CTkButton(self.app, text="Créer un compte", width=250, command=self.creer_compte)
        btn_creer_compte.pack(pady=10)

    def se_connecter(self):
        # Rediriger vers la page de connexion
        self.app.destroy()  # Fermer la page actuelle
        new_app = ctk.CTk()  # Créer une nouvelle instance pour la page de connexion
        ConnexionPage(new_app)
        new_app.mainloop()

    def creer_compte(self):
        # Rediriger vers la page de création du compte
        self.app.destroy()  # Fermer la page actuelle
        new_app = ctk.CTk()  # Créer une nouvelle instance pour la page de création du compte
        CreationComptePage(new_app)
        new_app.mainloop()
