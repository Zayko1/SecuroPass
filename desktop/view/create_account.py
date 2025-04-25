import customtkinter as ctk

class CreationComptePage:
    def __init__(self, app):
        self.app = app
        self.app.title("SécuroPass - Création du compte")
        self.app.geometry("400x300")
        
        self.create_widgets()

    def create_widgets(self):
        # Label et champs de texte pour le nom d'utilisateur
        ctk.CTkLabel(self.app, text="Nom d'utilisateur").pack(pady=10)
        self.entry_username = ctk.CTkEntry(self.app, width=250)
        self.entry_username.pack(pady=5)

        # Label et champs de texte pour le mot de passe
        ctk.CTkLabel(self.app, text="Mot de passe").pack(pady=10)
        self.entry_password = ctk.CTkEntry(self.app, show="*", width=250)
        self.entry_password.pack(pady=5)

        # Bouton pour créer le compte
        self.btn_creer = ctk.CTkButton(self.app, text="Créer le compte", width=250, command=self.creer_compte)
        self.btn_creer.pack(pady=20)

    def creer_compte(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        # Appeler la logique de création de compte ici
        print(f"Création du compte avec {username} et {password}")
        # Si tout est bon, on redirige vers la page principale ou autre, sinon un message d'erreur
