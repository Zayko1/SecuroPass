# view/password_manager.py

import customtkinter as ctk
from tkinter import ttk, messagebox
import string
from controller.controller import Controller
import model.model as model_module
import tkinter as tk

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
        cols = ("Titre", "Identifiant", "Mot de passe", "Site", "Dernière modif")
        self.tree = ttk.Treeview(self.container,
                                 columns=cols,
                                 show="headings",
                                 selectmode="browse")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(pady=20, expand=True, fill="both")

        self.menu = tk.Menu(self.app, tearoff=0)
        self.menu.add_command(label="Copier l'identifiant", command=self._copy_ident)
        self.menu.add_command(label="Copier le mot de passe", command=self._copy_pwd)
        self.menu.add_separator()
        self.menu.add_command(label="Supprimer l'entrée", command=self._delete_entry)


        # Binder clic droit sur le Treeview
        self.tree.bind("<Button-3>", self._on_right_click)
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
            # on masque le mot de passe dans le tableau par 5 étoiles
            masked_pwd = "*****"
            self.tree.insert("", "end",
                             iid=e["id"],
                             values=(e["titre"],
                                     e["identifiant"],
                                     masked_pwd,
                                     e["site_web"],
                                     e["date_ajout"].strftime("%Y-%m-%d %H:%M")
                                     ))
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
        """Ouvre un popup pour modifier l'entrée sélectionnée."""
        iid = self.tree.focus()
        if not iid:
            return
        entry_id = int(iid)
        # Récupère l'entrée complète
        entries = self.controller.get_passwords_controller(
            self.user_id, self.user_key
        )
        entry = next((e for e in entries if e["id"] == entry_id), None)
        if not entry:
            return

        # --- Création du popup ---
        popup = ctk.CTkToplevel(self.app)
        popup.title("Modifier l'entrée")
        popup.geometry("400x300")

        # Champs préremplis
        labels = [("Titre", entry["titre"]),
                  ("Identifiant", entry["identifiant"]),
                  ("Mot de passe", entry["password"]),
                  ("Note", entry.get("notes",""))]
        entries_widgets = {}
        for i, (label, value) in enumerate(labels):
            ctk.CTkLabel(popup, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            show = None if label!="Mot de passe" else "*"
            e = ctk.CTkEntry(popup, width=200, show=show)
            e.insert(0, value)
            e.grid(row=i, column=1, pady=5, sticky="w")
            entries_widgets[label] = e

        def save_changes():
            new_title = entries_widgets["Titre"].get().strip()
            new_ident = entries_widgets["Identifiant"].get().strip()
            new_pwd   = entries_widgets["Mot de passe"].get()
            new_note  = entries_widgets["Note"].get().strip()

            # Appel au contrôleur (voir Section 2)
            ok, msg = self.controller.update_entry_controller(
                entry_id, new_title, new_ident, new_pwd, new_note, self.user_key
            )
            if ok:
                messagebox.showinfo("Succès", msg, parent=popup)
                popup.destroy()
                self.refresh_list()
            else:
                messagebox.showerror("Erreur", msg, parent=popup)

        # Bouton Enregistrer
        ctk.CTkButton(popup, text="Enregistrer", command=save_changes).grid(
            row=len(labels), column=0, columnspan=2, pady=20
        )
            
    def _on_right_click(self, event):
        # Sélectionner la ligne sous le curseur
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)

        # Récupérer les données
        values = self.tree.item(iid, "values")
        # cols = ("Titre", "Identifiant", "Mot de passe", "Site", "Dernière modif")
        self._ctx_ident = values[1]
        self._ctx_pwd   = values[2]

        # Afficher le menu
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _copy_ident(self):
        # Copier identifiant dans le presse-papier
        item = self.tree.focus()
        if not item:
            return
        entry_id = int(item)
        entries = self.controller.get_passwords_controller(self.user_id, self.user_key)
        entry   = next((e for e in entries if e["id"] == entry_id), None)
        if entry:
            self.app.clipboard_clear()
            self.app.clipboard_append(entry["identifiant"])

    def _copy_pwd(self):
        # Copier mot de passe dans le presse-papier
        item = self.tree.focus()
        if not item:
            return
        entry_id = int(item)
        entries = self.controller.get_passwords_controller(self.user_id, self.user_key)
        entry   = next((e for e in entries if e["id"] == entry_id), None)
        if entry:
            self.app.clipboard_clear()
            self.app.clipboard_append(entry["password"])
    
    def _delete_entry(self):
        item = self.tree.focus()
        if not item:
            return
        entry_id = int(item)
        confirm = messagebox.askyesno(
            "Suppression", "Supprimer cette entrée ?",
            parent=self.app
        )
        if not confirm:
            return
        ok, msg = self.controller.delete_password_controller(entry_id)
        if ok:
            self.refresh_list()
            messagebox.showinfo("Suppression", "Entrée supprimée !", parent=self.app)
        else:
            messagebox.showerror("Erreur", msg, parent=self.app)

