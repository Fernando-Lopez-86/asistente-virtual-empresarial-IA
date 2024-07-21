import streamlit as st
from modules.config import load_config, initialize_session_state
from modules.files import handle_file_upload
from modules.ui import display_uploaded_files, display_embeddings
from modules.search import search_and_display_results
from modules.embeddings import init_faiss_index

# Cargar variables de entorno
load_config()

# Inicializar el estado de la sesión para eliminacion de documentos en streamlit
initialize_session_state()

# Inicializar FAISS
index, metadata = init_faiss_index()

# Configurar la barra lateral de streamlit para listar, eliminar y subir documentos
st.sidebar.title("Subir Archivos")
uploaded_file = st.sidebar.file_uploader("Elige un archivo", type=['pdf', 'docx', 'xlsx'], key=st.session_state.get("file_uploader_key", 0), label_visibility="hidden")

# Gestionar la subida de archivos
if uploaded_file and uploaded_file.name not in st.session_state.get("uploaded_files", []):
    handle_file_upload(uploaded_file, index, metadata)

# Mostrar archivos subidos y permitir eliminación
display_uploaded_files(index, metadata)

# Campo de texto para realizar preguntas
st.title("Asistente Virtual Empresarial IA")
query = st.text_input("Pregunta:")

# Buscar y mostrar resultados
if st.button("Buscar"):
    search_and_display_results(query, index, metadata)

# Mostrar detalles de los embeddings almacenados en FAISS
display_embeddings(metadata, index)