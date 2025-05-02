# view/home.py
import customtkinter as ctk
from tkinter import messagebox

class HomeApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("SécuroPass - Accueil")
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(bg_color="black")

        self.create_widgets()

    def create_widgets(self):
        # Menu latéral
        self.menu_frame = ctk.CTkFrame(self, width=200, fg_color="#1e1e1e")
        self.menu_frame.pack(side="left", fill="y")

        self.content_frame = ctk.CTkFrame(self, fg_color="black")
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Boutons du menu
        btn_gen = ctk.CTkButton(self.menu_frame, text="🔐 Générer un mot de passe", command=self.show_generate)
        btn_scan = ctk.CTkButton(self.menu_frame, text="🔎 Scanner les mots de passe", command=self.show_scan)
        btn_consult = ctk.CTkButton(self.menu_frame, text="📂 Consulter mes mots de passe", command=self.show_consult)
        btn_settings = ctk.CTkButton(self.menu_frame, text="⚙️ Paramètres", command=self.show_settings)
        btn_logout = ctk.CTkButton(self.menu_frame, text="🚪 Me déconnecter", fg_color="red", command=self.logout)

        for btn in (btn_gen, btn_scan, btn_consult, btn_settings, btn_logout):
            btn.pack(pady=10, padx=10, fill="x")

        self.label_info = ctk.CTkLabel(self.content_frame, text="Bienvenue dans SécuroPass !", font=("Arial", 18))
        self.label_info.pack(pady=20)

    def show_generate(self):
        self.update_content("Ici, tu pourras générer un mot de passe sécurisé.")

    def show_scan(self):
        self.update_content("Scanner les mots de passe : en construction.")

    def show_consult(self):
        self.update_content("Voici la liste de tes mots de passe enregistrés.")

    def show_settings(self):
        self.update_content("Paramètres du compte et de l'application.")

    def logout(self):
        confirmed = messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?")
        if confirmed:
            main.

    def update_content(self, text):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.content_frame, text=text, font=("Arial", 16)).pack(pady=30)

