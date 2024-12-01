import os
import uuid
import json
import streamlit as st
import docx
import pandas as pd
import fitz
import re
from modules.embeddings import create_embeddings, faiss_index_path, metadata_file, split_text_into_chunks, split_text_into_chunks_by_characters, split_text_spacy
import faiss
import numpy as np
import unicodedata

def extract_text_pdf(file_path):
    text = ''
    with fitz.open(file_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            text += page.get_text("text")
    return text

def extract_text_word(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_excel(file_path):
    xls = pd.read_excel(file_path)
    return xls.fillna('').astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep=' ')

def clean_text(text):
    # Normaliza el texto a la forma NFD
    normalized = unicodedata.normalize('NFD', text)
    # Filtra los caracteres diacriticos (categoria 'Mn')
    text_normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    text = re.sub(r'\s+', ' ', text_normalized)
    text = text.strip()
    return ' '.join(text.split()).strip()

def handle_file_upload(uploaded_file, index, metadata):
    try:
        # Verificar si el archivo ya existe en los metadatos
        for file_id, file_info in metadata.items():
            if file_info['file_name'] == uploaded_file.name:
                st.sidebar.warning("El archivo ya está subido.")
                return

        file_id = str(uuid.uuid4())  # Generar un UUID único para el archivo
        file_path = os.path.join("data/files", uploaded_file.name)

        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Identificar el tipo de archivo y extraer el texto
        if uploaded_file.type == "application/pdf":
            text = extract_text_pdf(file_path)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_word(file_path)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            text = extract_text_excel(file_path)
        else:
            st.sidebar.error("Tipo de archivo no soportado.")
            return

        # Limpiar y dividir el texto
        text = clean_text(text)
        # chunks = split_text_into_chunks(text, chunk_size=200)
        # chunks = split_text_into_chunks_by_characters(text, max_chars=200)
        chunks = split_text_spacy(text, chunk_size=75)

        # Generar embeddings y añadir al índice FAISS
        chunk_embeddings = create_embeddings(chunks)
        for embedding in chunk_embeddings:
            index.add(np.array(embedding).reshape(1, -1))

        faiss.write_index(index, faiss_index_path)

        # Guardar los datos del archivo en metadata usando el UUID
        metadata[file_id] = {
            "file_name": uploaded_file.name,
            "embedding_start_idx": index.ntotal - len(chunks),
            "embedding_end_idx": index.ntotal,
            "text_chunks": chunks
        }

        # Actualizar el archivo metadata.json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        st.session_state["uploaded_files"].append(uploaded_file.name)
    except Exception as e:
        st.error(f"Error al subir el archivo: {str(e)}")

def delete_file(file_id, file_info, index, metadata):
    import os
    import json
    import numpy as np
    from modules.embeddings import faiss_index_path, metadata_file

    try:
        start_idx = file_info['embedding_start_idx']
        end_idx = file_info['embedding_end_idx']

        # Eliminar embeddings del índice FAISS
        ids_to_remove = np.arange(start_idx, end_idx, dtype=np.int64)
        index.remove_ids(ids_to_remove)
        faiss.write_index(index, faiss_index_path)

        # Actualizar el archivo de metadatos
        del metadata[file_id]
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        # Eliminar el archivo físicamente
        file_path = os.path.join("data/files", file_info['file_name'])
        if os.path.exists(file_path):
            os.remove(file_path)

        # Actualizar el estado de la sesión
        st.session_state["file_uploader_key"] += 1

    except Exception as e:
        st.error(f"Error al eliminar el archivo: {str(e)}")