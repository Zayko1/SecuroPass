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

def connexion_controller(username, password, app):
    if not username or not password:
        messagebox.showwarning("Erreur", "Veuillez remplir tous les champs.")
        return

    result = model.verif_login(username, password)
    
    if result == "Connexion réussie":
        messagebox.showinfo("Bienvenue", "Connexion réussie !")
        # TODO : Rediriger vers la page principale après connexion
        app.destroy()
        # MainPage(app) ou redirection vers une interface utilisateur
    elif result == "Mot de passe incorrect":
        messagebox.showerror("Erreur", "Mot de passe incorrect.")
    elif result.startswith("error::"):
        messagebox.showerror("Erreur", f"Problème de connexion : {result.split('::')[1]}")
    else:
        messagebox.showerror("Erreur", result)