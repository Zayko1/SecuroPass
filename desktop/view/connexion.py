import customtkinter as ctk

class ConnexionPage:
    def __init__(self, app):
        self.app = app
        self.app.title("SécuroPass - Connexion")
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

        # Bouton pour se connecter
        self.btn_connexion = ctk.CTkButton(self.app, text="Se connecter", width=250, command=self.se_connecter)
        self.btn_connexion.pack(pady=20)

    def se_connecter(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        # Appeler la logique de connexion ici
        print(f"Connexion avec {username} et {password}")
        # Si la connexion réussit, on redirige ailleurs, sinon on montre un message d'erreur
