import streamlit as st

def display_app_content():
    from modules.files import handle_file_upload, delete_file
    from modules.search import search_and_display_results
    from modules.embeddings import init_faiss_index

    if st.session_state.get('logged_in'):
        st.sidebar.title("Subir Documentos 📤")
        st.sidebar.markdown(
            "1. Subir el documento pdf, docx, xlsx\n"
        )

        if 'uploaded_files' not in st.session_state or not isinstance(st.session_state['uploaded_files'], list):
            st.session_state['uploaded_files'] = []

        uploaded_file = st.sidebar.file_uploader(
            "Elige un archivo", 
            type=['pdf', 'docx', 'xlsx'], 
            key=st.session_state.get("file_uploader_key", 0)
        )

        index, metadata = init_faiss_index()

        if uploaded_file and uploaded_file.name not in st.session_state.get("uploaded_files", []):
            handle_file_upload(uploaded_file, index, metadata)
            # Verificar y corregir que siempre sea una lista
            if not isinstance(st.session_state['uploaded_files'], list):
                st.session_state['uploaded_files'] = [st.session_state['uploaded_files']]
    
            st.session_state['uploaded_files'].append(uploaded_file.name)

        st.sidebar.markdown("---")
        st.sidebar.title("Documentos Subidos 📄")
        files_to_delete = []

        for file_id, file_info in metadata.items():
            col1, col2 = st.sidebar.columns([0.8, 0.2])
            col1.write(file_info['file_name'])
            if col2.button('❌', key=file_id):
                files_to_delete.append((file_id, file_info))

        for file_id, file_info in files_to_delete:
            delete_file(file_id, file_info, index, metadata)
            st.rerun()

        st.title("🔎 Asistente Virtual Empresarial IA")

        if "input_query" not in st.session_state:
            st.session_state["input_query"] = ""

        query = st.text_input("Pregunta:", key="input_query")

        style_options = [
            "Responde de manera formal y profesional.",
            "Responde con un tono amigable y casual.",
            "Responde en formato de lista.",
            "Responde de manera breve y concisa.",
            "Responde en inglés.",
            "Responde de manera detallada y extensa.",
            "Responde de manera específica y no generalices.",
        ]
        selected_style = st.selectbox("Selecciona el estilo de respuesta:", style_options)

        if st.button("Buscar"):
            search_and_display_results(query, index, metadata, selected_style)

    else:
        st.write("Debe iniciar sesión para ver el contenido.")

def display_embeddings(metadata, index):
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
    if embeddings_list:
        for doc in embeddings_list:
            st.write(f"**Nombre del Documento:** {doc['ID/Nombre del Documento']}")
            st.write(f"**Texto:** {doc['Texto']}")
            st.write(f"**Embeddings:** {doc['Vector']}")
            st.write("---")

def highlight_common_words(context, response):
    context_words = set(context.split())
    response_words = response.split()
    highlighted_response = ' '.join([f"**{word}**" if word in context_words else word for word in response_words])
    return highlighted_response

def display_highlighted_text(metadata, raw_response):
    response_words = set(raw_response.split())
    st.title("Detalles de Embeddings")
    for doc in metadata.values():
        doc_text = doc.get('text', 'N/A')
        highlighted_text = ' '.join([f"<b>{word}</b>" if word in response_words else word for word in doc_text.split()])
        st.markdown(f"**Nombre del Documento:** {doc['file_name']}", unsafe_allow_html=True)
        st.markdown(f"**Texto:** {highlighted_text}", unsafe_allow_html=True)
        st.markdown("---")