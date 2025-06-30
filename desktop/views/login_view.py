# views/login_view.py
import customtkinter as ctk
from tkinter import messagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#1a1a1a")
        self.app = app
        
        # Import ici pour éviter les imports circulaires
        from controllers.auth_controller import AuthController
        self.auth_controller = AuthController()
        
        self.pack(fill="both", expand=True)
        self.setup_ui()
    
    def setup_ui(self):
        # Container principal centré
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(expand=True, fill="both")
        
        # Frame central
        center_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        center_frame.pack(expand=True)
        
        # Logo et titre
        logo_label = ctk.CTkLabel(
            center_frame,
            text="🛡️",
            font=("Arial", 72)
        )
        logo_label.pack(pady=(50, 10))
        
        title = ctk.CTkLabel(
            center_frame,
            text="SecuroPass",
            font=("Arial", 36, "bold"),
            text_color="#1f6aa5"
        )
        title.pack(pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            center_frame,
            text="Gestionnaire de mots de passe sécurisé",
            font=("Arial", 14),
            text_color="#e0e0e0"
        )
        subtitle.pack(pady=(0, 30))
        
        # Carte de connexion
        card = ctk.CTkFrame(
            center_frame, 
            width=400, 
            height=380,
            corner_radius=10,
            fg_color="#2d2d2d"
        )
        card.pack()
        card.pack_propagate(False)
        
        # Contenu de la carte
        card_content = ctk.CTkFrame(card, fg_color="transparent")
        card_content.pack(expand=True, fill="both", padx=40, pady=30)
        
        # Titre de la carte
        card_title = ctk.CTkLabel(
            card_content,
            text="Connexion",
            font=("Arial", 24, "bold"),
            text_color="#e0e0e0"
        )
        card_title.pack(pady=(0, 20))
        
        # Champ username
        self.username_entry = ctk.CTkEntry(
            card_content,
            placeholder_text="Nom d'utilisateur",
            width=320,
            height=40,
            corner_radius=8,
            border_width=1,
            fg_color="#3d3d3d",
            border_color="#4d4d4d",
            text_color="#e0e0e0",
            placeholder_text_color="#6c757d",
            font=("Arial", 14)
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Champ password
        self.password_entry = ctk.CTkEntry(
            card_content,
            placeholder_text="Mot de passe",
            show="•",
            width=320,
            height=40,
            corner_radius=8,
            border_width=1,
            fg_color="#3d3d3d",
            border_color="#4d4d4d",
            text_color="#e0e0e0",
            placeholder_text_color="#6c757d",
            font=("Arial", 14)
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Bouton connexion
        self.login_button = ctk.CTkButton(
            card_content,
            text="Se connecter",
            command=self.login,
            width=320,
            height=40,
            corner_radius=8,
            fg_color="#1f6aa5",
            hover_color="#155a8a",
            text_color="white",
            font=("Arial", 14, "bold")
        )
        self.login_button.pack(pady=(0, 20))
        
        # Section inscription
        register_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        register_frame.pack()
        
        register_label = ctk.CTkLabel(
            register_frame,
            text="Pas encore de compte ?",
            font=("Arial", 12),
            text_color="#e0e0e0"
        )
        register_label.grid(row=0, column=0, padx=(0, 5))
        
        # Bouton créer compte (utiliser un CTkLabel cliquable au lieu de CTkButton)
        register_link = ctk.CTkLabel(
            register_frame,
            text="Créer un compte",
            font=("Arial", 12, "underline"),
            text_color="#1f6aa5",
            cursor="hand2"
        )
        register_link.grid(row=0, column=1)
        register_link.bind("<Button-1>", lambda e: self.show_register())
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return
        
        self.login_button.configure(text="Connexion...", state="disabled")
        self.update()  # Force UI update
        
        success, result = self.auth_controller.login(username, password)
        
        if success:
            from views.main_view import MainView
            self.app.switch_view(MainView, user_data=result)
        else:
            self.login_button.configure(text="Se connecter", state="normal")
            messagebox.showerror("Erreur de connexion", result)
    
    def show_register(self):
        from views.register_view import RegisterView
        self.app.switch_view(RegisterView)