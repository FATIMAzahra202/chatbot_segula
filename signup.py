import streamlit as st
import sqlite3
from security import hash_password
from connection import connect_db

def signup():
    st.title("📝 Création de compte")

    email = st.text_input("Email").strip().lower()
    password = st.text_input("Mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")
    role = st.selectbox("Rôle", ["user", "admin"])

    if st.button("Créer le compte"):
        if not email or not password or not confirm_password:
            st.warning("⚠️ Tous les champs sont obligatoires.")
        elif password != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas.")
        else:
            conn = connect_db()
            cursor = conn.cursor()

            # Vérifie si l'email existe déjà
             cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
             if cursor.fetchone():
                 st.error("❌ Un compte avec cet email existe déjà.")

            else:
                hashed_pw = hash_password(password)
                cursor.execute(
                    "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                    (email, hashed_pw, role)
                )
                conn.commit()
                st.success("✅ Compte créé avec succès. Vous pouvez maintenant vous connecter.")
            
            cursor.close()
            conn.close()

    if st.button("Retour à la connexion"):
        st.session_state.page = "login"
