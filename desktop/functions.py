#importations de librairies
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
import base64
import random 
import string
import os


#Génération de mots de passes 
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

#génération de clé 

def generate_key():
    """Génère une clé AES-256 aléatoire"""
    return os.urandom(32)  # 32 octets = 256 bits

#chiffrement du mot de passe avec la clé
def encrypt(donnees, cle):
    """Chiffre les données"""
    if isinstance(cle, int):
        # Convertir l'entier en bytes si nécessaire
        cle = cle.to_bytes(32, byteorder='big')
    
    # Générer un vecteur d'initialisation
    iv = os.urandom(16)
    
    # Créer le chiffreur
    cipher = AES.new(cle, AES.MODE_CBC, iv)
    
    # Chiffrer les données
    donnees_paddees = pad(donnees.encode(), AES.block_size)
    donnees_chiffrees = cipher.encrypt(donnees_paddees)
    
    # Combiner IV et données chiffrées
    return base64.b64encode(iv + donnees_chiffrees).decode()

#déchiffrement du mot de passe avec la clé 
def decrypt(donnees_chiffrees, cle):
    """Déchiffre les données"""
    if isinstance(cle, int):
        # Convertir l'entier en bytes si nécessaire
        cle = cle.to_bytes(32, byteorder='big')
    
    # Décoder de base64
    donnees_bytes = base64.b64decode(donnees_chiffrees)
    
    # Extraire le vecteur d'initialisation
    iv = donnees_bytes[:16]
    ciphertext = donnees_bytes[16:]
    
    # Créer le déchiffreur
    cipher = AES.new(cle, AES.MODE_CBC, iv)
    
    # Déchiffrer et supprimer le padding
    donnees_dechiffrees = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return donnees_dechiffrees.decode()





#test
cle = generate_key()

# Chiffrer
message = "Hello"
chiffre = encrypt(message, cle)

# Déchiffrer
dechiffre = decrypt(chiffre, cle)

print(generate_key())
print(message ,"\n", chiffre, "\n", dechiffre )
#Connexion à la base de donnée