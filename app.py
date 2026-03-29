import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import time

# --- UI & CSS CONFIGURATION (PRO-CYBERPUNK EDITION) ---
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="wide")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    /* Smooth Fade-In Animation for Page Loads */
    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Global Theme */
    .stApp { 
        background-color: #050505; 
        color: #00ffcc; 
        font-family: 'Share Tech Mono', monospace;
        animation: fadeSlideIn 0.6s ease-out;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(0, 255, 204, 0.05), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(255, 0, 255, 0.05), transparent 25%);
    }
    
    /* Headers */
    h1, h2, h3 { 
        font-family: 'Orbitron', sans-serif; 
        text-transform: uppercase;
        color: #ff00ff !important;
        text-shadow: 0 0 5px rgba(255,0,255,0.4);
    }
    
    h1 { text-align: center; }

    /* Modernized, Responsive Buttons */
    div.stButton > button {
        background-color: transparent;
        color: #00ffcc; 
        border: 1px solid #00ffcc; 
        border-radius: 4px; 
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.2) inset;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.3s ease-in-out;
        width: 100%;
        padding: 10px;
    }
    div.stButton > button:hover { 
        background-color: #00ffcc;
        color: #000000;
        box-shadow: 0 0 15px #00ffcc; 
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Responsive Terminal Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(0, 255, 204, 0.05) !important;
        color: #00ffcc !important;
        border-radius: 4px !important;
        border: 1px solid #333 !important;
        font-family: 'Share Tech Mono', monospace;
        transition: all 0.3s ease;
    }
    
    /* Input Hover & Focus Animations */
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border: 1px solid #ff00ff !important;
        box-shadow: 0 0 10px rgba(255,0,255,0.4) !important;
    }
    
    /* Metrics / Numbers */
    div[data-testid="stMetricValue"] { 
        color: #00ffcc; 
        text-shadow: 0 0 10px rgba(0,255,204,0.3); 
        font-family: 'Orbitron', sans-serif;
    }
    
    /* Dividers */
    hr { border-color: rgba(255,0,255,0.3); }
