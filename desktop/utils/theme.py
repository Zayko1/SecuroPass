# utils/theme.py
import customtkinter as ctk
class Theme:
    # Couleurs du thème dark (identiques au web)
    PRIMARY_COLOR = "#1f6aa5"
    SECONDARY_COLOR = "#155a8a"
    DARK_BG = "#1a1a1a"
    CARD_BG = "#2d2d2d"
    TEXT_LIGHT = "#e0e0e0"
    SUCCESS = "#28a745"
    WARNING = "#ffc107"
    DANGER = "#dc3545"
    INPUT_BG = "#3d3d3d"
    INPUT_BORDER = "#4d4d4d"
    
    @classmethod
    def setup(cls):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configuration des couleurs par défaut pour CTk
        ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = [cls.CARD_BG, cls.CARD_BG]
        ctk.ThemeManager.theme["CTkLabel"]["text_color"] = [cls.TEXT_LIGHT, cls.TEXT_LIGHT]