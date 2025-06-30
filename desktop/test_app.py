# test_app.py - Pour tester si customtkinter fonctionne correctement
import customtkinter as ctk

# Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Fenêtre principale
root = ctk.CTk()
root.title("Test SecuroPass")
root.geometry("600x500")

# Frame principal
main_frame = ctk.CTkFrame(root, fg_color="#1a1a1a")
main_frame.pack(fill="both", expand=True)

# Titre
title = ctk.CTkLabel(
    main_frame,
    text="🛡️ SecuroPass",
    font=("Arial", 32, "bold"),
    text_color="#1f6aa5"
)
title.pack(pady=20)

# Card
card = ctk.CTkFrame(main_frame, fg_color="#2d2d2d", corner_radius=10)
card.pack(padx=50, pady=20, fill="x")

# Contenu de la card
card_title = ctk.CTkLabel(
    card,
    text="Connexion",
    font=("Arial", 20, "bold"),
    text_color="#e0e0e0"
)
card_title.pack(pady=20)

# Entry
username_entry = ctk.CTkEntry(
    card,
    placeholder_text="Nom d'utilisateur",
    width=300,
    height=40,
    fg_color="#3d3d3d",
    border_color="#4d4d4d",
    text_color="#e0e0e0"
)
username_entry.pack(pady=10)

password_entry = ctk.CTkEntry(
    card,
    placeholder_text="Mot de passe",
    show="•",
    width=300,
    height=40,
    fg_color="#3d3d3d",
    border_color="#4d4d4d",
    text_color="#e0e0e0"
)
password_entry.pack(pady=10)

# Bouton
login_btn = ctk.CTkButton(
    card,
    text="Se connecter",
    width=300,
    height=40,
    fg_color="#1f6aa5",
    hover_color="#155a8a",
    font=("Arial", 14, "bold"),
    command=lambda: print("Connexion...")
)
login_btn.pack(pady=20)

# Info
info_label = ctk.CTkLabel(
    card,
    text="Pas de compte ? Créer un compte",
    font=("Arial", 12),
    text_color="#6c757d"
)
info_label.pack(pady=(0, 20))

root.mainloop()