import streamlit as st
from login import login
from signup import signup
from dashboard import dashboard

st.set_page_config(page_title="SEGULA Chatbot RH")

# Initialisation session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# Routage
if st.session_state.page == "login":
    login()
elif st.session_state.page == "signup":
    signup()
elif st.session_state.logged_in:
    dashboard()
else:
    st.warning("🔐 Vous devez vous connecter.")

