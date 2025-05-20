#main.py
import customtkinter as ctk
from view.gui import MainPage
from view.home import HomeApp
from view.password_manager import PwdManagementPage
def main():
    app = ctk.CTk()  # Création de l'application
    main_page = MainPage(app)  # Initialisation de la page principale
    app.mainloop()  # Démarrage de l'interface graphique
    ouvrir_home()
    

def ouvrir_home():
    app = HomeApp()
    app.mainloop()

def ouvrir_pwdmngmnt():
    app = HomeApp()
    app.mainloop()
    
if __name__ == "__main__":
    main()
