
# streamlit: Biblioteca principal utilizada para crear la interfaz de usuario.
import streamlit as st
from modules.files import handle_file_upload, delete_file
from modules.search import search_and_display_results
from modules.embeddings import init_faiss_index


def display_app_content():
    if st.session_state.get('logged_in'):
        st.sidebar.title("Subir Documentos 📤")
        
        st.sidebar.markdown(
            "1. Subir el documento pdf, docx, xlsx\n"
        )

        # st.session_state: Almacena variables persistentes durante la ejecución.
        # uploaded_files: Lista de archivos subidos.
        # file_uploader_key: Clave única para actualizar el widget de subida de archivos.
        if 'uploaded_files' not in st.session_state or not isinstance(st.session_state['uploaded_files'], list):
            st.session_state['uploaded_files'] = []

        if 'file_uploader_key' not in st.session_state:
            st.session_state['file_uploader_key'] = 0

        uploaded_file = st.sidebar.file_uploader(
            "Elige un archivo", 
            type=['pdf', 'docx', 'xlsx'], 
            key=st.session_state.get("file_uploader_key", 0), 
            label_visibility="hidden"
        )

        # Llama a init_faiss_index para cargar el índice FAISS existente y los metadatos.
        index, metadata = init_faiss_index()

        # Si se sube un archivo nuevo:
        # Llama a handle_file_upload para procesarlo.
        # Lo agrega a la lista de archivos subidos.
        # Fuerza una recarga de la interfaz (st.rerun).
        if uploaded_file and uploaded_file.name not in st.session_state.get("uploaded_files", []):
            handle_file_upload(uploaded_file, index, metadata)
            # Verificar y corregir que siempre sea una lista
            if not isinstance(st.session_state['uploaded_files'], list):
                st.session_state['uploaded_files'] = [st.session_state['uploaded_files']]
    
            st.session_state['uploaded_files'].append(uploaded_file.name)
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.title("Documentos Subidos 📄")
        files_to_delete = []

        # Recorre los metadatos (metadata) para mostrar los archivos cargados.
        # Cada archivo tiene un botón de eliminación (❌).
        for file_id, file_info in metadata.items():
            col1, col2 = st.sidebar.columns([0.8, 0.2])
            col1.write(file_info['file_name'])
            if col2.button('❌', key=file_id):
                files_to_delete.append((file_id, file_info))

        # Elimina los archivos seleccionados utilizando delete_file.
        # Recarga la interfaz después de la eliminación.
        for file_id, file_info in files_to_delete:
            delete_file(file_id, file_info, index, metadata)
            st.rerun()

        st.title("🔎 Asistente Virtual Empresarial IA")

        if "input_query" not in st.session_state:
            st.session_state["input_query"] = ""

        query = st.text_input("**Pregunta:**", key="input_query")

        style_options = [
            "Responde de manera formal y profesional.",
            "Responde con un tono amigable y casual.",
            "Responde en formato de lista.",
            "Responde de manera breve y concisa.",
            "Responde en inglés.",
            "Responde de manera detallada y extensa.",
        ]
        selected_style = st.selectbox("**Selecciona el estilo de respuesta:**", style_options)


        # Al presionar "Buscar", ejecuta search_and_display_results, busca embeddings relevantes en el índice FAISS, recupera los textos correspondientes desde los metadatos.
        if st.button("Buscar"):
            search_and_display_results(query, index, metadata, selected_style)

    else:
        st.write("Debe iniciar sesión para ver el contenido.")


# Resumen
# Funcionalidades principales:
    # Subida de archivos y generación de embeddings.
    # Gestión de documentos subidos (listar y eliminar).
    # Realización de búsquedas semánticas con personalización del estilo de respuesta.
# Estructura del flujo:
    # Comprueba si el usuario está logueado.
    # Ofrece opciones de carga y gestión de documentos en la barra lateral.
    # Permite realizar búsquedas desde la sección principal.
# Interacción con otros módulos:
    # handle_file_upload: Procesa y guarda documentos.
    # delete_file: Elimina documentos y actualiza los metadatos.
    # search_and_display_results: Maneja las búsquedas semánticas.
# Si necesitas aclaraciones sobre alguna parte específica, no dudes en preguntarme.