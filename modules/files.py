import os
import uuid
import json
import streamlit as st
import docx
import pandas as pd
import fitz
from modules.embeddings import create_embeddings, faiss_index_path, metadata_file
import re
import faiss
import numpy as np

# Funciones para la extraccion de texto de los archivos pdf, doc, xls
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
    text = xls.fillna('').astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')
    return text

# Eliminar caracteres no deseados y normalizar espacios
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# Funcion para subir archivos
def handle_file_upload(uploaded_file, index, metadata):
    file_id = str(uuid.uuid4())
    file_path = os.path.join("data/files", uploaded_file.name)

    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    if uploaded_file.type == "application/pdf":
        text = extract_text_pdf(file_path)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_word(file_path)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        text = extract_text_excel(file_path)
    else:
        st.sidebar.error("Tipo de archivo no soportado.")
        return

    text = clean_text(text)
    embeddings = create_embeddings(text)
    index.add(embeddings)
    faiss.write_index(index, faiss_index_path)

    metadata[file_id] = {
        'file_name': uploaded_file.name,
        'embedding_start_idx': index.ntotal - 1,
        'embedding_end_idx': index.ntotal,
        'text': text 
    }
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

    st.session_state["uploaded_files"] = uploaded_file.name
    st.rerun()

def delete_file(file_id, file_info, index, metadata):
    start_idx = file_info['embedding_start_idx']
    end_idx = file_info['embedding_end_idx']
    index.remove_ids(np.arange(start_idx, end_idx, dtype=np.int64))
    faiss.write_index(index, faiss_index_path)

    del metadata[file_id]
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)
    
    os.remove(os.path.join("data/files", file_info['file_name']))
    st.session_state["file_uploader_key"] += 1
    st.rerun()