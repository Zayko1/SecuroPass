from model import model
from tkinter import messagebox

def creer_compte_controller(username, password):
    if not username or not password:
        messagebox.showwarning("Erreur", "Veuillez remplir tous les champs.")
        return

    result = model.enregistrer_compte(username, password)
    
    if result == "exists":
        messagebox.showerror("Erreur", "Ce nom d'utilisateur est déjà pris.")
    elif result == "success":
        messagebox.showinfo("Succès", "Compte créé avec succès !")
    elif result.startswith("error::"):
        messagebox.showerror("Erreur", f"Problème de connexion : {result.split('::')[1]}")
