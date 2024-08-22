import streamlit as st
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env con el modulo dotenv
def load_config():
    load_dotenv()

    # Streamlit trae por defecto un boton arriba a la derecha de que dice Deploy, para ocultarlo hay que modificar el CSS a traves de un markdown
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """, unsafe_allow_html=True)

# Con streamlit se complico la eliminacion de documentos de la base FAISS, por esto hay que inicializar variables de sesión para identificar los estados - OJO
def initialize_session_state():
    if 'uploaded_files' not in st.session_state:
        st.session_state["uploaded_files"] = []

    if 'files_to_delete' not in st.session_state:
        st.session_state.files_to_delete = set()

    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0


