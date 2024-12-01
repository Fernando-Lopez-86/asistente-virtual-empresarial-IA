import streamlit as st
from modules.files import delete_file, handle_file_upload


# def display_uploaded_files(index, metadata, role):
#     st.sidebar.title("Documentos Subidos 📄")
#     files_to_delete = []

#     for file_id, file_info in metadata.items():
#         if file_info['file_name'] not in st.session_state.get("files_to_delete", []):
#             col1, col2 = st.sidebar.columns([0.5, 0.5])
#             col1.write(file_info['file_name'])
#             if col2.button('❌', key=file_id):
#                 files_to_delete.append((file_id, file_info))

#     for file_id, file_info in files_to_delete:
#         delete_file(file_id, file_info, index, metadata)


def display_app_content():

    if 'checkbox_reset' not in st.session_state:
        st.session_state['checkbox_reset'] = 0
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0

    if st.session_state.get('logged_in'):
        if st.session_state['role'] == 'admin':
            st.sidebar.title("Subir Documentos 📤")

            st.sidebar.markdown(
                "1. Seleccionar la categoria del documento\n"
                "2. Subir el documento pdf, docx, xlsx\n"
            )

            # Inicializar los checkboxes
            # if 'General' not in st.session_state:
            #     st.session_state['General'] = False
            # if 'Administracion' not in st.session_state:
            #     st.session_state['Administracion'] = False
            # if 'Produccion' not in st.session_state:
            #     st.session_state['Produccion'] = False
            # if 'Laboratorio' not in st.session_state:
            #     st.session_state['Laboratorio'] = False

            # Crear dos columnas
            col1, col2 = st.sidebar.columns(2)

            # Colocar los checkboxes en las dos columnas
            with col1:
                general = st.checkbox('General', key='General')
                produccion = st.checkbox('Produccion', key='Produccion')
            with col2:
                administracion = st.checkbox('Administracion', key='Administracion')
                laboratorio = st.checkbox('Laboratorio', key='Laboratorio')

            

            # Determinar la categoría seleccionada
            selected_category = None
            if general:
                selected_category = 'General'
            elif administracion:
                selected_category = 'Administracion'
            elif produccion:
                selected_category = 'Produccion'
            elif laboratorio:
                selected_category = 'Laboratorio'


            uploaded_file = st.sidebar.file_uploader("Elige un archivo", type=['pdf', 'docx', 'xlsx'], key=st.session_state.get("file_uploader_key", 0), label_visibility="hidden")


            from modules.files import handle_file_upload
            from modules.search import search_and_display_results
            from modules.embeddings import init_faiss_index
            # from modules.ui import display_uploaded_files, display_embeddings

            index, metadata = init_faiss_index()

            if uploaded_file is not None:
                if not selected_category:
                    st.sidebar.error("Debe seleccionar una categoría antes de subir el archivo.")
                else:
                    if uploaded_file and uploaded_file.name not in st.session_state.get("uploaded_files", []):
                        handle_file_upload(uploaded_file, index, metadata, selected_category)
                        # st.session_state["uploaded_files"].append(uploaded_file.name)


            st.sidebar.markdown("---")
            # Llamar a la función display_uploaded_files
            # display_uploaded_files(index, metadata, st.session_state['role'])

            st.sidebar.title("Documentos Subidos 📄")
            files_to_delete = []
            for file_id, file_info in metadata.items():
                if st.session_state['role'] == 'admin':
                    if file_info['file_name'] not in st.session_state.get("files_to_delete", []):
                        col1, col2 = st.sidebar.columns([0.5, 0.5])
                        col1.write(file_info['file_name'])
                        if col2.button('❌', key=file_id):
                            files_to_delete.append((file_id, file_info))
            for file_id, file_info in files_to_delete:
                delete_file(file_id, file_info, index, metadata)



        else:
            from modules.files import handle_file_upload
            from modules.search import search_and_display_results
            from modules.embeddings import init_faiss_index
            # from modules.ui import display_uploaded_files, display_embeddings

            index, metadata = init_faiss_index()
            # display_uploaded_files(index, metadata, st.session_state['role'])
            # display_uploaded_files(index, metadata)
            st.sidebar.title("Documentos Subidos 📄")
            files_to_delete = []
            for file_id, file_info in metadata.items():
                if file_info['category'] == st.session_state.get('role') or file_info['category'] == 'General':
                    if file_info['file_name'] not in st.session_state.get("files_to_delete", []):
                        # col1, col2 = st.sidebar.columns([0.5, 0.5])
                        # col1.write(file_info['file_name'])
                        st.sidebar.write(file_info['file_name'])
                        # if col2.button('❌', key=file_id):
                        #     files_to_delete.append((file_id, file_info))

            for file_id, file_info in files_to_delete:
                delete_file(file_id, file_info, index, metadata)






        st.title("🔎 Asistente Virtual Empresarial IA")
        # Usar markdown para mostrar la etiqueta "Pregunta:" en negrita y más grande
        # st.markdown('<p style="font-weight: bold; font-size: 1.3em;">Pregunta:</p>', unsafe_allow_html=True)
        # query = st.text_input("Pregunta:", key="input_query")
        # Usar markdown para mostrar la etiqueta "Pregunta:" en negrita y más grande
        # Usar markdown para la etiqueta "Pregunta:" en negrita, más grande y ajustando margen
        # Usar markdown para la etiqueta "Pregunta:" en negrita y más grande, eliminando márgenes
        # Inyectar CSS personalizado para eliminar el espacio en blanco

        
        # Crear el input para la pregunta justo debajo del markdown personalizado
        query = st.text_input("Pregunta:", key="input_query")


        # Crear el combo box para seleccionar el estilo justo arriba del botón "Buscar"
        style_options = [
            "Responde de manera formal y profesional.",
            "Responde con un tono amigable y casual.",
            "Responde en formato de lista.",
            # "Responde con un toque de humor.",
            "Responde de manera breve y concisa.",
            "Responde en inglés.",
            "Responde de manera detallada y extensa.",
            "Responde de manera específica y no generalices.",
        ]
        
        selected_style = st.selectbox("Selecciona el estilo de respuesta:", style_options)

        if st.button("Buscar"):
            search_and_display_results(query, index, metadata, selected_style)

        # display_embeddings(metadata, index)
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