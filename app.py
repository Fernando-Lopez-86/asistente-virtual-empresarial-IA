import streamlit as st
import os

# Carpeta donde almacenamos los documentos de la empresa
uploaded_files = "data/files/"
if not os.path.exists(uploaded_files):
    os.makedirs(uploaded_files)

# Barra lateral de Streamlit para subir y listar los documentos
st.sidebar.title("Subir Archivos")
uploaded_file = st.sidebar.file_uploader("Elige un archivo", type=['pdf', 'docx', 'xlsx'])

if uploaded_file:
    file_path = os.path.join(uploaded_files, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success("Archivo subido y procesado correctamente.")

# Campo de texto para realizar preguntas
st.title("Asistente Virtual Empresarial IA")
query = st.text_input("Pregunta:")

if st.button("Buscar"):
    st.write(f"Buscando resultados para: {query}")
