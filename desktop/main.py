import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import bcrypt

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")   # dark / light
ctk.set_default_color_theme("blue")  # blue / green / dark-blue etc.

# Configuration de la base de données
db_config = {
    "host": "",  # Remplace par ton endpoint AWS RDS
    "user": "",  # Ton utilisateur MySQL
    "password": "",  # Ton mot de passe MySQL
    "database": ""  # Nom de ta base de données
}

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def enregistrer_compte():
    username = entry_username.get()
    password = entry_password.get()
    
    if not username or not password:
        messagebox.showwarning("Erreur", "Veuillez remplir tous les champs.")
        return

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe
        cursor.execute("SELECT * FROM comptes_maitres WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Ce nom d'utilisateur est déjà pris.")
            return

        # Insérer le compte
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO comptes_maitres (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        messagebox.showinfo("Succès", "Compte créé avec succès !")
        conn.close()

    except Error as e:
        messagebox.showerror("Erreur", f"Problème de connexion : {e}")

# Interface graphique
app = ctk.CTk()
app.title("SécuroPass - Création du compte maître")
app.geometry("400x300")

ctk.CTkLabel(app, text="Nom d'utilisateur").pack(pady=10)
entry_username = ctk.CTkEntry(app, width=250)
entry_username.pack(pady=5)

ctk.CTkLabel(app, text="Mot de passe").pack(pady=10)
entry_password = ctk.CTkEntry(app, show="*", width=250)
entry_password.pack(pady=5)

btn_creer = ctk.CTkButton(app, text="Créer le compte", command=enregistrer_compte)
btn_creer.pack(pady=20)

app.mainloop()
