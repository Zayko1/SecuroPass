import customtkinter as ctk
from view.gui import MainPage

def main():
    app = ctk.CTk()  # Création de l'application
    main_page = MainPage(app)  # Initialisation de la page principale
    app.mainloop()  # Démarrage de l'interface graphique

if __name__ == "__main__":
    main()
