import streamlit as st
from modules.embeddings import create_embeddings
import os
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Búsqueda de embeddings con FAISS
def search_embeddings(query, index, k=5, threshold=1.015):
    """
    Busca los k embeddings más cercanos en el índice FAISS.
    Filtra los resultados según un umbral de distancia para mejorar la relevancia.
    """
    # Generar embedding de la consulta
    query_embedding = create_embeddings([query])[0]

    # Buscar en FAISS
    distances, indices = index.search(np.array([query_embedding]), k=k)

    # Filtrar por umbral de distancia
    filtered_indices = [idx for dist, idx in zip(distances[0], indices[0]) if dist <= threshold]
    return filtered_indices

# Recuperar textos relevantes basados en los índices devueltos por FAISS
def get_relevant_texts(filtered_indices, metadata):
    """
    Recupera los textos relevantes a partir de los índices filtrados.
    """
    texts = []
    for idx in filtered_indices:
        for file_id, file_info in metadata.items():
            if file_info['embedding_start_idx'] <= idx < file_info['embedding_end_idx']:
                relative_idx = idx - file_info['embedding_start_idx']
                texts.append(file_info['text_chunks'][relative_idx])
                break
    return texts

# Función principal para realizar la búsqueda y mostrar resultados
def search_and_display_results(query, index, metadata, selected_style, k=5, threshold=1.015):
    """
    Realiza la búsqueda semántica y muestra los resultados en la interfaz de usuario.
    """
    # Búsqueda de embeddings
    filtered_indices = search_embeddings(query, index, k=k, threshold=threshold)

    # Recuperar textos relevantes
    relevant_texts = get_relevant_texts(filtered_indices, metadata)

    # Construir el contexto a partir de los textos relevantes
    context = "\n".join(relevant_texts)

    # Generar el prompt del sistema
    system_prompt = (
        f"Contexto: {context}\n\n"
        "Eres un asistente inteligente que responde únicamente en base al contexto proporcionado. "
        "Si el contexto es nulo, vacío o contiene información insuficiente para responder la pregunta, pide disculpas de manera breve y no intentes proporcionar ninguna respuesta adicional. "
        "Por ejemplo, si no puedes responder, di: 'Lo siento, no puedo proporcionar una respuesta con la información disponible.' "
        "No inventes ni supongas información fuera del contexto proporcionado. Responde únicamente basándote en los datos proporcionados."
        f"{selected_style}"
    )

    # Consultar la API de OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        max_tokens=800
    )

    # Mostrar la respuesta generada
    st.write(response.choices[0].message.content.strip(), unsafe_allow_html=True)

    # Mostrar contexto y embeddings relevantes en un expander
    with st.expander("#### Contexto enviado a la API de OpenAI"):
        st.write(context)

        st.markdown("#### Embeddings Relevantes y Representaciones Vectoriales:")
        for idx, text in zip(filtered_indices, relevant_texts):
            # Recuperar el vector almacenado en FAISS para cada índice
            embedding_vector = index.reconstruct(int(idx))
            st.markdown(f"**Embedding #{idx}:**")
            st.write(text)  # Mostrar el texto relevante
            st.markdown("**Vector Representacional:**")
            st.code(embedding_vector.tolist())  # Mostrar el vector como lista