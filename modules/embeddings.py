import numpy as np
import faiss
import os
import json
from sentence_transformers import SentenceTransformer

# SentenceTransformer es una clase proporcionada por la biblioteca sentence-transformers, la cual es una extension de transformers de Hugging Face
# Esta biblioteca esta diseñada para generar representaciones vectoriales (embeddings) de frases y oraciones para tareas de procesamiento de lenguaje natural (NLP), 
# como la búsqueda semántica, la clasificacion de textos, detección de similitud semántica, etc.
# all-MiniLM-L6-v2 es un modelo de embeddings desarrollado por Microsoft que se encuentra disponible en la biblioteca sentence-transformers
# Este modelo está diseñado para ser rápido y eficiente, generando embeddings de alta calidad a partir de textos.
model = SentenceTransformer('all-MiniLM-L6-v2')
uploaded_files = "data/files/"         # Carpeta donde almacenamos los documentos de la empresa
metadata_file = 'data/metadata.json'   # Archivo donde almacenamos los metadatos de los documentos
faiss_index_path = 'data/faiss_index.index'
dimension = 384    # Dimensión de los embeddings que se van a utilizar. En este caso cada vector de embeddings tiene 384 dimensiones

# Creacion de tokens - 3 opciones: con el modulo spacy, con el modulo tiktoken propio de openia, con el modulo SentenceTransformer
# Creacion de embeddings - 3 opciones: con el modulo numpy, con el endpoint de openia, con el modulo SentenceTransformer
# Se reemplaza tiktoken por el modelo SentenceTransformers de Hugging Face, tokeniza y crea los embeddins en el mismo paso
# La funcion model.encode(text) toma el texto y lo convierte en un vector de embeddings. 
# El resultado lo guarda en una matriz de nombre embeddings, la cual es una matriz numpy de dimensión (1, 384) en el caso del modelo all-MiniLM-L6-v2
def create_embeddings(text):
    embeddings = model.encode(text)
    return np.array(embeddings, dtype=np.float32).reshape(1, -1)


# Inicializar FAISS
# faiss.IndexFlatL2(dimension) crea un nuevo indice FAISS utilizando la mtrica L2 (distancia euclidiana). 
# Esto es adecuado para encontrar similitudes entre vectores de alta dimensión. 
def init_faiss_index():
    index = faiss.IndexFlatL2(dimension)      # Crear un nuevo índice FAISS con métrica L2 (distancia euclidiana)
    if os.path.exists(faiss_index_path):      # Si el archivo del indice FAISS existe, carga el indice desde el archivo 
        index = faiss.read_index(faiss_index_path)   
    if os.path.exists(metadata_file):            # Si el archivo de metadatos existe, carga los metadatos desde el archivo JSON
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    return index, metadata



