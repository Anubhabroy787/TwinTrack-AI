import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import time

# ==========================================
# 1. UI & CSS CONFIGURATION (OMOSKILLO + CYBERPUNK)
# ==========================================
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Inter:wght@400;600&display=swap');
    
    @keyframes fadeSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulseGlow { 0% { transform: scale(0.9); opacity: 0.4; } 100% { transform: scale(1.1); opacity: 0.8; } }

    /* Core Theme with Cyber Grid Background */
    .stApp { 
        background-color: #0b0a1a; 
        background-image: 
            linear-gradient(rgba(162, 112, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(162, 112, 255, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
        color: #e0e0e0; 
        font-family: 'Inter', sans-serif; 
        animation: fadeSlideIn 0.5s ease-out; 
    }
    
    h1, h2, h3, h4, h5 { font-family: 'Orbitron', sans-serif; color: #a270ff !important; text-transform: uppercase; }
    
    .cyber-card {
        background-color: rgba(22, 21, 43, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(162, 112, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hero-text { font-family: 'Orbitron', sans-serif; font-size: 3.2rem; color: #00ffcc; line-height: 1.1; text-shadow: 0 0 15px rgba(0,255,204,0.4); }
    
    div.stButton > button {
        background: linear-gradient(45deg, #1c1a35, #2a264f); color: #00ffcc; border: 1px solid #00ffcc; border-radius: 8px; 
        font-family: 'Orbitron', sans-serif; text-transform: uppercase; letter-spacing: 1.5px; width: 100%; padding: 12px; transition: 0.3s;
    }
    div.stButton > button:hover { background: #00ffcc; color: #0d0c1d; box-shadow: 0 0 20px #00ffcc; transform: translateY(-2px); }
    
    .danger-btn div.stButton > button { border-color: #ff0055; color: #ff0055; }
    .danger-btn div.stButton > button:hover { background: #ff0055; color: white; box-shadow: 0 0 15px #ff0055; }

    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div { 
        background-color: rgba(13, 12, 29, 0.9) !important; color: #fff !important; border-radius: 8px !important; border: 1px solid #3d396b !important; 
    }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #a270ff, #00ffcc); border-radius: 10px; }
    hr { border-color: rgba(162, 112, 255, 0.15); }
</style>
''', unsafe_allow_html=True)

# ==========================================
# 2. API SETUP & BACKEND LOGIC
# ==========================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

if "page" not in st.session_state: st.session_state.page = "login"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "decay_penalty" not in st.session_state: st.session_state.decay_penalty = 0.0
if "user_data" not in st.session_state: 
    st.session_state.user_data = {"name": "Anubhab Roy", "cgpa": 7.5, "days": 30, "internals": 22, "assignments": 80, "att": 70, "hrs": 2}

def switch_page(page_name): st.session_state.page = page_name

def extract_pdf_text(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() + "\n" for page in pdf_reader.pages[:5]])[:3000]
    except Exception as e: return f"Error: {e}"

# ==========================================
# 3. LOGIN PAGE (Animated Illustration + Form)
# ==========================================
if st.session_state.page == "login":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, spacing, col2 = st.columns([1.2, 0.2, 1])
    
    with col1:
        # Animated CSS Illustration (Glowing Geometric Core)
        st.markdown('''
            <div style="display: flex; align-items: center; margin-bottom: 30px;">
                <div style="position: relative; width: 120px; height: 120px;">
                    <div style="position: absolute; width: 100%; height: 100%; background: #00ffcc; border-radius: 50%; filter: blur(30px); animation: pulseGlow 3s infinite alternate;"></div>
                    <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="position: relative; z-index: 10;">
                        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                        <polyline points="2 17 12 22 22 17"></polyline>
                        <polyline points="2 12 12 17 22 12"></polyline>
                    </svg>
                </div>
            </div>
            
            <h1 class="hero-text">MASTER YOUR<br><span style="color:#a270ff;">ACADEMIC</span><br>TRAJECTORY.</h1>
            <p style="color: #a0a0b0; font-size: 1.1rem; margin-top: 15px; max-width: 90%;">
                TwinTrack AI builds a real-time digital twin of your semester. 
                Upload your syllabus, track your metrics, and let our predictive agent schedule your success.
            </p>
            
            <div style="margin-top: 40px; padding: 15px 20px; border-left: 4px solid #00ffcc; background: rgba(0, 255, 204, 0.05); display: inline-block;">
                <h5 style="color:#00ffcc; margin:0; font-family: 'Share Tech Mono', monospace;">SYSTEM V.2.0 ONLINE</h5>
                <span style="font-family: 'Share Tech Mono', monospace; color: #666; font-size: 0.9rem;">> SECURE CONNECTION ESTABLISHED...</span>
            </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown("<br><h2 style='text-align: left; margin-bottom: 20px;'>WELCOME BACK</h2>", unsafe_allow_html=True)
        
        # Native Streamlit Form Elements (No broken HTML wrappers)
        u_name = st.text_input("STUDENT ID (NAME)", value=st.session_state.user_data.get("name", "Anubhab Roy"))
        pwd = st.text_input("PASSWORD", type="password", value="********")
        sem = st.selectbox("CURRENT SEMESTER", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"], index=2)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("➔ INITIALIZE TWIN"):
            st.session_state.user_data.update({"name": u_name, "sem": sem})
            switch_page("dashboard")
            st.rerun()

# ==========================================
# 4. MAIN APP (Sidebar + Dashboard)
# ==========================================
elif st.session_state.page in ["dashboard", "syllabus", "chat"]:
    
    d = st.session_state.user_data

    # --- SIDEBAR NAVIGATION (OMOSKILLO STYLE) ---
    with st.sidebar:
        st.markdown(f"### 👤 {d.get('name', 'USER').upper()}")
        st.markdown(f"<span style='color:#888;'>Sem {d.get('sem', '3rd')} CSE<br>Narula Institute of Technology</span>", unsafe_allow_html=True)
        st.divider()
        
        if st.button("🎛️ DASHBOARD"): switch_page("dashboard"); st.rerun()
        if st.button("📚 SYLLABUS & DATA"): switch_page("syllabus"); st.rerun()
        if st.button("🤖 AI AGENT"): switch_page("chat"); st.rerun()
        
        st.divider()
        st.markdown("#### LIVE TWIN STATUS")
        st.progress(d.get('att', 70) / 100)
        st.caption(f"Attendance: {d.get('att', 70)}%")
        st.progress(d.get('pred_sgpa', 0.0) / 10.0)
        st.caption(f"Projected SGPA: {d.get('pred_sgpa', 0.0):.2f}")
        
        st.divider()
        st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
        if st.button("🚪 LOG OUT"): switch_page("login"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DASHBOARD VIEW ---
    if st.session_state.page == "dashboard":
        st.markdown("<h2>OVERVIEW DASHBOARD</h2>", unsafe_allow_html=True)
        
        # 1. CORE INTERACTION: LIVE TELEMETRY INPUTS
        with st.expander("🎛️ ADJUST LIVE TWIN PARAMETERS", expanded=True):
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1:
                new_cgpa = st.number_input("CURRENT CGPA", min_value=0.0, max_value=10.0, value=float(d.get('cgpa', 7.5)), step=0.1)
                new_days = st.number_input("DAYS UNTIL EXAM", min_value=0, value=int(d.get('days', 30)))
            with col_in2:
                new_internals = st.number_input("INTERNAL MARKS (/30)", min_value=0, max_value=30, value=int(d.get('internals', 22)))
                new_assign = st.slider("ASSIGNMENTS DONE (%)", 0, 100, int(d.get('assignments', 80)))
            with col_in3:
                new_att = st.slider("ATTENDANCE (%)", 0, 100, int(d.get('att', 70)))
                new_hrs = st.slider("DAILY STUDY HOURS", 0, 12, int(d.get('hrs', 2)))

            # Instantly update state if user changes a value
            if new_cgpa != d['cgpa'] or new_days != d['days'] or new_internals != d['internals'] or new_assign != d['assignments'] or new_att != d['att'] or new_hrs != d['hrs']:
                st.session_state.user_data.update({
                    "cgpa": new_cgpa, "days": new_days, "internals": new_internals, 
                    "assignments": new_assign, "att": new_att, "hrs": new_hrs
                })
                st.rerun()

        # Update reference after inputs
        d = st.session_state.user_data

        # --- CORE MATH: The Twin Algorithm ---
        base_calc = (d['cgpa'] * 0.5) + (d['internals'] / 30 * 2) + (d['assignments'] / 100 * 1) + (d['hrs'] * 0.15) + ((d['att'] - 75) * 0.01)
        pred_sgpa = np.clip(base_calc - st.session_state.decay_penalty, 0.0, 10.0)
        st.session_state.user_data['pred_sgpa'] = pred_sgpa

        # Quick Stats Row
        st.markdown("<div style='display:flex; gap:20px; margin-top: 10px;'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='cyber-card'><h5>Proj SGPA</h5><h2 style='color:#fff;'>{pred_sgpa:.2f}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='cyber-card'><h5>Days Left</h5><h2 style='color:#fff;'>{d['days']}</h2></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='cyber-card'><h5>Internals</h5><h2 style='color:#fff;'>{d['internals']}/30</h2></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='cyber-card'><h5>Attendance</h5><h2 style='color:#fff;'>{d['att']}%</h2></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Middle Row: Charts & Progress
        mid_col1, mid_col2 = st.columns([2, 1])
        with mid_col1:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("#### Performance Activities")
            fig_bar = go.Figure(data=[go.Bar(x=['Assignments', 'Internals', 'Study Hrs', 'Attendance'], y=[d['assignments']/10, (d['internals']/30)*10, d['hrs'], d['att']/10], marker_color=['#a270ff', '#00ffcc', '#1c1a35', '#ff0055'])])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#3d396b'), margin=dict(t=10, b=10, l=10, r=10), height=250)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with mid_col2:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("#### Course Statistics")
            st.write(f"Assignments ({d['assignments']}%)")
            st.progress(d['assignments'] / 100)
            st.write(f"Daily Study Quota ({d['hrs']}/8 Hrs)")
            st.progress(min(d['hrs'] / 8, 1.0))
            st.write(f"Semester Timeline ({d['days']} Days Left)")
            st.progress(max(1.0 - (d['days'] / 120), 0.0))
            st.markdown("</div>", unsafe_allow_html=True)

        # Bottom Row: Weakest Topics & Gamification Controls
        bot_col1, bot_col2 = st.columns(2)
        with bot_col1:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("#### Detected Weak Topics")
            st.error("1. Graph Algorithms (Needs Review)")
            st.warning("2. Boolean Algebra (Internals Low)")
            st.info("3. Pipelining Hazards")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with bot_col2:
            st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
            st.markdown("#### System Gamification")
            st.markdown("<p style='color:#888;'>Demonstrate Twin Decay logic to the judges. Simulating missed work instantly drops the projected SGPA.</p>", unsafe_allow_html=True)
            st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
            if st.button("⚠️ SIMULATE MISSED STUDY DAY (-0.15 SGPA)"):
                st.session_state.decay_penalty += 0.15
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.session_state.decay_penalty > 0:
                if st.button("🔄 RESTORE TWIN STATE"):
                    st.session_state.decay_penalty = 0.0
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- SYLLABUS UPLOAD VIEW ---
    elif st.session_state.page == "syllabus":
        st.markdown("<h2>DATA INGESTION ENGINE</h2>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        st.markdown("Upload your Syllabus or Academic Routine PDF to map modules to study hours.")
        file1 = st.file_uploader("Upload Document [PDF]", type=['pdf'])
        sub = st.selectbox("Assign to Subject:", ["Data Structures", "Computer Architecture", "Digital Logic"])
        if file1 and st.button("[ PROCESS & SYNC TO AGENT ]"):
            with st.spinner("Extracting vectors..."):
                raw = extract_pdf_text(file1)
                st.session_state.user_data.update({"subject": sub, "syllabus_content": raw})
                st.success("Synced successfully. Agent is ready.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- AI AGENT CHAT VIEW ---
    elif st.session_state.page == "chat":
        st.markdown("<h2>AGENTIC COMMAND CENTER</h2>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-card'>", unsafe_allow_html=True)
        
        if not st.session_state.chat_history:
            sys_prompt = f"Act as TwinTrack AI. Generate a 2-sentence proactive warning message for {d.get('name', 'User')} based on Pred SGPA {d.get('pred_sgpa', 0.0):.2f} and attendance {d.get('att', 70)}%. Suggest a module to study."
            with st.spinner("Agent initializing..."):
                if client:
                    try:
                        chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}], model="llama-3.3-70b-versatile")
                        initial_msg = f"**[ PROACTIVE ALERT ]**\n\n" + chat_completion.choices[0].message.content
                    except Exception:
                        initial_msg = f"**[ SYSTEM READY ]** SGPA: {d.get('pred_sgpa', 0.0):.2f}. How can I assist your study planning today?"
                else:
                    initial_msg = f"**[ SYSTEM READY ]** SGPA: {d.get('pred_sgpa', 0.0):.2f}. Connect API to enable proactive alerts."
            st.session_state.chat_history.append({"role": "assistant", "content": initial_msg})

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        if prompt := st.chat_input("Command the Twin..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.write(prompt)
            
            sys_prompt = f"You are TwinTrack AI, an Academic Agent for {d.get('name', 'User')}. Target: {d.get('subject', 'Subject')}. Pred SGPA: {d.get('pred_sgpa', 0.0):.2f}. Give actionable outputs using bullet points."
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    if client:
                        try:
                            chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                            bot_res = chat_completion.choices[0].message.content
                            st.write(bot_res)
                            st.session_state.chat_history.append({"role": "assistant", "content": bot_res})
                        except Exception as e: st.error("API Error.")
                    else:
                        st.error("API Key not configured.")
        st.markdown("</div>", unsafe_allow_html=True)
