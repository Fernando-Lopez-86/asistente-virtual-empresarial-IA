import streamlit as st
import os
import docx
import pandas as pd
import spacy
import fitz  # PyMuPDF
import re
import openpyxl

# Cargar el modelo de spaCy para español 
# Descargar el modelo de lenguaje español
# !python -m spacy download es_core_news_sm - VER INSTALACION EN SCRIPT O ALTERNATIVA
nlp = spacy.load('es_core_news_sm')

def extract_text_pdf(file_path):
    text = ''
    with fitz.open(file_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            text += page.get_text("text")
    return text

def extract_text_word(file_path):
    doc = docx.Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def extract_text_excel(file_path):
    xls = pd.read_excel(file_path)
    # Convertir DataFrame a string, y despues limpia el texto ignorando valores NaN que se repiten mucho
    text = xls.fillna('').astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')
    return text

# Eliminar caracteres no deseados y normalizar espacios
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# Creacion de tokens
def create_tokens(text):
    doc = nlp(text)
    tokens_normalizados = []

    for token in doc:
        if not token.is_stop and not token.is_punct and token.text.strip():
            tokens_normalizados.append(token.lemma_)

    print("Texto:", text.strip())
    print("Tokens normalizados:", tokens_normalizados)
    return tokens_normalizados

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
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_word(file_path)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        text = extract_text_excel(file_path)
    else:
        st.sidebar.error("Tipo de archivo no soportado.")
        text = None

    if text:
        text = clean_text(text)
        tokens = create_tokens(text)

    st.sidebar.success("Archivo subido y procesado correctamente.")

# Campo de texto para realizar preguntas
st.title("Asistente Virtual Empresarial IA")
query = st.text_input("Pregunta:")

if st.button("Buscar"):
    st.write(f"Buscando resultados para: {query}")
