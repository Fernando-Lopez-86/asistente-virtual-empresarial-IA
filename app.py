import streamlit as st
import os
import docx
import pandas as pd
## import spacy
import fitz  # PyMuPDF
import re
import openpyxl
import tiktoken
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import uuid
import json
from openai import OpenAI
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API key desde las variables de entorno
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=api_key,
)

# Cargar el modelo de spaCy para español 
# Descargar el modelo de lenguaje español
# !python -m spacy download es_core_news_sm - VER INSTALACION EN SCRIPT O ALTERNATIVA
## nlp = spacy.load('es_core_news_sm')

# Inicializar el tokenizador para el modelo GPT-4
#enc = tiktoken.get_encoding("cl100k_base")
model = SentenceTransformer('all-MiniLM-L6-v2')


# Carpeta donde almacenamos los documentos de la empresa
uploaded_files = "data/files/"   # Quitar ruta hardcodeada - Revisar
if not os.path.exists(uploaded_files):
    os.makedirs(uploaded_files)


# Archivo donde almacenamos los metadatos de los documentos
metadata_file = 'data/metadata.json'
if os.path.exists(metadata_file):
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
else:
    metadata = {}



# Inicializar FAISS
dimension = 384  # Dimensión de los embeddings, ajusta según sea necesario
index = faiss.IndexFlatL2(dimension)
faiss_index_path = 'data/faiss_index.index'
if os.path.exists(faiss_index_path):
    index = faiss.read_index(faiss_index_path)
    

# Estructura para almacenar los detalles de los documentos subidos
# document_details = []


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

# Creacion de tokens - 2 opciones: con el modulo spacy o con el modulo tiktoken propio de openia
# Creacion de embeddings - 2 opciones: con el modulo numpy o con el endpoint de openia
# Se reemplaza tiktoken por el modelo sentence-transformers de Hugging Face, tokeniza y crea los embeddins en el mismo paso
def create_embeddings(text):

    # doc = nlp(text)
    # tokens_normalizados = []
    # for token in doc:
        # if not token.is_stop and not token.is_punct and token.text.strip():
            # tokens_normalizados.append(token.lemma_)

    # response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    # embeddings = response['data'][0]['embedding']
    # return np.array(embeddings, dtype=np.float32).reshape(1, -1)

    #tokens = enc.encode(text)
    #decoded_tokens = [enc.decode([token]) for token in tokens]
    #grouped_tokens = [enc.decode(tokens[i:i+10]) for i in range(0, len(tokens), 10)]     # Agrupar tokens para mostrar mejor
    print("Texto:", text.strip())
    #print("Tokens:", tokens)
    #print("Tokens decode:", decoded_tokens)
    #print("Tokens agrupados:", grouped_tokens)
    #print("Embeddings:", np.array(tokens, dtype=np.float32).reshape(1, -1))
    #tokens = enc.encode(text)  # para probar tokenizar con tiktoken previo a enviarle el texto sentence-transformer
    embeddings = model.encode(text)
    print("Embeddings:", embeddings)
    print("Embeddings Numpt:", np.array(embeddings, dtype=np.float32).reshape(1, -1))
    return np.array(embeddings, dtype=np.float32).reshape(1, -1)

# Inicializar variable de sesión
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = set()

if 'new_files' not in st.session_state:
    st.session_state.new_files = set()

if 'files_to_delete' not in st.session_state:
    st.session_state.files_to_delete = set()

if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0



# Barra lateral de Streamlit para subir y listar los documentos
st.sidebar.title("Subir Archivos")
uploaded_file = st.sidebar.file_uploader("Elige un archivo", type=['pdf', 'docx', 'xlsx'], key=st.session_state["file_uploader_key"], label_visibility="hidden")

# Guarda el documento subido en la carpeta data/files, y despues lo procesa dependiendo del tipo de archivo
# if uploaded_file and uploaded_file.name not in st.session_state.uploaded_files:
if uploaded_file and uploaded_file.name not in st.session_state.uploaded_files and uploaded_file.name not in st.session_state.new_files:
    file_id = str(uuid.uuid4())
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
        embeddings = create_embeddings(text)
        # if embeddings.shape[0] == len(text.split()):
        #     embeddings = embeddings.reshape(len(text.split()), -1)
        index.add(embeddings)
        faiss.write_index(index, faiss_index_path)

        # Guardar metadatos del documento
        metadata[file_id] = {
            'file_name': uploaded_file.name,
            'embedding_start_idx': index.ntotal - 1,
            'embedding_end_idx': index.ntotal,
            'text': text 
        }
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        st.session_state.uploaded_files.add(uploaded_file.name)
        st.session_state.new_files.add(uploaded_file.name)
        #st.sidebar.success("Archivo subido y procesado correctamente.")
        st.rerun()




