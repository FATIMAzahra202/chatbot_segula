import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="0000",  # ← remplace par ton mot de passe MySQL
        database="segula_chatbot"
    )
