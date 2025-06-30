# views/components.py
import customtkinter as ctk
from utils.theme import Theme
import tkinter as tk

class ModernEntry(ctk.CTkEntry):
    """Champ de saisie moderne avec placeholder"""
    def __init__(self, parent, placeholder="", show="", width=200, height=40, **kwargs):
        super().__init__(
            parent,
            placeholder_text=placeholder,
            show=show,
            width=width,
            height=height,
            corner_radius=8,
            border_width=1,
            fg_color=Theme.INPUT_BG,
            border_color=Theme.INPUT_BORDER,
            text_color=Theme.TEXT_LIGHT,
            placeholder_text_color="#6c757d",
            font=("Arial", 14),
            **kwargs
        )

class ModernButton(ctk.CTkButton):
    """Bouton moderne avec effets"""
    def __init__(self, parent, text="", command=None, variant="primary", width=200, height=40, **kwargs):
        colors = {
            "primary": (Theme.PRIMARY_COLOR, Theme.SECONDARY_COLOR),
            "success": (Theme.SUCCESS, "#1e7e34"),
            "danger": (Theme.DANGER, "#bd2130"),
            "secondary": (Theme.CARD_BG, Theme.INPUT_BG)
        }
        
        fg_color, hover_color = colors.get(variant, colors["primary"])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=8,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color="white",
            font=("Arial", 14, "bold"),
            cursor="hand2",
            **kwargs
        )

class Card(ctk.CTkFrame):
    """Carte moderne avec ombre"""
    def __init__(self, parent, width=400, height=300, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            corner_radius=10,
            fg_color=Theme.CARD_BG,
            border_width=1,
            border_color="#3a3a3a",
            **kwargs
        )

class PasswordStrengthBar(ctk.CTkFrame):
    """Barre de force du mot de passe"""
    def __init__(self, parent):
        super().__init__(parent, height=5, fg_color="transparent")
        
        self.bar = ctk.CTkProgressBar(
            self,
            height=5,
            corner_radius=3,
            progress_color=Theme.DANGER,
            fg_color="#4a4a4a"
        )
        self.bar.pack(fill="x")
        self.bar.set(0)
    
    def update_strength(self, password):
        if not password:
            self.bar.set(0)
            self.bar.configure(progress_color=Theme.DANGER)
            return "Faible"
        
        score = 0
        if len(password) >= 8: score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isupper() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in "!@#$%^&*(),.?\":{}|<>" for c in password): score += 1
        if len(password) >= 12: score += 1
        
        if score < 3:
            self.bar.set(0.33)
            self.bar.configure(progress_color=Theme.DANGER)
            return "Faible"
        elif score < 5:
            self.bar.set(0.66)
            self.bar.configure(progress_color=Theme.WARNING)
            return "Moyen"
        else:
            self.bar.set(1.0)
            self.bar.configure(progress_color=Theme.SUCCESS)
            return "Fort"

class Toast(ctk.CTkToplevel):
    """Notification toast moderne"""
    def __init__(self, parent, message, variant="info", duration=3000):
        super().__init__(parent)
        
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        
        # Pour macOS
        if parent.winfo_toplevel().winfo_exists():
            self.transient(parent.winfo_toplevel())
        
        colors = {
            "success": Theme.SUCCESS,
            "error": Theme.DANGER,
            "warning": Theme.WARNING,
            "info": Theme.PRIMARY_COLOR
        }
        
        bg_color = colors.get(variant, colors["info"])
        
        # Frame principal
        frame = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=10)
        frame.pack(padx=2, pady=2)
        
        # Message
        label = ctk.CTkLabel(
            frame,
            text=message,
            font=("Arial", 14),
            text_color="white"
        )
        label.pack(padx=20, pady=15)
        
        # Position
        self.update_idletasks()
        
        # Obtenir la fenêtre parent principale
        main_window = parent.winfo_toplevel()
        x = main_window.winfo_x() + (main_window.winfo_width() - self.winfo_width()) // 2
        y = main_window.winfo_y() + 50
        
        self.geometry(f"+{x}+{y}")
        
        # Animation d'apparition
        self.attributes('-alpha', 0.0)
        self.fade_in()
        
        # Auto-fermeture
        self.after(duration, self.fade_out)
    
    def fade_in(self, alpha=0.0):
        alpha += 0.1
        self.attributes('-alpha', alpha)
        if alpha < 1.0:
            self.after(20, lambda: self.fade_in(alpha))
    
    def fade_out(self, alpha=1.0):
        alpha -= 0.1
        self.attributes('-alpha', alpha)
        if alpha > 0:
            self.after(20, lambda: self.fade_out(alpha))
        else:
            self.destroy()