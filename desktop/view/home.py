# view/home.py
import customtkinter as ctk
from tkinter import messagebox
from view.password_manager import PwdManagementPage

class HomeApp(ctk.CTk):
    def __init__(self, app):
        self.app = app

        # Configuration de la fenêtre (App l’a déjà créée)
        self.app.title("SécuroPass - Accueil")
        self.app.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.app.configure(bg_color="black")

        # Construction des widgets
        self.build()

    def build(self):
        # Efface tout l'ancien contenu
        for w in self.app.winfo_children():
            w.destroy()

        # Cadre du menu latéral
        self.menu_frame = ctk.CTkFrame(self.app, width=200, fg_color="#1e1e1e")
        self.menu_frame.pack(side="left", fill="y")

        # Cadre principal de contenu
        self.content_frame = ctk.CTkFrame(self.app, fg_color="black")
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Boutons du menu
        btn_consult   = ctk.CTkButton(self.menu_frame,
                                      text="📂 Consulter mes mots de passe",
                                      command=self.show_consult)
        btn_settings  = ctk.CTkButton(self.menu_frame,
                                      text="⚙️ Paramètres",
                                      command=self.show_settings)
        btn_logout    = ctk.CTkButton(self.menu_frame,
                                      text="🚪 Me déconnecter",
                                      fg_color="red",
                                      command=self.logout)

        for btn in (btn_consult, btn_settings, btn_logout):
            btn.pack(pady=10, padx=10, fill="x")

        # Message de bienvenue
        self.label_info = ctk.CTkLabel(self.content_frame,
                                       text="Bienvenue dans SécuroPass !",
                                       font=("Arial", 18))
        self.label_info.pack(pady=20)

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def show_consult(self):
        self.clear_content()
        # On passe le frame parent à PwdManagementPage
        PwdManagementPage(self.content_frame)

    def show_settings(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame,
                     text="Paramètres du compte et de l'application.",
                     font=("Arial", 16)).pack(pady=30)

    def logout(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?", parent=self.app):
            # Revenir à la page principale
            self.app.show_main()

