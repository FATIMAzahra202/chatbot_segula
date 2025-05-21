-- Création de la base de données
CREATE DATABASE IF NOT EXISTS segula_chatbot;
USE segula_chatbot;

-- Création de la table users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'employee') DEFAULT 'employee'
);

-- Ajouter un utilisateur admin (mot de passe hashé de 'admin123')
INSERT INTO users (email, password, role) VALUES (
    'admin@segula.com',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'admin'
);
