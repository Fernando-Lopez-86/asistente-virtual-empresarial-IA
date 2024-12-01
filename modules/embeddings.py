import numpy as np
import faiss
import os
import json
from sentence_transformers import SentenceTransformer
import spacy

model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("es_core_news_sm")  # Cargamos spaCy para la división de texto

uploaded_files = "data/files/"
metadata_file = 'data/metadata.json'
faiss_index_path = 'data/faiss_index.index'
dimension = 384
chunk_size = 75
max_chars=200

# Divide el texto en fragmentos coherentes utilizando spaCy.
def split_text_spacy(text, chunk_size=75):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        words_in_sentence = len(sentence.split())
        if current_length + words_in_sentence > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += words_in_sentence

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def create_embeddings(text_chunks):
    # Genera embeddings para cada fragmento de texto.
    return [model.encode(chunk) for chunk in text_chunks]

# Divide el texto en fragmentos basados en un límite de caracteres.
# :param text: Texto completo del documento.
# :param max_chars: Número máximo de caracteres por fragmento.
# :return: Lista de fragmentos de texto.
def split_text_into_chunks_by_characters(text, max_chars=200):
    chunks = []
    while len(text) > max_chars:
        split_index = text[:max_chars].rfind(' ')  # Encuentra el último espacio antes del límite
        if split_index == -1:  # Si no hay espacio, corta directamente
            split_index = max_chars
        chunks.append(text[:split_index])
        text = text[split_index:].strip()  # Elimina espacios iniciales en el resto del texto
    if text:
        chunks.append(text)
    return chunks

def split_text_into_chunks(text, chunk_size=10):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def init_faiss_index():
    index = faiss.IndexFlatL2(dimension)
    if os.path.exists(faiss_index_path):
        index = faiss.read_index(faiss_index_path)
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    return index, metadata