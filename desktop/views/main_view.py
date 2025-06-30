# ==================== views/main_view.py ====================
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pyperclip
from views.components import ModernButton, Card, ModernEntry, PasswordStrengthBar, Toast
from controllers.password_controller import PasswordController
from utils.theme import Theme
from models.database import Database

class MainView(ctk.CTkFrame):
    def __init__(self, parent, app, user_data):
        super().__init__(parent, fg_color=Theme.DARK_BG)
        self.app = app
        self.user_data = user_data
        self.password_controller = PasswordController(user_data)
        self.current_passwords = []
        
        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_passwords()
    
    def setup_ui(self):
        # Header
        self.create_header()
        
        # Content area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Actions
        left_panel = ctk.CTkFrame(content_frame, fg_color="transparent", width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)
        
        self.create_action_panel(left_panel)
        
        # Right panel - Password list
        right_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_panel.pack(side="left", fill="both", expand=True)
        
        self.create_password_panel(right_panel)
    
    def create_header(self):
        header = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Logo et titre
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=10)
        
        logo = ctk.CTkLabel(left_frame, text="🛡️", font=("Segoe UI", 32))
        logo.pack(side="left", padx=(0, 10))
        
        title = ctk.CTkLabel(
            left_frame,
            text="SecuroPass",
            font=("Segoe UI", 24, "bold"),
            text_color=Theme.PRIMARY_COLOR
        )
        title.pack(side="left")
        
        # User info et logout
        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=10)
        
        user_label = ctk.CTkLabel(
            right_frame,
            text=f"👤 {self.user_data['username']}",
            font=("Segoe UI", 14),
            text_color=Theme.TEXT_LIGHT
        )
        user_label.pack(side="left", padx=10)
        
        logout_btn = ModernButton(
            right_frame,
            text="Déconnexion",
            command=self.logout,
            variant="danger",
            width=120
        )
        logout_btn.pack(side="left")
    
    def create_action_panel(self, parent):
        # Titre
        title = ctk.CTkLabel(
            parent,
            text="Actions",
            font=("Segoe UI", 20, "bold"),
            text_color=Theme.TEXT_LIGHT
        )
        title.pack(pady=(0, 20))
        
        # Bouton ajouter
        add_btn = ModernButton(
            parent,
            text="➕ Ajouter un mot de passe",
            command=self.show_add_dialog,
            variant="success",
            width=260
        )
        add_btn.pack(pady=10)
        
        # Barre de recherche
        search_frame = Card(parent)
        search_frame.pack(fill="x", pady=20)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Rechercher",
            font=("Segoe UI", 14),
            text_color=Theme.TEXT_LIGHT
        )
        search_label.pack(pady=(10, 5))
        
        self.search_entry = ModernEntry(
            search_frame,
            placeholder="Titre, identifiant, site...",
            width=240
        )
        self.search_entry.pack(padx=10, pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.search_passwords)
        
        # Statistiques
        stats_card = Card(parent)
        stats_card.pack(fill="x", pady=10)
        
        stats_title = ctk.CTkLabel(
            stats_card,
            text="📊 Statistiques",
            font=("Segoe UI", 16, "bold"),
            text_color=Theme.TEXT_LIGHT
        )
        stats_title.pack(pady=(10, 5))
        
        self.stats_label = ctk.CTkLabel(
            stats_card,
            text="",
            font=("Segoe UI", 12),
            text_color=Theme.TEXT_LIGHT,
            justify="left"
        )
        self.stats_label.pack(padx=10, pady=(0, 10))
        
        # Générateur
        generator_btn = ModernButton(
            parent,
            text="🔐 Générateur de mot de passe",
            command=self.show_generator_dialog,
            variant="primary",
            width=260
        )
        generator_btn.pack(pady=10)
    
    def create_password_panel(self, parent):
        # Header avec titre et actions
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Mes mots de passe",
            font=("Segoe UI", 20, "bold"),
            text_color=Theme.TEXT_LIGHT
        )
        title.pack(side="left")
        
        # Container scrollable
        self.password_container = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=Theme.INPUT_BORDER,
            scrollbar_button_hover_color=Theme.PRIMARY_COLOR
        )
        self.password_container.pack(fill="both", expand=True)
    
    def load_passwords(self):
        self.current_passwords = self.password_controller.get_all_passwords()
        self.display_passwords(self.current_passwords)
        self.update_stats()
    
    def display_passwords(self, passwords):
        # Clear existing widgets
        for widget in self.password_container.winfo_children():
            widget.destroy()
        
        if not passwords:
            no_data = ctk.CTkLabel(
                self.password_container,
                text="🔒 Aucun mot de passe enregistré",
                font=("Segoe UI", 16),
                text_color="#6c757d"
            )
            no_data.pack(pady=50)
            return
        
        # Display each password as a card
        for pwd in passwords:
            self.create_password_card(pwd)
    
    def create_password_card(self, pwd_data):
        card = Card(self.password_container)
        card.pack(fill="x", pady=5, padx=5)
        
        # Main content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=15)
        
        # Left side - Info
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)
        
        # Title and security level
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(fill="x")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text=pwd_data['titre'],
            font=("Segoe UI", 16, "bold"),
            text_color=Theme.TEXT_LIGHT,
            anchor="w"
        )
        title_label.pack(side="left")
        
        # Security badge
        level_colors = {
            "Très Fort": Theme.SUCCESS,
            "Fort": Theme.SUCCESS,
            "Moyen": Theme.WARNING,
            "Faible": Theme.DANGER
        }
        level_color = level_colors.get(pwd_data['niveau'], Theme.WARNING)
        
        level_label = ctk.CTkLabel(
            title_frame,
            text=pwd_data['niveau'],
            font=("Segoe UI", 10, "bold"),
            text_color=level_color
        )
        level_label.pack(side="left", padx=10)
        
        # Identifier
        id_label = ctk.CTkLabel(
            left_frame,
            text=f"📧 {pwd_data['identifiant']}",
            font=("Segoe UI", 12),
            text_color=Theme.TEXT_LIGHT,
            anchor="w"
        )
        id_label.pack(fill="x", pady=2)
        
        # Website
        if pwd_data['site_web']:
            site_label = ctk.CTkLabel(
                left_frame,
                text=f"🌐 {pwd_data['site_web']}",
                font=("Segoe UI", 12),
                text_color=Theme.PRIMARY_COLOR,
                anchor="w",
                cursor="hand2"
            )
            site_label.pack(fill="x", pady=2)
        
        # Date
        date_str = pwd_data['date_ajout'].strftime("%d/%m/%Y %H:%M")
        date_label = ctk.CTkLabel(
            left_frame,
            text=f"📅 {date_str}",
            font=("Segoe UI", 10),
            text_color="#6c757d",
            anchor="w"
        )
        date_label.pack(fill="x", pady=2)
        
        # Right side - Actions
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=(10, 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        actions_frame.pack()
        
        # Copy password button
        copy_pwd_btn = ctk.CTkButton(
            actions_frame,
            text="📋",
            width=40,
            height=40,
            command=lambda: self.copy_password(pwd_data['password']),
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.PRIMARY_COLOR
        )
        copy_pwd_btn.pack(side="left", padx=2)
        
        # Copy username button
        copy_user_btn = ctk.CTkButton(
            actions_frame,
            text="👤",
            width=40,
            height=40,
            command=lambda: self.copy_to_clipboard(pwd_data['identifiant'], "Identifiant"),
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.PRIMARY_COLOR
        )
        copy_user_btn.pack(side="left", padx=2)
        
        # View/Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=40,
            height=40,
            command=lambda: self.show_edit_dialog(pwd_data),
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.WARNING
        )
        edit_btn.pack(side="left", padx=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=40,
            height=40,
            command=lambda: self.delete_password(pwd_data['id']),
            fg_color=Theme.INPUT_BG,
            hover_color=Theme.DANGER
        )
        delete_btn.pack(side="left", padx=2)
    
    def show_add_dialog(self):
        dialog = PasswordDialog(self, "Ajouter un mot de passe")
        self.wait_window(dialog)
        
        if dialog.result:
            success, message = self.password_controller.add_password(**dialog.result)
            if success:
                Toast(self, message, "success")
                self.load_passwords()
            else:
                messagebox.showerror("Erreur", message)
    
    def show_edit_dialog(self, pwd_data):
        dialog = PasswordDialog(self, "Modifier le mot de passe", pwd_data)
        self.wait_window(dialog)
        
        if dialog.result:
            success, message = self.password_controller.update_password(
                pwd_data['id'],
                **dialog.result
            )
            if success:
                Toast(self, message, "success")
                self.load_passwords()
            else:
                messagebox.showerror("Erreur", message)
    
    def show_generator_dialog(self):
        dialog = GeneratorDialog(self)
        self.wait_window(dialog)
    
    def delete_password(self, pwd_id):
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce mot de passe ?"):
            success, message = self.password_controller.delete_password(pwd_id)
            if success:
                Toast(self, message, "success")
                self.load_passwords()
            else:
                messagebox.showerror("Erreur", message)
    
    def copy_password(self, password):
        pyperclip.copy(password)
        Toast(self, "Mot de passe copié!", "success")
    
    def copy_to_clipboard(self, text, label):
        pyperclip.copy(text)
        Toast(self, f"{label} copié!", "success")
    
    def search_passwords(self, event=None):
        query = self.search_entry.get().lower()
        if not query:
            self.display_passwords(self.current_passwords)
            return
        
        filtered = [
            pwd for pwd in self.current_passwords
            if query in pwd['titre'].lower() or
               query in pwd['identifiant'].lower() or
               query in pwd.get('site_web', '').lower()
        ]
        self.display_passwords(filtered)
    
    def update_stats(self):
        total = len(self.current_passwords)
        
        if total == 0:
            self.stats_label.configure(text="Aucun mot de passe")
            return
        
        # Count by strength
        strength_counts = {
            "Très Fort": 0,
            "Fort": 0,
            "Moyen": 0,
            "Faible": 0
        }
        
        for pwd in self.current_passwords:
            level = pwd.get('niveau', 'Inconnu')
            if level in strength_counts:
                strength_counts[level] += 1
        
        stats_text = f"""Total: {total} mot(s) de passe
🟢 Très fort: {strength_counts['Très Fort']}
🟢 Fort: {strength_counts['Fort']}
🟡 Moyen: {strength_counts['Moyen']}
🔴 Faible: {strength_counts['Faible']}"""
        
        self.stats_label.configure(text=stats_text)
    
    def logout(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            from views.login_view import LoginView
            self.app.switch_view(LoginView)


class PasswordDialog(ctk.CTkToplevel):
    """Dialog pour ajouter/modifier un mot de passe"""
    def __init__(self, parent, title, pwd_data=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.pwd_data = pwd_data
        
        # Configuration de la fenêtre
        self.geometry("500x650")
        self.resizable(False, False)
        
        # Configurer comme modal
        self.transient(parent)
        
        # Attendre que la fenêtre soit mappée avant le grab
        self.wait_visibility()
        self.grab_set()
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"500x650+{x}+{y}")
        
        # Configuration du style
        self.configure(fg_color="#1a1a1a")
        
        self.setup_ui()
        
        # Pre-fill if editing
        if pwd_data:
            self.fill_data(pwd_data)
        
        # Focus sur le premier champ
        self.title_entry.focus()
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="#2d2d2d", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=self.title(),
            font=("Arial", 20, "bold"),
            text_color="#e0e0e0"
        )
        title_label.pack(pady=(10, 20))
        
        # Form frame avec scrollbar si nécessaire
        form_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20)
        
        # Title field
        ctk.CTkLabel(
            form_container,
            text="Titre *",
            font=("Arial", 12),
            text_color="#e0e0e0",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.title_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Ex: Gmail personnel",
            width=400,
            height=40,
            fg_color="#3d3d3d",
            border_color="#4d4d4d",
            text_color="#e0e0e0"
        )
        self.title_entry.pack(fill="x", pady=(0, 15))
        
        # Identifier field
        ctk.CTkLabel(
            form_container,
            text="Identifiant *",
            font=("Arial", 12),
            text_color="#e0e0e0",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.identifier_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Ex: email@example.com",
            width=400,
            height=40,
            fg_color="#3d3d3d",
            border_color="#4d4d4d",
            text_color="#e0e0e0"
        )
        self.identifier_entry.pack(fill="x", pady=(0, 15))
        
        # Password field avec boutons
        ctk.CTkLabel(
            form_container,
            text="Mot de passe *",
            font=("Arial", 12),
            text_color="#e0e0e0",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        pwd_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            pwd_frame,
            placeholder_text="Mot de passe sécurisé",
            show="•",
            height=40,
            fg_color="#3d3d3d",
            border_color="#4d4d4d",
            text_color="#e0e0e0"
        )
        self.password_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        # Show/Hide button
        self.show_pwd_btn = ctk.CTkButton(
            pwd_frame,
            text="👁",
            width=40,
            height=40,
            command=self.toggle_password,
            fg_color="#3d3d3d",
            hover_color="#1f6aa5"
        )
        self.show_pwd_btn.pack(side="left", padx=(0, 5))
        
        # Generate button
        gen_btn = ctk.CTkButton(
            pwd_frame,
            text="🎲",
            width=40,
            height=40,
            command=self.generate_password,
            fg_color="#3d3d3d",
            hover_color="#28a745"
        )
        gen_btn.pack(side="left")
        
        # Password strength bar
        from views.components import PasswordStrengthBar
        self.strength_bar = PasswordStrengthBar(form_container)
        self.strength_bar.pack(fill="x", pady=(5, 15))
        
        self.password_entry.bind("<KeyRelease>", self.check_strength)
        
        # Website field
        ctk.CTkLabel(
            form_container,
            text="Site web",
            font=("Arial", 12),
            text_color="#e0e0e0",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.website_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Ex: https://gmail.com",
            width=400,
            height=40,
            fg_color="#3d3d3d",
            border_color="#4d4d4d",
            text_color="#e0e0e0"
        )
        self.website_entry.pack(fill="x", pady=(0, 15))
        
        # Notes field
        ctk.CTkLabel(
            form_container,
            text="Notes",
            font=("Arial", 12),
            text_color="#e0e0e0",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        self.notes_text = ctk.CTkTextbox(
            form_container,
            height=80,
            fg_color="#3d3d3d",
            text_color="#e0e0e0",
            border_width=1,
            border_color="#4d4d4d"
        )
        self.notes_text.pack(fill="x", pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            command=self.cancel,
            width=150,
            height=40,
            fg_color="#3d3d3d",
            hover_color="#4d4d4d"
        )
        cancel_btn.pack(side="left", padx=(20, 10))
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            command=self.save,
            width=150,
            height=40,
            fg_color="#1f6aa5",
            hover_color="#155a8a"
        )
        save_btn.pack(side="right", padx=(10, 20))
    
    def toggle_password(self):
        if self.password_entry.cget("show") == "•":
            self.password_entry.configure(show="")
            self.show_pwd_btn.configure(text="🙈")
        else:
            self.password_entry.configure(show="•")
            self.show_pwd_btn.configure(text="👁")
    
    def generate_password(self):
        from models.database import Database
        password = Database.generate_password(16)
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)
        self.check_strength()
    
    def check_strength(self, event=None):
        password = self.password_entry.get()
        self.strength_bar.update_strength(password)
    
    def fill_data(self, data):
        self.title_entry.insert(0, data['titre'])
        self.identifier_entry.insert(0, data['identifiant'])
        self.password_entry.insert(0, data['password'])
        self.website_entry.insert(0, data.get('site_web', ''))
        self.notes_text.insert("1.0", data.get('notes', ''))
        self.check_strength()
    
    def save(self):
        # Validation
        title = self.title_entry.get().strip()
        identifier = self.identifier_entry.get().strip()
        password = self.password_entry.get()
        
        if not title or not identifier or not password:
            messagebox.showerror("Erreur", "Les champs marqués * sont obligatoires.")
            return
        
        self.result = {
            "title": title,
            "identifier": identifier,
            "password": password,
            "site": self.website_entry.get().strip(),
            "notes": self.notes_text.get("1.0", "end-1c").strip()
        }
        
        self.destroy()
    
    def cancel(self):
        self.destroy()


