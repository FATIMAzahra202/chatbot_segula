import streamlit as st
from ai_gemini import ask_gemini
from datetime import datetime
import pandas as pd
import os
import re
import base64
import tempfile
import fitz  # PyMuPDF

# ✅ Logo + titre
def show_logo_and_title():
    st.markdown("""
        <div style='text-align:center; margin-top:20px; margin-bottom:0px;'>
            <img src='data:image/png;base64,{}' style='width:180px;' alt='Logo SEGULA'/>
        </div>
    """.format(get_encoded_logo()), unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:#1e88e5; margin-top:10px;'>🤖 Chatbot RH SEGULA Technologies</h2>", unsafe_allow_html=True)

def get_encoded_logo():
    with open("assets/SEGULA_Technologies_logo_DB.jpg", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# 🔤 Nettoyage
def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# ❓ FAQ de base
base_faq = {
    "quels sont les horaires de travail": "Les horaires standards sont de 9h à 17h du lundi au vendredi.",
    "comment poser un congé": "Vous devez faire la demande via l’intranet RH ou contacter votre manager.",
    "quels sont les avantages sociaux": "SEGULA offre mutuelle, transport, tickets resto, etc."
}

# ✅ Page principale
def dashboard():
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Vous devez vous connecter.")
        st.session_state.page = "login"
        st.stop()

    show_logo_and_title()
    st.markdown(f"👤 Connecté en tant que : `{st.session_state.user_email}`")

    if st.button("🚪 Déconnexion"):
        st.session_state.clear()
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("🗑️ Vider la conversation"):
        st.session_state.messages = []
        if os.path.exists("chat_log.xlsx"):
            os.remove("chat_log.xlsx")
        st.rerun()

    # 📎 Upload fichier
    st.markdown("### 📎 Uploader un fichier (PDF ou TXT)")
    uploaded_file = st.file_uploader("Sélectionner un fichier", type=["pdf", "txt"])

    if uploaded_file:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if file_ext == "txt":
            st.session_state.doc_content = uploaded_file.read().decode("utf-8")
            st.success(f"✅ Fichier TXT chargé : {uploaded_file.name}")

        elif file_ext == "pdf":
            try:
                pdf_bytes = uploaded_file.read()
                temp_path = os.path.join(tempfile.gettempdir(), f"temp_{uploaded_file.name}")

                with open(temp_path, "wb") as f:
                    f.write(pdf_bytes)

                doc = fitz.open(temp_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()

                st.session_state.doc_content = text
                st.success(f"✅ Fichier PDF chargé : {uploaded_file.name}")

            except Exception as e:
                st.error(f"❌ Erreur lecture PDF : {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    # 💬 Affichage conversation
    for msg in st.session_state.messages:
        align = "margin-left:auto;" if msg["role"] == "user" else "margin-right:auto;"
        bg = "#1e88e5" if msg["role"] == "user" else "#f1f1f1"
        color = "#fff" if msg["role"] == "user" else "#000"
        label = "👤 Vous" if msg["role"] == "user" else "🤖 Bot"
        st.markdown(f"""
            <div style='background:{bg}; color:{color}; padding:10px 15px;
                        border-radius:12px; margin:10px 0; max-width:75%; {align}'>
                {label}: {msg['content']}
            </div>
        """, unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Votre message", placeholder="Posez votre question RH...")
        submitted = st.form_submit_button("Envoyer")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        clean_input = normalize(user_input)

        matched = None
        for question in base_faq:
            if normalize(question) == clean_input:
                matched = base_faq[question]
                break

        if matched:
            response = matched
        else:
            try:
                if "doc_content" in st.session_state:
                    question = f"{user_input}\n\nVoici le contenu du document :\n{st.session_state.doc_content}"
                else:
                    question = user_input
                response = ask_gemini(question)
            except Exception:
                response = "❌ Une erreur est survenue avec Gemini."

        st.session_state.messages.append({"role": "bot", "content": response})

        df = pd.DataFrame([
            {"Rôle": m["role"], "Message": m["content"], "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            for m in st.session_state.messages
        ])
        df.to_excel("chat_log.xlsx", index=False)
        st.rerun()

    if os.path.exists("chat_log.xlsx"):
        with open("chat_log.xlsx", "rb") as f:
            st.download_button("📥 Télécharger l'historique", f, file_name="chat_log.xlsx")

    # 📊 Statistiques si admin
    if st.session_state.user_role == "admin":
        st.subheader("📊 Statistiques d'utilisation")
        if os.path.exists("chat_log.xlsx"):
            df = pd.read_excel("chat_log.xlsx")
            st.write(df)
            st.metric("💬 Total messages", len(df))
            st.metric("👤 Utilisateur", len(df[df["Rôle"] == "user"]))
            st.metric("🤖 Bot", len(df[df["Rôle"] == "bot"]))
            df["Date"] = pd.to_datetime(df["Date"])
            df["Jour"] = df["Date"].dt.date
            st.line_chart(df.groupby("Jour").count()["Message"])
