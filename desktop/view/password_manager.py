#view/password_manager.py
import customtkinter as ctk
from tkinter import ttk
import string

class PwdManagementPage:
    def __init__(self, app):
        self.app = app  # content_frame du HomeApp
        self.entries = []  # Données locales ou à remplacer par la BDD
        self.create_widgets()

    def create_widgets(self):
        # Titre
        ctk.CTkLabel(self.app, text="🔐 Gestionnaire de mots de passe", font=("Arial", 20)).pack(pady=(10, 5))

        # Bouton Ajouter
        btn_ajouter = ctk.CTkButton(
            self.app,
            text="+ Ajouter un mot de passe",
            fg_color="#1f6aa5",
            hover_color="#155a8a",
            text_color="white",
            font=("Arial", 14, "bold"),
            command=self.afficher_formulaire_popup
        )
        btn_ajouter.pack(pady=10)

        # Tableau
        self.tree = ttk.Treeview(self.app, columns=("Titre", "Identifiant", "Site", "Mot de passe"), show="headings")
        for col in ("Titre", "Identifiant", "Site", "Mot de passe"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=20, expand=True, fill="both")

    def afficher_formulaire_popup(self):
        self.popup = ctk.CTkToplevel(self.app)
        self.popup.title("Ajouter un mot de passe")
        self.popup.geometry("400x350")

        # Champs
        labels = ["Titre", "Identifiant", "Site Web", "Mot de passe"]
        self.entries_form = {}
        for idx, label in enumerate(labels):
            ctk.CTkLabel(self.popup, text=f"{label} :").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self.popup, width=200, show="*" if label == "Mot de passe" else None)
            entry.grid(row=idx, column=1, pady=5)
            self.entries_form[label.lower()] = entry

        # Barre de sécurité
        self.security_bar = ctk.CTkProgressBar(self.popup, width=200)
        self.security_bar.grid(row=4, column=1, pady=10, sticky="w")
        self.security_bar.set(0)

        self.entries_form["mot de passe"].bind("<KeyRelease>", self.evaluer_mot_de_passe)

        # Bouton Enregistrer
        ctk.CTkButton(self.popup, text="Enregistrer", command=self.enregistrer_mot_de_passe).grid(row=5, column=0, columnspan=2, pady=20)

    def evaluer_mot_de_passe(self, event=None):
        password = self.entries_form["mot de passe"].get()
        score = self.calculer_score_mdp(password)
        self.security_bar.set(score / 5)

        # Changement de couleur dynamique
        if score <= 2:
            self.security_bar.configure(progress_color="red")
        elif score <= 4:
            self.security_bar.configure(progress_color="orange")
        else:
            self.security_bar.configure(progress_color="green")

    def calculer_score_mdp(self, password):
        score = 0
        if len(password) >= 8: score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isupper() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in string.punctuation for c in password): score += 1
        return score

    def enregistrer_mot_de_passe(self):
        titre = self.entries_form["titre"].get()
        identifiant = self.entries_form["identifiant"].get()
        site = self.entries_form["site web"].get()
        mdp = self.entries_form["mot de passe"].get()

        self.entries.append((titre, identifiant, site, mdp))
        self.tree.insert('', 'end', values=(titre, identifiant, site, mdp))
        self.popup.destroy()
