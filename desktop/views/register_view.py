# ==================== views/register_view.py ====================
import customtkinter as ctk
from tkinter import messagebox
from views.components import ModernEntry, ModernButton, Card, PasswordStrengthBar
from controllers.auth_controller import AuthController
from utils.theme import Theme

class RegisterView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=Theme.DARK_BG)
        self.app = app
        self.auth_controller = AuthController()
        
        self.pack(fill="both", expand=True)
        self.setup_ui()
    
    def setup_ui(self):
        # Container principal
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo et titre
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(pady=(0, 30))
        
        logo_label = ctk.CTkLabel(
            title_frame,
            text="🛡️",
            font=("Segoe UI", 72)
        )
        logo_label.pack()
        
        title = ctk.CTkLabel(
            title_frame,
            text="SecuroPass",
            font=("Segoe UI", 36, "bold"),
            text_color=Theme.PRIMARY_COLOR
        )
        title.pack()
        
        # Carte d'inscription
        card = Card(container, width=400, height=500)
        card.pack(padx=20, pady=20)
        card.pack_propagate(False)
        
        # Titre de la carte
        card_title = ctk.CTkLabel(
            card,
            text="Créer un compte",
            font=("Segoe UI", 24, "bold"),
            text_color=Theme.TEXT_LIGHT
        )
        card_title.pack(pady=(30, 20))
        
        # Formulaire
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(padx=40, pady=20, fill="x")
        
        # Username
        self.username_entry = ModernEntry(
            form_frame,
            placeholder="Nom d'utilisateur (min. 3 caractères)",
            width=320
        )
        self.username_entry.pack(pady=10)
        
        # Password
        self.password_entry = ModernEntry(
            form_frame,
            placeholder="Mot de passe (min. 8 caractères)",
            show="•",
            width=320
        )
        self.password_entry.pack(pady=10)
        
        # Barre de force
        self.strength_bar = PasswordStrengthBar(form_frame)
        self.strength_bar.pack(fill="x", padx=5, pady=(0, 10))
        
        # Confirm password
        self.confirm_entry = ModernEntry(
            form_frame,
            placeholder="Confirmer le mot de passe",
            show="•",
            width=320
        )
        self.confirm_entry.pack(pady=10)
        
        # Bouton inscription
        self.register_button = ModernButton(
            form_frame,
            text="Créer mon compte",
            command=self.register,
            width=320
        )
        self.register_button.pack(pady=20)
        
        # Lien connexion
        login_frame = ctk.CTkFrame(card, fg_color="transparent")
        login_frame.pack(pady=(0, 30))
        
        login_label = ctk.CTkLabel(
            login_frame,
            text="Déjà un compte ?",
            font=("Segoe UI", 12),
            text_color=Theme.TEXT_LIGHT
        )
        login_label.pack(side="left", padx=5)
        
        login_link = ctk.CTkButton(
            login_frame,
            text="Se connecter",
            font=("Segoe UI", 12, "underline"),
            text_color=Theme.PRIMARY_COLOR,
            fg_color="transparent",
            hover=False,
            command=self.show_login,
            width=100
        )
        login_link.pack(side="left")
        
        # Bind password entry
        self.password_entry.bind("<KeyRelease>", self.check_password_strength)
    
    def check_password_strength(self, event=None):
        password = self.password_entry.get()
        self.strength_bar.update_strength(password)
    
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Validation
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        
        if len(username) < 3:
            messagebox.showerror("Erreur", "Le nom d'utilisateur doit contenir au moins 3 caractères.")
            return
        
        if len(password) < 8:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 8 caractères.")
            return
        
        if password != confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.")
            return
        
        self.register_button.configure(text="Création...", state="disabled")
        
        success, message = self.auth_controller.register(username, password)
        
        if success:
            messagebox.showinfo("Succès", message)
            self.show_login()
        else:
            self.register_button.configure(text="Créer mon compte", state="normal")
            messagebox.showerror("Erreur", message)
    
    def show_login(self):
        from views.login_view import LoginView
        self.app.switch_view(LoginView)