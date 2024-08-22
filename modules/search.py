import streamlit as st
from modules.embeddings import create_embeddings
from modules.ui import highlight_common_words, display_highlighted_text
from openai import OpenAI
import os

# Obtener la API key desde las variables de entorno
client = OpenAI(
     api_key=os.getenv('OPENAI_API_KEY'),
)

# Función donde se le envia la pregunta y un índice FAISS, y devuelve los indices de los vectores de embeddings mas similares a la pregunta en el indice FAISS
# Primero, el texto de la pregunta la transforma en embeddings utilizando la función create_embeddings
# Segundo, utiliza el metodo search del índice FAISS para encontrar los 5 (k=5) embeddings más similares a los embeddings de la pregunta. Ver de agregar campo para modificar temperatura k
# Devuelve los índices de los embeddings mas similares.
def search_embeddings(query, index):
    query_embeddings = create_embeddings(query)
    distances, indexes_relevant = index.search(query_embeddings, k=5)
    return indexes_relevant

# Funcion para tomar los indices de los embeddings mas similares y el diccionario de metadatos, y devuelve los textos correspondientes a esos embeddings
# Inicializa una lista vacia de nombre texts
# Se itera sobre los indices relevantes devueltos por la funcion search_embeddings
# Para cada indice se busca el rango de embeddings en los metadatos
# Si el indice esta dentro del rango de embeddings de un archivo, agrega el texto de ese archivo a la lista texts
# Devuelve la lista de textos relevantes.
def get_relevant_texts(indexes_relevant, metadata):
    texts = []
    for idx in indexes_relevant[0]:
        for file_id, file_info in metadata.items():
            start_idx = file_info['embedding_start_idx']
            end_idx = file_info['embedding_end_idx']
            if start_idx <= idx < end_idx:
                texts.append(file_info['text'])
                break
    return texts

# Esta es funcion principal en el proceso de busqueda de los embeddings relevantes, obteniendo los textos y mostrando la respuesta generada por el modelo de lenguaje de OpenAI junto con el contexto resaltado
# Primero se ejecuta la funcion search_embeddings para obtener los indices de los embeddings mas similares a la pregunta
# Segundo se ejecuta la funcion get_relevant_texts para obtener los textos correspondientes a los indices que devuelve la funcion search_embeddings
# Tercero se almacenan los textos relevantes en una sola cadena de nombre context
# Cuarto se ejecuta una consulta a la API de OpenIA enviandole el contexto y la pregunta para obtener una respuesta
# Sexto y solo con el fin de resaltar en negrita las palabras comunes entre el contexto y la respuesta, se utiliza la funcion highlight_common_words, despues esta funcion desaparece
# Septimo se muestra la respuesta resaltada en streamlit
# Ultimo se muestra los textos de los metadatos resaltando las palabras de la respuesta utilizando display_highlighted_text.
def search_and_display_results(query, index, metadata):
    indices = search_embeddings(query, index)
    relevant_texts = get_relevant_texts(indices, metadata)
    context = "\n".join(relevant_texts)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Contexto: {context}"},
            {"role": "user", "content": query}
        ],
        max_tokens=300
    )
    raw_response = response.choices[0].message.content.strip()
    highlighted_response = highlight_common_words(context, raw_response)
    st.write(highlighted_response, unsafe_allow_html=True)
    display_highlighted_text(metadata, raw_response)