# # Listar documentos subidos
# st.sidebar.title("Documentos Subidos")
# for file_id, file_info in metadata.items():
#     if st.sidebar.button(f"Eliminar {file_info['file_name']}", key=file_id):
#         # Eliminar embeddings del índice FAISS
#         start_idx = file_info['embedding_start_idx']
#         end_idx = file_info['embedding_end_idx']
#         index.remove_ids(np.arange(start_idx, end_idx, dtype=np.int64))
#         faiss.write_index(index, faiss_index_path)
        
#         # Eliminar metadatos del documento
#         del metadata[file_id]
#         with open(metadata_file, 'w') as f:
#             json.dump(metadata, f)
        
#         # Eliminar archivo
#         os.remove(os.path.join(uploaded_files, file_info['file_name']))
#         st.session_state.uploaded_files.remove(file_info['file_name'])
#         if file_info['file_name'] in st.session_state.new_files:
#             st.session_state.new_files.remove(file_info['file_name'])
#         st.sidebar.success(f"Archivo {file_info['file_name']} eliminado correctamente.")
#         st.rerun()


# Función para eliminar archivos
def eliminar_archivo(file_id, file_info):
    start_idx = file_info['embedding_start_idx']
    end_idx = file_info['embedding_end_idx']
    index.remove_ids(np.arange(start_idx, end_idx, dtype=np.int64))
    faiss.write_index(index, faiss_index_path)
    
    del metadata[file_id]
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)
    
    os.remove(os.path.join(uploaded_files, file_info['file_name']))
    if file_info['file_name'] in st.session_state.uploaded_files:
        st.session_state.uploaded_files.remove(file_info['file_name'])
    if file_info['file_name'] in st.session_state.new_files:
        st.session_state.new_files.remove(file_info['file_name'])
    st.session_state.files_to_delete.add(file_info['file_name'])
    st.session_state["file_uploader_key"] += 1
    st.rerun()

st.sidebar.title("Documentos Subidos")
archivos_a_eliminar = []
for file_id, file_info in metadata.items():
    if file_info['file_name'] not in st.session_state.files_to_delete:
        if st.sidebar.button(f"Eliminar {file_info['file_name']}", key=file_id):
            archivos_a_eliminar.append((file_id, file_info))

for file_id, file_info in archivos_a_eliminar:
    eliminar_archivo(file_id, file_info)





# Campo de texto para realizar preguntas
st.title("Asistente Virtual Empresarial IA")
query = st.text_input("Pregunta:")

# if st.button("Buscar"):
#     st.write(f"Buscando resultados para: {query}")




def search_embeddings(query):
    query_embeddings = create_embeddings(query)
    distances, indices = index.search(query_embeddings, k=5)
    return indices


# Se obtienen los embeddings de la base de datos FAISS que mas se asemejan con los embeddings de la pregunta
def get_relevant_texts(indices):
    texts = []
    for idx in indices[0]:
        for file_id, file_info in metadata.items():
            start_idx = file_info['embedding_start_idx']
            end_idx = file_info['embedding_end_idx']
            if start_idx <= idx < end_idx:
                texts.append(file_info['text'])
                break
    return texts

# El texto de la busqueda se convierte a embeddings
# Se envian los embeddings de la pregunta para comparar y obtener los embeddings de la base de datos que mas cerca estan o que mas se parecen
# Se obtienen los embeddings de la base de datos FAISS que mas se asemejan con los embeddings de la pregunta
# Se envian los embeddings filtrados al endpoint de OpenIA para obtener una respuesta "bonita"
# El API de OpenIA responde en base al contecto de embeddings que le enviamos
if st.button("Buscar"):
    indices = search_embeddings(query)
    relevant_texts = get_relevant_texts(indices)
    context = "\n".join(relevant_texts)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Contexto: {context}"},
            {"role": "user", "content": query}
        ],
        max_tokens=150
    )
    st.write(response.choices[0].message.content.strip())

    



# Función para mostrar los embeddings almacenados en FAISS
def mostrar_embeddings():
    embeddings_list = []
    for file_id, file_info in metadata.items():
        start_idx = file_info['embedding_start_idx']
        end_idx = file_info['embedding_end_idx']
        embeddings = index.reconstruct_n(start_idx, end_idx - start_idx)
        for idx, embedding in enumerate(embeddings):
            embeddings_list.append({
                'ID/Nombre del Documento': file_info['file_name'],
                'Vector': embedding.tolist(),
                'Texto': file_info.get('text', 'N/A')  
            })
    return embeddings_list

# Mostrar detalles de los documentos subidos y sus embeddings
embeddings_list = mostrar_embeddings()
if embeddings_list:
    for doc in embeddings_list:
        st.write(f"**Nombre del Documento:** {doc['ID/Nombre del Documento']}")
        st.write(f"**Texto:** {doc['Texto']}")
        st.write(f"**Embeddings:** {doc['Vector']}")
        st.write("---")