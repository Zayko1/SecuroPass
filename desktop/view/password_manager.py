#view/password_manager.py
import customtkinter as ctk
from model.model import get_passwords

class PwdManagementPage(ctk.CTkFrame):
    def __init__(self, master, user_id, cle_chiffrement):
        super().__init__(master)
        self.user_id = user_id
        self.cle = cle_chiffrement

        self.label = ctk.CTkLabel(self, text="Mes mots de passe")
        self.label.pack(pady=10)

        self.table = ctk.CTkTextbox(self, width=800, height=400)
        self.table.pack(padx=20, pady=20)

        self.afficher_mots_de_passe()

    def afficher_mots_de_passe(self):
        self.table.delete("0.0", "end")

        passwords = get_passwords(self.user_id, self.cle)
        if not passwords:
            self.table.insert("end", "Aucun mot de passe enregistré.\n")
            return

        for titre, identifiant, mdp, site, niveau in passwords:
            ligne = f"{titre} | {identifiant} | {mdp} | {site or ''} | {niveau or ''}\n"
            self.table.insert("end", ligne)

