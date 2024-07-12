import streamlit as st
import os
from PyPDF2 import PdfReader
import docx
import pandas as pd


def extract_text_pdf(file_path):
    with open(file_path, 'rb') as f:
        pdf = PdfReader(f)
        text = ''
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_word(file_path):
    doc = docx.Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def extract_text_excel(file_path):
    xls = pd.read_excel(file_path)
    text = xls.to_string(index=False)
    return text


# Carpeta donde almacenamos los documentos de la empresa
uploaded_files = "data/files/"   # Quitar ruta hardcodeada - Revisar
if not os.path.exists(uploaded_files):
    os.makedirs(uploaded_files)

# Barra lateral de Streamlit para subir y listar los documentos
st.sidebar.title("Subir Archivos")
uploaded_file = st.sidebar.file_uploader("Elige un archivo", type=['pdf', 'docx', 'xlsx'])

# Guarda el documento subido en la carpeta data/files, y despues lo procesa dependiendo del tipo de archivo
if uploaded_file:
    file_path = os.path.join(uploaded_files, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Procesar el archivo pdf subido para crear los embeddings - Revisar tipo de archivos OJO!!
    if uploaded_file.type == "application/pdf":
        text = extract_text_pdf(file_path)
    elif uploaded_file.type == "application/doc":
        text = extract_text_word(file_path)
    elif uploaded_file.type == "application/xls":
        text = extract_text_excel(file_path)

    st.sidebar.success("Archivo subido y procesado correctamente.")

# Campo de texto para realizar preguntas
st.title("Asistente Virtual Empresarial IA")
query = st.text_input("Pregunta:")

if st.button("Buscar"):
    st.write(f"Buscando resultados para: {query}")
