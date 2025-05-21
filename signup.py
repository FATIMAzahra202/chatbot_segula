import streamlit as st
from db.connection import connect_db
from utils.security import hash_password
from db.connection import connect_db

conn = connect_db()

def signup():
    st.title("📝 Créer un compte")

    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")

    if st.button("Créer mon compte"):
        if not email or not password or not confirm_password:
            st.warning("⚠️ Veuillez remplir tous les champs.")
        elif password != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas.")
        else:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                st.warning("⚠️ Cet email existe déjà.")
            else:
                hashed = hash_password(password)
                cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", (email, hashed, 'employee'))
                conn.commit()
                st.success("✅ Compte créé avec succès. Vous pouvez vous connecter.")
                st.session_state.page = "login"
            cursor.close()
            conn.close()

    if st.button("J'ai déjà un compte"):
        st.session_state.page = "login"
