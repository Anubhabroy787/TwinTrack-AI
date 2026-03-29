import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import PyPDF2
import time

# --- UI & CSS CONFIGURATION ---
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #e0e6ed; }
    h1 { text-shadow: 0 0 20px rgba(0, 210, 255, 0.8); font-family: 'Orbitron', sans-serif; text-align: center; }
    div.stButton > button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white; border: none; border-radius: 10px; transition: all 0.4s ease;
        font-weight: bold; box-shadow: 0px 4px 15px rgba(0, 114, 255, 0.4);
    }
    div.stButton > button:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0px 8px 25px rgba(0, 210, 255, 0.8); }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #161b22; color: #00d2ff; border-radius: 8px; border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- SECURE API SETUP (GEMINI 2.0 FLASH) ---
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def switch_page(page_name):
    st.session_state.page = page_name

# --- PDF SMART SCANNER ---
def extract_semester_syllabus(file, subject_name, semester_val):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        sem_str = f"Semester {semester_val}"
        relevant_pages = []
        for page in pdf_reader.pages:
            p_text = page.extract_text()
            if p_text and sem_str.lower() in p_text.lower():
                if subject_name.lower() in p_text.lower():
                    relevant_pages.append(p_text)
        
        if not relevant_pages:
            for page in pdf_reader.pages:
                p_text = page.extract_text()
                if p_text and subject_name.lower() in p_text.lower():
                    relevant_pages.append(p_text)
                    
        return "\n".join(relevant_pages)[:8000]
    except Exception as e:
        return f"Syllabus extraction failed: {e}"

# --- PHASE 1: LANDING (LAYOUT FIXED) ---
if st.session_state.page == "landing":
    # Everything is now safely wrapped inside a single block
    st.markdown("""
        <br><br><br>
        <div style="text-align: center;">
            <h1 style="font-size: 70px; font-weight: 900; background: -webkit-linear-gradient(#00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TwinTrack AI</h1>
            <h3 style="color: #a3b8cc; letter-spacing: 2px;">THE ACADEMIC DIGITAL TWIN</h3>
            <p style="color: #58a6ff; font-family: monospace;">Developed by the Royal Bengal Coders</p>
            <br>
            <h5 style="font-style: italic; color: #8b949e; max-width: 600px; margin: auto;">"Stop guessing your trajectory. Upload your syllabus, visualize
