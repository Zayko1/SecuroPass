# view/password_manager.py

import customtkinter as ctk
from tkinter import ttk, messagebox
import string
from controller.controller import Controller
import model.model as model_module

class PwdManagementPage:
    def __init__(self, parent_frame):
        """
        parent_frame : le CTkFrame hérité de HomePage
        """
        self.container = parent_frame
        # l'objet CTk principal est le parent du frame
        self.app = parent_frame.master
        # ID et clé utilisateur mis à jour lors du login
        self.user_id  = getattr(self.app, "user_id", None)
        self.user_key = getattr(self.app, "user_key", None)

        # couche métier
        self.controller = Controller(model_module)

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # Titre
        ctk.CTkLabel(self.container,
                     text="🔐 Gestionnaire de mots de passe",
                     font=("Arial", 20)).pack(pady=(10, 5))

        # Bouton + Ajouter
        ctk.CTkButton(self.container,
                      text="+ Ajouter un mot de passe",
                      fg_color="#1f6aa5",
                      hover_color="#155a8a",
                      text_color="white",
                      font=("Arial", 14, "bold"),
                      command=self.afficher_formulaire_popup
        ).pack(pady=10)

        # Arbre / tableau
        cols = ("Titre", "Identifiant", "Site", "Dernière modif")
        self.tree = ttk.Treeview(self.container,
                                 columns=cols,
                                 show="headings",
                                 selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(pady=20, expand=True, fill="both")

        # Double-clic pour afficher le mot de passe en clair
        self.tree.bind("<Double-1>", self.on_double_click)

    def refresh_list(self):
        # Vide l'arbre
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Récupère les entrées en base
        entries = self.controller.get_passwords_controller(self.user_id,
                                                          self.user_key)
        # Rempli l'arbre
        for e in entries:
            # on affiche juste la date comme "Dernière modif"
            self.tree.insert("", "end",
                             iid=e["id"],
                             values=(e["titre"],
                                     e["identifiant"],
                                     e["site_web"],
                                     e["date_ajout"].strftime("%Y-%m-%d %H:%M")))
    # ──────────────────────────────────────────────────────────────────────────
    def afficher_formulaire_popup(self):
        self.popup = ctk.CTkToplevel(self.container)
        self.popup.title("Ajouter un mot de passe")
        self.popup.geometry("400x400")

        # Champs du formulaire
        labels = [("Titre", False),
                  ("Identifiant", False),
                  ("Site Web", False),
                  ("Notes", False),
                  ("Mot de passe", True)]
        self.entries_form = {}
        for idx, (label, is_pwd) in enumerate(labels):
            ctk.CTkLabel(self.popup, text=f"{label} :").grid(row=idx,
                                                             column=0,
                                                             padx=10,
                                                             pady=5,
                                                             sticky="e")
            entry = ctk.CTkEntry(self.popup,
                                 width=200,
                                 show="*" if is_pwd else None)
            entry.grid(row=idx, column=1, pady=5)
            self.entries_form[label.lower()] = entry

        # Barre d'évaluation
        self.security_bar = ctk.CTkProgressBar(self.popup, width=200)
        self.security_bar.grid(row=len(labels), column=1,
                               pady=10, sticky="w")
        self.security_bar.set(0)
        self.entries_form["mot de passe"].bind(
            "<KeyRelease>", self.evaluer_mot_de_passe
        )

        # Niveau (lecture seule, calculé automatiquement)
        self.level_var = ctk.StringVar(self.popup, value="")
        ctk.CTkLabel(self.popup, text="Niveau :").grid(
            row=len(labels)+1, column=0, sticky="e", padx=10
        )
        ctk.CTkEntry(self.popup,
                     textvariable=self.level_var,
                     state="disabled").grid(
            row=len(labels)+1, column=1, pady=5
        )

        # Bouton Enregistrer
        ctk.CTkButton(self.popup,
                      text="Enregistrer",
                      command=self.enregistrer_mot_de_passe
        ).grid(row=len(labels)+2, column=0, columnspan=2, pady=20)

    def evaluer_mot_de_passe(self, event=None):
        pwd   = self.entries_form["mot de passe"].get()
        score = self.calculer_score_mdp(pwd)
        # mise à jour barre & couleur
        self.security_bar.set(score/5)
        color = "green" if score > 4 else "orange" if score > 2 else "red"
        self.security_bar.configure(progress_color=color)
        self.level_var.set(["Faible","Moyen","Fort","Fort","Fort"][score])

    def calculer_score_mdp(self, pwd: str) -> int:
        score = 0
        if len(pwd) >= 8: score += 1
        if any(c.islower() for c in pwd): score += 1
        if any(c.isupper() for c in pwd): score += 1
        if any(c.isdigit() for c in pwd): score += 1
        if any(c in string.punctuation for c in pwd): score += 1
        return score

    def enregistrer_mot_de_passe(self):
        data = {k: v.get().strip() for k, v in self.entries_form.items()}
        ok, msg = self.controller.add_password_controller(
            self.user_id,
            data["titre"],
            data["identifiant"],
            data["mot de passe"],
            data["site web"],
            data.get("notes", ""),
            self.level_var.get(),
            self.user_key
        )
        if not ok:
            messagebox.showerror("Erreur", msg, parent=self.popup)
            return
        messagebox.showinfo("Succès", msg, parent=self.popup)
        self.popup.destroy()
        self.refresh_list()

    def on_double_click(self, event):
        # Affiche le mot de passe en clair dans une boîte de dialogue
        item = self.tree.focus()
        if not item:
            return
        entry_id = int(item)
        # On refetch l'entrée pour la décrypter
        entries = self.controller.get_passwords_controller(
            self.user_id, self.user_key
        )
        entry = next((e for e in entries if e["id"] == entry_id), None)
        if entry:
            messagebox.showinfo("Mot de passe",
                                entry["password"],
                                parent=self.container)
