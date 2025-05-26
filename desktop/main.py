# main.py
import customtkinter as ctk
from view.gui import MainPage
from view.home import HomeApp
from view.password_manager import PwdManagementPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # stocke la "clé utilisateur" après login
        self.user_key = None

        # Méthodes de navigation accessibles par les vues
        self.show_main          = self._show_main
        self.show_home          = self._show_home
        self.show_password_mgr  = self._show_password_mgr

        # Page de démarrage
        self._show_main()

    def _show_main(self):
        # Affiche la page d'accueil
        MainPage(self)

    def _show_home(self):
        # Affiche l'écran "home" après login
        HomeApp(self)

    def _show_password_mgr(self):
        # Affiche la gestion des mots de passe
        PwdManagementPage(self)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
