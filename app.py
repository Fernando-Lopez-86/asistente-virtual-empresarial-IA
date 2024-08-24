import streamlit as st
from http.cookies import SimpleCookie
from config import load_config, initialize_session_state
from modules.ui import display_app_content
from modules.database import create_database
from login.session_management import initialize_session, is_logged_in, display_logout_button
from login.login import display_login_form

# CSS avanzado para cambiar el color de fondo y la barra lateral
custom_css = """
<style>
body {
    background-color: #2E2E6E; /* Fondo de la página */
    color: #FFFFFF; /* Color del texto */
}
.sidebar .sidebar-content {
    background-color: #4B4B4B; /* Fondo de la barra lateral */
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
        # st.session_state['username'] = user  # Guarda el nombre de usuario en la sesión
        st.rerun()
else:
    display_logout_button()
    display_app_content()