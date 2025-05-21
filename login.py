import streamlit as st
import sqlite3
from security import hash_password, check_password
from connection import connect_db

def login():
    st.title("🔐 Connexion")

    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if not email or not password:
            st.warning("⚠️ Veuillez remplir tous les champs.")
        else:
            conn = connect_db()
            conn.row_factory = sqlite3.Row  # ✅ pour que chaque ligne soit un dict
            cursor = conn.cursor()

            # Vérifie si l'utilisateur existe
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and check_password(password, user["password"]):
                st.success("✅ Connexion réussie ! Bienvenue.")
                st.session_state.logged_in = True
                st.session_state.user_email = user["email"]
                st.session_state.user_role = user["role"]
                st.session_state.page = "dashboard"  # redirection automatique
            else:
                st.error("❌ Email ou mot de passe incorrect.")

            cursor.close()
            conn.close()

    if st.button("Créer un compte"):
        st.session_state.page = "signup"
