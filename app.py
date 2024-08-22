import streamlit as st
from modules.config import load_config, initialize_session_state
from modules.ui import display_login_form, display_app_content
from modules.database import create_database, get_user, add_user
from modules.authentication import login_user, hash_password

# Cargar variables de entorno
load_config()

# Inicializar el estado de la sesión para eliminacion de documentos en streamlit
initialize_session_state()

# Crear la base de datos (si no existe)
create_database()

# Función para mostrar el botón de cerrar sesión en la parte superior derecha
def logout_button():
    st.markdown(
        """
        <style>
        .logout-button {
            position: fixed;
            top: 60px;
            right: 20px;
            background-color: #ff4b4b;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            z-index: 1000;
            border: none;
        }
        .logout-button:hover {
            background-color: #ff3333;
        }
        </style>
        <form action="?logout=true" method="get">
            <button class="logout-button" type="submit">Cerrar Sesión</button>
        </form>
        """,
        unsafe_allow_html=True
    )

    if st.query_params.get("logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# Pantalla de Login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    user = display_login_form()
    if user:
        st.session_state['logged_in'] = True
        st.rerun()
else:
    logout_button()
    display_app_content()