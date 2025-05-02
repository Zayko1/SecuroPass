CREATE DATABASE IF NOT EXISTS securopass CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE securopass;

-- TABLE 1 : Clés maîtres (utilisateurs)
CREATE TABLE cles_maitres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    cle_chiffrement VARBINARY(256) NOT NULL,
    double_auth BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 2 : Mots de passe sauvegardés
CREATE TABLE mots_de_passe (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT NOT NULL,
    titre VARCHAR(100) NOT NULL,             -- Exemple : "Compte Gmail"
    identifiant VARCHAR(150) NOT NULL,       -- Email ou nom d'utilisateur
    mot_de_passe_chiffre VARBINARY(512) NOT NULL,
    site_web VARCHAR(255),
    niveau_securite VARCHAR(10),             -- Faible, Moyen, Fort
    notes TEXT,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES cles_maitres(id) ON DELETE CASCADE
);

-- TABLE 3 : Journalisation des actions
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_utilisateur INT,
    action VARCHAR(255) NOT NULL,         -- Exemple : "Connexion réussie"
    adresse_ip VARCHAR(45),               -- IPv4 ou IPv6
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilisateur) REFERENCES cles_maitres(id) ON DELETE SET NULL
);