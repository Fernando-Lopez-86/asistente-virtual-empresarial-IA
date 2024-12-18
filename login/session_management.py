import streamlit as st

def initialize_session():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

def logout():
    st.session_state['logged_in'] = False
    st.rerun()

def is_logged_in():
    return st.session_state.get('logged_in', False)

def display_logout_button():
    st.markdown(
        """
        <style>
        .logout-button {
            position: fixed;
            top: 60px;
            right: 20px;
            background-color: white; /* Fondo blanco */
            color: black; /* Letra negra */
            border-radius: 8px; /* Bordes redondeados */
            padding: 5px 10px; /* Espaciado interno del botón */
            font-size: 16px; /* Tamaño del texto */
            border: 1px solid #d3d3d3; /* Borde gris */
            transition: 0.1s; /* Transición suave para hover */
        }
        .logout-button:hover {
            background-color: white; /* Mantener fondo blanco al pasar el cursor */
            color: red; /* Letra roja al pasar el cursor */
            border: 1px solid red; /* Borde rojo al pasar el cursor */
        }
        </style>
        <form action="?logout=true" method="get">
            <button class="logout-button" type="submit">Cerrar Sesión</button>
        </form>
        """,
        unsafe_allow_html=True
    )

    if st.query_params.get("logout"):
        logout()