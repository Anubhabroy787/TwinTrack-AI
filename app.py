import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai  # Changed from groq
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

# --- API SETUP (GEMINI 2.0 FLASH) ---
# It's better to keep the key in secrets, but I'll use your provided key for now
genai.configure(api_key="AIzaSyCvGzWkIwRSTQZVQFZ3gSiw8A7nkwGehS8")
model = genai.GenerativeModel('gemini-2.0-flash') # The latest flagship

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def switch_page(page_name):
    st.session_state.page = page_name

# --- PDF SMART SCANNER (Keeping your logic) ---
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

# --- PHASE 1: LANDING ---
if st.session_state.page == "landing":
    st.markdown("<br><br><br><div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 70px;'>TwinTrack AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #a3b8cc;'>THE ACADEMIC DIGITAL TWIN</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("⚡ INITIALIZE SYSTEM", use_container_width=True, on_click=switch_page, args=("login",))

# --- PHASE 1.5: AUTHENTICATION ---
elif st.session_state.page == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        with tab1:
            st.text_input("Email ID", value="anubhab@narula.edu")
            st.text_input("Password", type="password", value="********")
            st.button("Secure Login", use_container_width=True, on_click=switch_page, args=("intake",))
        with tab2:
            st.text_input("Full Name")
            st.text_input("Email ID", key="register_email")
            st.button("Create Account", use_container_width=True, on_click=switch_page, args=("intake",))

# --- PHASE 2: INTAKE ---
elif st.session_state.page == "intake":
    st.markdown("<h2 style='color: #00d2ff;'>📝 Calibration Matrix</h2>", unsafe_allow_html=True)
    u_name = st.text_input("Student Designation:", value="Anubhab Roy")
    col1, col2 = st.columns(2)
    with col1:
        course = st.selectbox("Program:", ["B.Tech", "BBA", "BCA"], index=0)
        year = st.selectbox("Year:", ["1st", "2nd", "3rd", "4th"], index=2)
    with col2:
        sem = st.selectbox("Semester:", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"], index=2)
    
    if st.button("Generate Trajectory ➡️", use_container_width=True):
        st.session_state.user_data.update({"name": u_name, "course": course, "year": year, "sem": sem})
        switch_page("analysis")

# --- PHASE 3: 3D DIGITAL TWIN & PDF SCAN ---
elif st.session_state.page == "analysis":
    d = st.session_state.user_data
    col_a, col_b = st.columns(2)
    with col_a:
        att = st.number_input("Attendance (%):", 0, 100, 70)
        cgpa = st.number_input("Current CGPA:", 0.0, 10.0, 7.5)
    with col_b:
        days = st.number_input("Days left for Exam:", 0, 100, 30)
        hrs = st.number_input("Study Hours per Day:", 0, 24, 2)

    st.markdown("<h3 style='color: #00d2ff;'>🌌 3D Digital Twin Projection</h3>", unsafe_allow_html=True)
    s_mesh, a_mesh = np.meshgrid(np.linspace(0, 10, 20), np.linspace(0, 100, 20))
    z_mesh = np.clip(cgpa + (s_mesh * 0.15) + ((a_mesh - 75) * 0.01), 0, 10)
    fig = go.Figure(data=[go.Surface(z=z_mesh, x=s_mesh, y=a_mesh, colorscale='Electric', opacity=0.8)])
    fig.update_layout(scene=dict(xaxis_title='Hours', yaxis_title='Attnd %', zaxis_title='CGPA'), height=450)
    st.plotly_chart(fig, use_container_width=True)

    file = st.file_uploader("Upload University Syllabus (PDF)", type=['pdf'])
    if file:
        sub = st.selectbox("Target Subject:", ["Data Structures & Algorithms", "Computer Organization", "Digital Logic"])
        if st.button("🔥 START STRATEGY", use_container_width=True):
            with st.spinner("Extracting syllabus context..."):
                raw_syllabus = extract_semester_syllabus(file, sub, d['sem'])
                st.session_state.user_data.update({"att": att, "days": days, "cgpa": cgpa, "hrs": hrs, "subject": sub, "syllabus_content": raw_syllabus})
            st.balloons()
            switch_page("chat")

# --- PHASE 4: THE BEAST (GEMINI 2.0 FLASH CHAT) ---
elif st.session_state.page == "chat":
    d = st.session_state.user_data
    with st.sidebar:
        if st.button("⬅️ Back to Analysis"): switch_page("analysis")
        st.write(f"**Subject:** {d['subject']}")
        st.write(f"**Attendance:** {d['att']}%")

    st.markdown("<h2 style='color: #00d2ff;'>🤖 Tactical Virtual Educator</h2>", unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        status = "🔴 CRITICAL" if d['att'] < 75 else "🟢 STABLE"
        initial_msg = f"**System Ready.** Status: {status}. {d['name']}, you have {d['days']} days left. I've analyzed your syllabus for {d['subject']}. Let's build your plan."
        st.session_state.chat_history.append({"role": "assistant", "content": initial_msg})

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Command your strategist..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        syllabus_data = d.get('syllabus_content', 'General context.')
        sys_prompt = f"""
        You are 'TwinTrack AI', a strict Academic Strategist for {d['name']}.
        SUBJECT: {d['subject']} | DAYS LEFT: {d['days']} | ATTENDANCE: {d['att']}% | CGPA: {d['cgpa']}.
        SYLLABUS DATA: {syllabus_data}
        
        RULES:
        1. Reference specific modules from the SYLLABUS DATA.
        2. Warn them if attendance is below 75%.
        3. Be concise and use bold text for key terms.
        """
        
        with st.chat_message("assistant"):
            with st.spinner("Calculating..."):
                try:
                    # Gemini 2.0 Flash call
                    response = model.generate_content(f"SYSTEM INSTRUCTIONS: {sys_prompt}\n\nUSER PROMPT: {prompt}")
                    bot_response = response.text
                    st.write(bot_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                except Exception as e:
                    st.error("⚠️ Neural Link Overloaded. Try again in a few seconds.")
