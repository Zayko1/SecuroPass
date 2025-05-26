# view/create_account.py

import customtkinter as ctk
from tkinter import messagebox
from controller.controller import Controller
import model.model as model_module

class CreationComptePage:
    def __init__(self, app):
        self.app = app
        # 1) on instancie le controller
        self.controller = Controller(model_module)

        self.app.title("SécuroPass - Création du compte")
        self.app.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self.app, text="Nom d'utilisateur").pack(pady=10)
        self.entry_username = ctk.CTkEntry(self.app, width=250)
        self.entry_username.pack(pady=5)

        ctk.CTkLabel(self.app, text="Mot de passe").pack(pady=10)
        self.entry_password = ctk.CTkEntry(self.app, show="*", width=250)
        self.entry_password.pack(pady=5)

        # 2) on assigne bien l'attribut self.btn_creer
        self.btn_creer = ctk.CTkButton(
            self.app,
            text="Créer le compte",
            width=250,
            command=self.creer_compte
        )
        self.btn_creer.pack(pady=20)

        # 3) idem pour annuler, on retourne à la page principale
        self.btn_annuler = ctk.CTkButton(
            self.app,
            text="Annuler",
            width=250,
            fg_color="red",
            command=self.app.show_main
        )
        self.btn_annuler.pack(pady=20)

    def creer_compte(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        # 4) on appelle le controller et on s'attend à (ok, msg)
        ok, msg = self.controller.creer_compte_controller(username, password)

        if not ok:
            messagebox.showerror("Erreur création", msg, parent=self.app)
            return

        messagebox.showinfo("Succès", msg, parent=self.app)
        # 5) on revient à l'accueil
        self.app.show_main()
