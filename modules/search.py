import streamlit as st
from modules.embeddings import create_embeddings
import os
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def search_embeddings(query, index):
    query_embedding = create_embeddings([query])[0]
    distances, indexes_relevant = index.search(np.array(query_embedding).reshape(1, -1), k=5)
    return indexes_relevant

def get_relevant_texts2(indexes_relevant, metadata):
    texts = set()  # Usamos un set para evitar duplicados
    for idx in indexes_relevant[0]:  # Recorremos los índices relevantes devueltos por FAISS
        for file_id, file_info in metadata.items():
            start_idx = file_info['embedding_start_idx']
            end_idx = file_info['embedding_end_idx']
            if start_idx <= idx < end_idx:  # Verifica si el índice está dentro del rango del archivo
                chunk_idx = idx - start_idx  # Calcula el índice del fragmento relevante
                texts.add(file_info['text_chunks'][chunk_idx])  # Añade solo el fragmento relevante
                break  # Salimos del bucle al encontrar el fragmento
    return list(texts)  # Convertimos el set a lista para mantener compatibilidad

def get_relevant_texts(indexes_relevant, metadata):
    texts = []
    for idx in indexes_relevant[0]:
        for file_id, file_info in metadata.items():
            if file_info["embedding_start_idx"] <= idx < file_info["embedding_end_idx"]:
                relative_idx = idx - file_info["embedding_start_idx"]
                texts.append(file_info["text_chunks"][relative_idx])
                break
    return texts

def search_and_display_results(query, index, metadata, selected_style):
    indices = search_embeddings(query, index)
    relevant_texts = get_relevant_texts(indices, metadata)

    
    
    context = "\n".join(relevant_texts)

    

    system_prompt = (
        f"Contexto: {context}\n\n"
        f"Si la informacion de context es nula o vacia, pide disculpas y no contestes nada por favor\n\n"
        f"Si no tienes suficiente informacion de context, pide disculpas y no contestes nada por favor\n\n"
        f"{selected_style}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        max_tokens=800
    )
    st.write(response.choices[0].message.content.strip(), unsafe_allow_html=True)


    with st.expander("#### Contexto enviado a la API de OpenAI"):
        st.write(context)

        st.markdown("#### Embeddings Relevantes y Representaciones Vectoriales:")
        for idx, text in zip(indices[0], relevant_texts):
            # Recuperar el vector almacenado en FAISS para cada índice
            embedding_vector = index.reconstruct(int(idx))
            st.markdown(f"**Embedding #{idx}:**")
            st.write(text)  # Mostrar el texto relevante
            st.markdown("**Vector Representacional:**")
            st.code(embedding_vector.tolist())  # Mostrar el vector como lista