</style>
''', unsafe_allow_html=True)

# --- API & BACKEND SETUP (GROQ LLaMA 3.3) ---
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def switch_page(page_name):
    st.session_state.page = page_name

# --- PDF SMART SCANNER ---
def extract_semester_syllabus(file, subject_name, semester_val):
    try:
        file.seek(0) 
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        core_keyword = subject_name.split()[0].lower() 
        for page in pdf_reader.pages:
            p_text = page.extract_text()
            if p_text and core_keyword in p_text.lower():
                full_text += p_text + "\n"
        if not full_text.strip():
            for page in pdf_reader.pages[:10]:
                if page.extract_text():
                    full_text += page.extract_text() + "\n"
        return full_text[:15000] 
    except Exception as e:
        return f"Syllabus extraction error: {e}"

# ==========================================
# PHASE 1 & 1.5: LANDING & LOGIN
# ==========================================
if st.session_state.page == "landing":
    st.markdown('''
        <br><br><br>
        <div style="text-align: center;">
            <h1 style="font-size: 80px; font-weight: 900; color: #00ffcc !important; text-shadow: 0 0 20px rgba(0,255,204,0.5);">TwinTrack AI</h1>
            <h3 style="color: #ff00ff; letter-spacing: 5px;">[ ACADEMIC DIGITAL TWIN ]</h3>
            <p style="color: #00ffcc; font-family: monospace; opacity: 0.8;">ENGINEERED BY ROYAL BENGAL CODERS</p>
            <br>
            <div style="border: 1px solid rgba(255,0,255,0.3); padding: 20px; max-width: 600px; margin: auto; background: rgba(255,0,255,0.02); border-radius: 4px;">
                <h5 style="color: #ccc; margin:0; font-family: 'Share Tech Mono', monospace;">"Input your parameters. Upload your syllabus. Visualize your academic trajectory in real-time."</h5>
            </div>
        </div>
        <br><br>
    ''', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: 
        st.button("[ LAUNCH WORKSPACE ]", use_container_width=True, on_click=switch_page, args=("login",))

elif st.session_state.page == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>[ AUTHENTICATION ]</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["SIGN IN", "REGISTER"])
        with tab1:
            st.text_input("EMAIL ADDRESS", value="anubhab@narula.edu")
            st.text_input("PASSWORD", type="password", value="********")
            st.button("[ SECURE LOGIN ]", use_container_width=True, on_click=switch_page, args=("intake",))
        with tab2:
            st.text_input("FULL NAME")
            st.text_input("EMAIL ADDRESS", key="register_email")
            st.button("[ CREATE PROFILE ]", use_container_width=True, on_click=switch_page, args=("intake",))

# ==========================================
# PHASE 2: INTAKE 
# ==========================================
elif st.session_state.page == "intake":
    st.markdown("<h2>[ SYSTEM CALIBRATION ]</h2>", unsafe_allow_html=True)
    st.markdown("`ENTER BASELINE METRICS`")
    
    u_name = st.text_input("STUDENT NAME:", value=st.session_state.user_data.get("name", "Anubhab Roy"))
    col1, col2 = st.columns(2)
    with col1:
        course = st.selectbox("PROGRAM:", ["B.Tech", "BBA", "BCA"], index=0)
        year = st.selectbox("YEAR:", ["1st", "2nd", "3rd", "4th"], index=1)
    with col2:
        sem = st.selectbox("SEMESTER:", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"], index=2)
    
    st.write("")
    if st.button("[ GENERATE DIGITAL TWIN ]", use_container_width=True):
        st.session_state.user_data.update({"name": u_name, "course": course, "year": year, "sem": sem})
        switch_page("analysis")
        st.rerun()

# ==========================================
# PHASE 3: THE DIGITAL TWIN SIMULATOR
# ==========================================
elif st.session_state.page == "analysis":
    d = st.session_state.user_data
    st.toast(f"Profile Loaded: {d['name']} | Sem {d['sem']}", icon="✅")
    
    st.markdown("<h2>[ ACADEMIC TELEMETRY ]</h2>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        cgpa = st.number_input("CURRENT CGPA:", min_value=0.0, max_value=10.0, format="%.2f", value=7.5)
        days = st.number_input("DAYS UNTIL EXAM:", min_value=0, value=30)
    with col_b:
        internals = st.number_input("INTERNAL MARKS (OUT OF 30):", min_value=0, max_value=30, value=22)
        assignments = st.slider("ASSIGNMENTS COMPLETED (%):", 0, 100, 80)
    with col_c:
        att = st.slider("CURRENT ATTENDANCE (%):", 0, 100, 70)
        hrs = st.slider("DAILY STUDY HOURS:", 0, 12, 2)

    st.divider()

    st.markdown("<h2>[ PREDICTIVE DASHBOARD ]</h2>", unsafe_allow_html=True)
    
    base_calc = (cgpa * 0.5) + (internals / 30 * 2) + (assignments / 100 * 1) + (hrs * 0.15) + ((att - 75) * 0.01)
    pred_sgpa = np.clip(base_calc, 0.0, 10.0)
    
    risk_level = "CRITICAL (DETENTION)" if att < 75 else "WARNING" if pred_sgpa < 7.0 else "OPTIMAL"
    
    dash1, dash2, dash3 = st.columns(3)
    dash1.metric(label="PROJECTED SGPA", value=f"{pred_sgpa:.2f}", delta=f"{pred_sgpa - cgpa:.2f} Delta")
    dash2.metric(label="ATTENDANCE COMPLIANCE", value=f"{att}%", delta="-5% Deficit" if att < 75 else "Compliant")
    dash3.metric(label="SYSTEM STATUS", value=risk_level)

    st.divider()
    
    st.markdown("<h4 style='color: #00ffcc;'>[ 3D TRAJECTORY VISUALIZATION ]</h4>", unsafe_allow_html=True)
    s_m, a_m = np.meshgrid(np.linspace(0, 10, 20), np.linspace(0, 100, 20))
    z_m = np.clip(cgpa + (s_m * 0.15) + ((a_m - 75) * 0.01), 0, 10)
    fig = go.Figure(data=[go.Surface(z=z_m, x=s_m, y=a_m, colorscale='Sunsetdark', opacity=0.8)])
    fig.add_trace(go.Scatter3d(x=[hrs], y=[att], z=[pred_sgpa], mode='markers', marker=dict(size=8, color='#00ffcc'), name='Current Twin'))
    fig.update_layout(
        scene=dict(
            xaxis_title='HOURS', yaxis_title='ATTND %', zaxis_title='SGPA',
            xaxis=dict(backgroundcolor="#050505", gridcolor="#333", color="#00ffcc"),
            yaxis=dict(backgroundcolor="#050505", gridcolor="#333", color="#00ffcc"),
            zaxis=dict(backgroundcolor="#050505", gridcolor="#333", color="#00ffcc")
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=0), height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("<h2>[ SYLLABUS INTEGRATION ]</h2>", unsafe_allow_html=True)
    file = st.file_uploader("UPLOAD SYLLABUS DOCUMENT [PDF]", type=['pdf'])

    if file:
        subjects = ["Data Structures & Algorithms", "Computer Organization", "Digital Logic", "Mathematics"]
        sub = st.selectbox("TARGET SUBJECT:", subjects, index=0)
        
        if st.button("[ ANALYZE & EXTRACT STRATEGY ]", use_container_width=True):
            progress_text = "Processing document vectors..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.005)
                my_bar.progress(percent_complete + 1, text=progress_text)
            my_bar.empty()
            
            with st.spinner(f"Extracting modules for '{sub}'..."):
                raw_syllabus = extract_semester_syllabus(file, sub, d['sem'])
                st.session_state.user_data.update({
                    "att": att, "days": days, "cgpa": cgpa, "hrs": hrs, 
                    "internals": internals, "assignments": assignments,
                    "pred_sgpa": pred_sgpa, "subject": sub, "syllabus_content": raw_syllabus
                })
            
            switch_page("chat")
            st.rerun()

# ==========================================
# PHASE 4: THE BEAST (Decision Support Chat)
# ==========================================
elif st.session_state.page == "chat":
    d = st.session_state.user_data
    
    with st.sidebar:
        st.markdown("<h2 style='color: #ff00ff;'>[ CONTROLS ]</h2>", unsafe_allow_html=True)
        if st.button("[ RETURN TO TELEMETRY ]"): 
            switch_page("analysis")
            st.rerun()
        if st.button("[ RESET SESSION ]"): 
            st.session_state.chat_history = []
            switch_page("intake")
            st.rerun()
        
        st.divider()
        st.write(f"`TARGET:` **{d.get('subject', 'N/A')}**")
        st.write(f"`PROJ_SGPA:` **{d.get('pred_sgpa', 0.0):.2f}**")
        st.write(f"`ATTENDANCE:` **{d.get('att', 0)}%**")
        st.write(f"`INTERNALS:` **{d.get('internals', 0)}/30**")

    st.markdown("<h2>[ DECISION SUPPORT SYSTEM ]</h2>", unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        status = "🔴 ACTION REQUIRED" if d.get('att', 0) < 75 or d.get('pred_sgpa', 0.0) < 7.0 else "🟢 OPTIMAL"
        initial_msg = f"**[ SYSTEM READY ]** Status: {status}. \n\n{d.get('name', 'User')}, your Digital Twin predicts an SGPA of **{d.get('pred_sgpa', 0.0):.2f}**. You have {d.get('days', 0)} days remaining. Syllabus context loaded for {d.get('subject', 'your subject')}. \n\nDo you require a module breakdown or an attendance recovery protocol?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_msg})

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])

    if prompt := st.chat_input("Input query..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        sys_prompt = f"""
        You are 'TwinTrack AI', an Academic Decision Support System for engineering student {d.get('name', 'User')}. Respond in a precise, analytical, and professional tone.
        
        USER TELEMETRY:
        - Target: {d.get('subject', 'Subject')} in {d.get('days', 0)} days
        - Current Stats: {d.get('att', 0)}% Attendance | {d.get('cgpa', 0.0)} CGPA | Studies {d.get('hrs', 0)} hrs/day.
        - Internal Marks: {d.get('internals', 0)}/30 | Assignments: {d.get('assignments', 0)}% complete.
        - Simulated Predicted SGPA: {d.get('pred_sgpa', 0.0):.2f}
        
        SYLLABUS DATA:
        {d.get('syllabus_content', 'General topics only.')}
        
        STRATEGY RULES (MANDATORY):
        1. ACT LIKE A DECISION SYSTEM. Give quantitative, actionable outputs.
        2. If attendance < 75%, state: "Action Required: You must attend approximately [X] classes to reach the 75% threshold."
        3. When giving a study plan, map specific modules from the SYLLABUS DATA directly to their {d.get('hrs', 0)} hour daily limit.
        4. Use clear bullet points and bold numbers. Do not use conversational filler.
        """
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing telemetry..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    bot_response = chat_completion.choices[0].message.content
                    st.write(bot_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                except Exception as e:
                    st.error(f"[ ERROR ]: API Connection Failed. Details: {e}")
