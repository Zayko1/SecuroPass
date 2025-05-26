#view> gui.py

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
        self.show()
        
    def show(self):
        # Vide tous les widgets précédents
        for widget in self.app.winfo_children():
            widget.destroy()

        # Widgets de la page d'accueil
        ctk.CTkLabel(self.app, text="Bienvenue sur SécuroPass", font=("Arial", 20)).pack(pady=30)

        ctk.CTkButton(
            self.app,
            text="Se connecter",
            width=250,
            command=self.se_connecter
        ).pack(pady=10)

        ctk.CTkButton(
            self.app,
            text="Créer un compte",
            width=250,
            command=self.creer_compte
        ).pack(pady=10)

    def se_connecter(self):
        # On vide la fenêtre et on y affiche la page de connexion
        for widget in self.app.winfo_children():
            widget.destroy()
        ConnexionPage(self.app)


    def creer_compte(self):
        # On vide la fenêtre et on y affiche la page de création
        for widget in self.app.winfo_children():
            widget.destroy()
        CreationComptePage(self.app)