class GeneratorDialog(ctk.CTkToplevel):
    """Dialog pour générer des mots de passe"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Générateur de mot de passe")
        
        # Configuration
        self.geometry("450x550")
        self.resizable(False, False)
        self.transient(parent)
        
        # Attendre que la fenêtre soit visible avant grab_set
        self.wait_visibility()
        self.grab_set()
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 550) // 2
        self.geometry(f"450x550+{x}+{y}")
        
        # Configuration du style
        self.configure(fg_color="#1a1a1a")
        
        self.setup_ui()
        self.generate()
    
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="#2d2d2d", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔐 Générateur de mot de passe",
            font=("Arial", 20, "bold"),
            text_color="#e0e0e0"
        )
        title_label.pack(pady=(10, 20))
        
        # Password display
        pwd_frame = ctk.CTkFrame(main_frame, fg_color="#3d3d3d", corner_radius=8)
        pwd_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.password_label = ctk.CTkLabel(
            pwd_frame,
            text="",
            font=("Consolas", 16),
            text_color="#e0e0e0",
            wraplength=380
        )
        self.password_label.pack(pady=15, padx=10)
        
        # Strength bar
        from views.components import PasswordStrengthBar
        self.strength_bar = PasswordStrengthBar(main_frame)
        self.strength_bar.pack(fill="x", padx=20, pady=(0, 20))
        
        # Options
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=20)
        
        # Length slider
        length_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        length_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            length_frame,
            text="Longueur:",
            font=("Arial", 12),
            text_color="#e0e0e0"
        ).pack(side="left", padx=(0, 10))
        
        self.length_var = tk.IntVar(value=16)
        self.length_slider = ctk.CTkSlider(
            length_frame,
            from_=8,
            to=32,
            variable=self.length_var,
            command=lambda v: self.on_option_change(),
            fg_color="#3d3d3d",
            progress_color="#1f6aa5",
            button_color="#1f6aa5",
            button_hover_color="#155a8a"
        )
        self.length_slider.pack(side="left", expand=True, fill="x", padx=10)
        
        self.length_label = ctk.CTkLabel(
            length_frame,
            text="16",
            font=("Arial", 12),
            text_color="#e0e0e0",
            width=30
        )
        self.length_label.pack(side="left")
        
        # Character options
        self.lowercase_var = tk.BooleanVar(value=True)
        self.uppercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)
        
        options = [
            ("Minuscules (a-z)", self.lowercase_var),
            ("Majuscules (A-Z)", self.uppercase_var),
            ("Chiffres (0-9)", self.digits_var),
            ("Caractères spéciaux (!@#$...)", self.special_var)
        ]
        
        for text, var in options:
            cb = ctk.CTkCheckBox(
                options_frame,
                text=text,
                variable=var,
                command=self.on_option_change,
                font=("Arial", 12),
                text_color="#e0e0e0",
                fg_color="#1f6aa5",
                hover_color="#155a8a",
                border_color="#4d4d4d"
            )
            cb.pack(anchor="w", pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20, padx=20)
        
        regenerate_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Régénérer",
            command=self.generate,
            width=150,
            height=40,
            fg_color="#1f6aa5",
            hover_color="#155a8a"
        )
        regenerate_btn.pack(side="left", padx=(0, 10))
        
        copy_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Copier",
            command=self.copy_password,
            width=150,
            height=40,
            fg_color="#28a745",
            hover_color="#1e7e34"
        )
        copy_btn.pack(side="right")
    
    def on_option_change(self, *args):
        self.length_label.configure(text=str(self.length_var.get()))
        self.generate()
    
    def generate(self):
        # S'assurer qu'au moins une option est sélectionnée
        if not any([self.lowercase_var.get(), self.uppercase_var.get(), 
                   self.digits_var.get(), self.special_var.get()]):
            self.lowercase_var.set(True)
        
        from models.database import Database
        password = Database.generate_password(
            length=self.length_var.get(),
            include_lower=self.lowercase_var.get(),
            include_upper=self.uppercase_var.get(),
            include_digits=self.digits_var.get(),
            include_special=self.special_var.get()
        )
        
        self.password_label.configure(text=password)
        self.strength_bar.update_strength(password)
    
    def copy_password(self):
        password = self.password_label.cget("text")
        if password:
            import pyperclip
            pyperclip.copy(password)
            
            # Afficher un toast
            from views.components import Toast
            Toast(self.master, "Mot de passe copié!", "success")