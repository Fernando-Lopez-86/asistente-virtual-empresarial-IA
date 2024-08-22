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
            background-color: #ff4b4b;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            z-index: 1000;
            border: none;
        }
        .logout-button:hover {
            background-color: #ff3333;
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