import streamlit as st
from login.login_handler import login_user

def display_login_form():
    st.title("🤖💼 Asistente Virtual Empresarial\n")
    st.markdown("#### Iniciar Sesión")
    username = st.text_input("**Usuario**")
    password = st.text_input("**Contraseña**", type="password")
    if st.button("Iniciar Sesión"):
        user = login_user(username, password)
        if user:
            st.success("Login exitoso!")
            return user
        else:
            st.error("Usuario o contraseña incorrectos")
    return None