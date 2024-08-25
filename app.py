import streamlit as st
from http.cookies import SimpleCookie
from config import load_config, initialize_session_state
from modules.ui import display_app_content
from modules.database import create_database
from login.session_management import initialize_session, is_logged_in, display_logout_button
from login.login import display_login_form

st.set_page_config(page_title="Asistente Virtual Empresarial IA\n", page_icon="🔎", layout="centered")

# CSS personalizado para cambiar la fuente del título
custom_css = """
<style>

h1 {
    font-family: 'Calibri', sans-serif;  /* Cambia 'Arial' por la fuente que desees */
    font-size: 46px;  /* Ajusta el tamaño de la fuente */
    color: #4B4B4B;  /* Cambia el color del texto */
    text-align: left;  /* Alineación del texto */
}

.custom-text {
    font-family: 'Calibri', sans-serif; /* Cambia 'Arial' por la fuente que desees */
    font-size: 28px; /* Ajusta el tamaño de la fuente */
    color: #333333; /* Cambia el color del texto */
    font-weight: bold; /* Hace el texto en negrita */
}

label[for="input_query"] {
    font-weight: bold;
    font-size: 1.3em; /* Aumenta ligeramente el tamaño del texto */
    color: #333; /* Color gris oscuro para el texto */
}

</style>
"""

# Aplica el CSS usando st.markdown
st.markdown(custom_css, unsafe_allow_html=True)


# Cargar variables de entorno
load_config()

# Inicializar el estado de la sesión para eliminacion de documentos en streamlit
initialize_session_state()

# Crear la base de datos (si no existe)
create_database()

# Inicializar sesión
initialize_session()

# Pantalla de Login o Contenido Principal
if not is_logged_in():
    user = display_login_form()
    if user:
        st.session_state['logged_in'] = True
        st.session_state['username'] = user  
        st.session_state['role'] = user[3]
        st.rerun()
else:
    display_logout_button()
    display_app_content()