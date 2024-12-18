
import os
import uuid
import json
import streamlit as st
import docx
import pandas as pd
import fitz
import re
from modules.embeddings import create_embeddings, faiss_index_path, metadata_file, dimension, split_text_spacy
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
        # Generar un UUID único para el archivo
        file_id = str(uuid.uuid4())  
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
        # chunks = split_text_spacy(text, max_sentences=3, max_chars=600)
        chunks = split_text_spacy(text, min_tokens=50, max_tokens=150)

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

        st.session_state["uploaded_files"] = uploaded_file.name

    except Exception as e:
        st.error(f"Error al subir el archivo: {str(e)}")


def delete_file(file_id, file_info, index, metadata):
    try:
        current_query = st.session_state.get("input_query", "")

        # Eliminar el archivo del metadata
        del metadata[file_id]

        # Renumerar los metadatos
        renumber_metadata(metadata)

        # Reconstruir el índice FAISS
        index = rebuild_faiss_index(metadata)

        # Guardar los metadatos actualizados
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        # Eliminar el archivo físicamente
        file_path = os.path.join("data/files", file_info['file_name'])
        if os.path.exists(file_path):
            os.remove(file_path)

        # Actualizar el estado de la sesión
        if "uploaded_files" in st.session_state and file_info["file_name"] in st.session_state["uploaded_files"]:
            st.session_state["uploaded_files"].remove(file_info["file_name"])

        # Forzar la recarga del file_uploader
        st.session_state["file_uploader_key"] += 1

        st.session_state["input_query"] = current_query

        st.rerun()

    except Exception as e:
        st.error(f"Error al eliminar el archivo: {str(e)}")


# Ajusta los índices de embeddings después de eliminar un archivo para mantener consistencia.
def renumber_metadata(metadata):
    """
    Renumera los índices de embeddings en metadata.json después de eliminar un archivo.
    :param metadata: Diccionario con los metadatos actuales.
    """
    current_idx = 0  # Índice inicial
    for file_info in metadata.values():
        num_embeddings = file_info["embedding_end_idx"] - file_info["embedding_start_idx"]
        file_info["embedding_start_idx"] = current_idx
        file_info["embedding_end_idx"] = current_idx + num_embeddings
        current_idx += num_embeddings


# Reconstruye el índice FAISS desde los embeddings almacenados en los metadatos.
def rebuild_faiss_index(metadata):
    """
    Reconstruye el índice FAISS desde los embeddings almacenados en los metadatos.
    :param metadata: Diccionario con los metadatos actuales.
    :return: Índice FAISS reconstruido.
    """
    # Crear un nuevo índice FAISS
    index = faiss.IndexFlatL2(dimension)
    all_embeddings = []

    for file_info in metadata.values():
        text_chunks = file_info["text_chunks"]
        chunk_embeddings = create_embeddings(text_chunks)
        all_embeddings.extend(chunk_embeddings)

    if all_embeddings:
        index.add(np.array(all_embeddings, dtype=np.float32))

    # Guardar el índice reconstruido
    faiss.write_index(index, faiss_index_path)
    return index

# Resumen
# Este archivo combina múltiples funcionalidades:
    # Extracción: Lee y convierte contenido de documentos a texto plano.
    # Procesamiento: Limpia y divide el texto en fragmentos semánticos.
    # Gestión de índices: Añade y elimina embeddings en FAISS.
    # Gestión de archivos: Interactúa con los metadatos y la interfaz de usuario.
# El enfoque es modular, asegurando flexibilidad y mantenibilidad del código. Si necesitas más detalles de alguna sección, no dudes en preguntar.