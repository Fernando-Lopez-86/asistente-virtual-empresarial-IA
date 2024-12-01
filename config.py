import streamlit as st
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    if 'uploaded_files' not in st.session_state:
        st.session_state["uploaded_files"] = []

    if 'files_to_delete' not in st.session_state:
        st.session_state.files_to_delete = set()

    if "file_uploader_key" not in st.session_state:
        st.session_state["file_uploader_key"] = 0

