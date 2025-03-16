import tkinter as tk
from tkinter import messagebox
import random 
import string
import os
import pyperclip  # Pour copier dans le presse-papier

# Génération de mot de passe
def generatePassword(longueur):
    # Définition des ensembles de caractères
    majuscules = string.ascii_uppercase
    minuscules = string.ascii_lowercase
    chiffres = string.digits
    speciaux = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Assurer au moins un caractère de chaque type
    mdp = [
        random.choice(majuscules),
        random.choice(minuscules),
        random.choice(chiffres),
        random.choice(speciaux)
    ]
    
    # Compléter avec des caractères aléatoires
    tous_caracteres = majuscules + minuscules + chiffres + speciaux
    mdp.extend(random.choice(tous_caracteres) for _ in range(longueur - 4))
    
    # Mélanger aléatoirement
    random.shuffle(mdp)
    
    return ''.join(mdp)

# Classe de l'application Tkinter
class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de Mots de Passe")
        self.root.geometry("400x350")

        # Liste pour stocker les mots de passe (à remplacer par la base de données plus tard)
        self.password_list = []

        # Label et champs de texte pour le nom du site
        self.site_label = tk.Label(root, text="Nom du site/app:")
        self.site_label.pack(pady=10)
        self.site_entry = tk.Entry(root, width=30)
        self.site_entry.pack(pady=5)

        # Label et champs de texte pour le mot de passe
        self.password_label = tk.Label(root, text="Mot de passe:")
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(root, width=30, show="*")  # Le show="*" masque le mot de passe
        self.password_entry.pack(pady=5)

        # Bouton pour générer un mot de passe
        self.generate_button = tk.Button(root, text="Générer un mot de passe", command=self.generate_password)
        self.generate_button.pack(pady=10)

        # Bouton pour ajouter le mot de passe
        self.add_button = tk.Button(root, text="Ajouter le mot de passe", command=self.add_password)
        self.add_button.pack(pady=20)

        # Liste affichant les mots de passe ajoutés (ici, temporaire, pas encore reliée à la base de données)
        self.password_listbox = tk.Listbox(root, width=50, height=5)
        self.password_listbox.pack(pady=10)

    def add_password(self):
        # Récupère les valeurs des champs de texte
        site = self.site_entry.get()
        password = self.password_entry.get()

        # Validation : vérifier que les champs ne sont pas vides
        if not site or not password:
            messagebox.showwarning("Champs vides", "Veuillez remplir tous les champs.")
            return

        # Ajouter le mot de passe à la liste (en tant que tuple : (nom du site, mot de passe))
        self.password_list.append((site, password))

        # Mettre à jour l'affichage de la liste
        self.update_password_list()

        # Effacer les champs de saisie après ajout
        self.site_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

        messagebox.showinfo("Mot de passe ajouté", f"Mot de passe pour '{site}' ajouté avec succès.")

    def generate_password(self):
        # Générer un mot de passe de longueur 12 (tu peux changer cette valeur selon tes besoins)
        generated_password = generatePassword(12)
        # Afficher le mot de passe généré dans le champ de mot de passe
        self.password_entry.delete(0, tk.END)  # Effacer le champ de saisie
        self.password_entry.insert(0, generated_password)  # Mettre le mot de passe généré dans le champ

    def update_password_list(self):
        # Vide la liste pour la mettre à jour
        self.password_listbox.delete(0, tk.END)

        # Afficher tous les mots de passe ajoutés dans la liste (version masquée)
        for site, password in self.password_list:
            masked_password = "*" * len(password)  # Masquer le mot de passe
            self.password_listbox.insert(tk.END, f"{site}: {masked_password}")
        
        # Lier un événement de clic pour chaque mot de passe dans la liste
        self.password_listbox.bind("<ButtonRelease-1>", self.copy_password)

    def copy_password(self, event):
        # Récupérer l'élément sélectionné
        selection = self.password_listbox.curselection()
        if selection:
            index = selection[0]
            site, password = self.password_list[index]
            
            # Copier le mot de passe dans le presse-papier
            pyperclip.copy(password)
            messagebox.showinfo("Copie", f"Le mot de passe pour '{site}' a été copié dans le presse-papier.")

# Créer la fenêtre principale
root = tk.Tk()
app = PasswordManagerApp(root)

# Lancer l'interface
root.mainloop()
