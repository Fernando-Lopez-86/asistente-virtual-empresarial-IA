
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
# max_chars = 200


# def split_text_spacy(text, max_sentences=3, max_chars=600):
#     """
#     Divide el texto en fragmentos dinámicos utilizando spaCy, priorizando la coherencia semántica.
#     Se generan fragmentos basados en un número máximo de oraciones o un límite de caracteres.
    
#     :param text: Texto a dividir.
#     :param max_sentences: Número máximo de oraciones por fragmento.
#     :param max_chars: Número máximo de caracteres por fragmento.
#     :return: Lista de fragmentos dinámicos.
#     """
#     doc = nlp(text)  # Procesar el texto con spaCy
#     sentences = [sent.text.strip() for sent in doc.sents]  # Dividir el texto en oraciones
#     chunks = []
#     current_chunk = []
#     current_length_chars = 0

#     for sentence in sentences:
#         chars_in_sentence = len(sentence)

#         if (len(current_chunk) >= max_sentences or current_length_chars + chars_in_sentence > max_chars): # Comprobar si agregar esta oración excede el límite de caracteres o de oraciones
#             chunks.append(" ".join(current_chunk))   # Añadir el fragmento actual a la lista
#             current_chunk = []
#             current_length_chars = 0

#         current_chunk.append(sentence)  # Añadir la oración al fragmento actual
#         current_length_chars += chars_in_sentence

#     if current_chunk:  # Añadir el último fragmento si quedó algo pendiente
#         chunks.append(" ".join(current_chunk))

#     return chunks


def split_text_spacy(text, min_tokens=50, max_tokens=150):
    """
    Divide el texto en fragmentos basados en oraciones con spaCy,
    asegurando que cada fragmento tenga un número adecuado de tokens.
    """
    doc = nlp(text)  # Procesar el texto con spaCy
    chunks = []
    current_chunk = []
    current_length = 0

    # Recorrer cada oración
    for sent in doc.sents:
        sent_tokens = len(sent.text.split())  # Contar tokens en la oración
        
        # Si agregar esta oración excede el tamaño máximo
        if current_length + sent_tokens > max_tokens:
            if current_chunk:  # Guardar el fragmento actual
                chunks.append(" ".join(current_chunk))
            current_chunk = [sent.text]  # Iniciar un nuevo fragmento
            current_length = sent_tokens
        else:
            current_chunk.append(sent.text)
            current_length += sent_tokens

        # Si el fragmento es demasiado pequeño, extiéndelo al siguiente ciclo
        if current_length < min_tokens:
            continue

    # Agregar el último fragmento
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def create_embeddings(text_chunks):    # ESTE ERA EL ORIGINAL
    # Genera embeddings para cada fragmento de texto.
    return [model.encode(chunk) for chunk in text_chunks]


# Inicializa el índice FAISS para realizar búsquedas basadas en similitud.
# Crea un índice IndexFlatL2 (distancia euclidiana) de dimensión 384.
# Si el índice FAISS existe en el archivo especificado, lo carga con faiss.read_index.
# Si existe un archivo de metadatos (metadata.json), lo carga; de lo contrario, crea un diccionario vacío.
# index: Índice FAISS (nuevo o cargado).
# metadata: Diccionario con los metadatos asociados a los documentos.
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


# Resumen
    # Objetivo: Este código prepara el procesamiento de texto y la búsqueda semántica mediante embeddings y FAISS.
# Flujo:
    # Divide un texto en fragmentos coherentes con split_text_spacy.
    # Convierte los fragmentos en embeddings con create_embeddings.
    # Inicializa un índice FAISS y carga los metadatos para búsquedas posteriores.
    # Este enfoque es esencial para manejar grandes cantidades de texto, facilitando búsquedas rápidas y precisas basadas en similitud semántica.