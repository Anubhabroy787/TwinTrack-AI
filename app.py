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

    /* Global Theme - Adjusted to match the deep dashboard purples */
    .stApp { 
        background-color: #141326; 
        color: #00ffcc; 
        font-family: 'Share Tech Mono', monospace;
        animation: fadeSlideIn 0.6s ease-out;
    }
    
    /* Headers */
    h1, h2, h3, h4 { 
        font-family: 'Orbitron', sans-serif; 
        text-transform: uppercase;
        color: #a270ff !important;
        text-shadow: 0 0 5px rgba(162, 112, 255, 0.4);
    }
    
    h1 { text-align: center; font-size: 3.5rem !important;}

    /* Modernized, Responsive Buttons */
    div.stButton > button {
        background-color: #1c1a35;
        color: #00ffcc; 
        border: 1px solid #00ffcc; 
        border-radius: 8px; 
        box-shadow: 0 0 8px rgba(0, 255, 204, 0.1) inset;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.3s ease-in-out;
        width: 100%;
        padding: 10px;
    }
    div.stButton > button:hover { 
        background-color: #00ffcc;
        color: #141326;
        box-shadow: 0 0 15px #00ffcc; 
        transform: translateY(-2px);
    }
    
    /* Back Button specific styling override */
    .back-btn div.stButton > button {
        background-color: transparent;
        border: 1px solid #ff0055;
        color: #ff0055;
        width: auto;
        padding: 5px 20px;
        font-size: 0.8rem;
    }
    .back-btn div.stButton > button:hover {
        background-color: #ff0055;
        color: white;
        box-shadow: 0 0 15px #ff0055;
    }

    /* Responsive Terminal Inputs & Dashboard Cards */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1c1a35 !important;
        color: #fff !important;
        border-radius: 8px !important;
        border: 1px solid #3d396b !important;
        font-family: 'Share Tech Mono', monospace;
    }

    /* Metrics / Numbers */
    div[data-testid="stMetricValue"] { 
        color: #fff; 
        font-family: 'Orbitron', sans-serif;
    }
    div[data-testid="stMetricLabel"] {
        color: #a270ff;
    }
    
    /* Dividers */
    hr { border-color: rgba(162, 112, 255, 0.2); }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #a270ff, #00ffcc);
    }
</style>
''', unsafe_allow_html=True)

# --- API & BACKEND SETUP (GROQ LLaMA 3.3) ---
# Ensure your secrets.toml has GROQ_API_KEY
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except KeyError:
    st.warning("API Key not found. Please set GROQ_API_KEY in Streamlit secrets.")
    client = None

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
            <h1>TwinTrack AI</h1>
            <h3 style="color: #00ffcc; letter-spacing: 5px;">[ ACADEMIC DIGITAL TWIN ]</h3>
            <p style="color: #a270ff; font-family: monospace; opacity: 0.8;">ENGINEERED BY ROYAL BENGAL CODERS</p>
            <br>
            <div style="border: 1px solid rgba(162,112,255,0.3); padding: 20px; max-width: 600px; margin: auto; background: #1c1a35; border-radius: 12px;">
                <h5 style="color: #ccc; margin:0; font-family: 'Share Tech Mono', monospace;">"Input your parameters. Upload your syllabus. Visualize your academic trajectory in real-time."</h5>
            </div>
        </div>
        <br><br>
    ''', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: 
        st.button("[ LAUNCH WORKSPACE ]", use_container_width=True, on_click=switch_page, args=("login",))

elif st.session_state.page == "login":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    st.button("< BACK", on_click=switch_page, args=("landing",))
    st.markdown("</div>", unsafe_allow_html=True)
    
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
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    st.button("< BACK", on_click=switch_page, args=("login",))
    st.markdown("</div>", unsafe_allow_html=True)

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
# PHASE 3: THE DIGITAL TWIN DASHBOARD
# ==========================================
elif st.session_state.page == "analysis":
    d = st.session_state.user_data
    
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        st.button("< BACK", on_click=switch_page, args=("intake",))
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h2>[ DASHBOARD: {d.get('name', 'USER').upper()} ]</h2>", unsafe_allow_html=True)

    # --- TOP CONTROL PANEL (INPUTS) ---
    with st.expander("[ ADJUST LIVE PARAMETERS ]", expanded=True):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            cgpa = st.number_input("CURRENT CGPA:", min_value=0.0, max_value=10.0, format="%.2f", value=st.session_state.user_data.get("cgpa", 7.5))
            days = st.number_input("DAYS UNTIL EXAM:", min_value=0, value=st.session_state.user_data.get("days", 30))
        with col_b:
            internals = st.number_input("INTERNAL MARKS (/30):", min_value=0, max_value=30, value=st.session_state.user_data.get("internals", 22))
            assignments = st.slider("ASSIGNMENTS DONE (%):", 0, 100, st.session_state.user_data.get("assignments", 80))
        with col_c:
            att = st.slider("ATTENDANCE (%):", 0, 100, st.session_state.user_data.get("att", 70))
            hrs = st.slider("DAILY STUDY HOURS:", 0, 12, st.session_state.user_data.get("hrs", 2))

    # Calculate Twin Logic
    base_calc = (cgpa * 0.5) + (internals / 30 * 2) + (assignments / 100 * 1) + (hrs * 0.15) + ((att - 75) * 0.01)
    pred_sgpa = np.clip(base_calc, 0.0, 10.0)
    risk_level = "CRITICAL" if att < 75 else "WARNING" if pred_sgpa < 7.0 else "OPTIMAL"
    
    # Save current state dynamically
    st.session_state.user_data.update({"att": att, "days": days, "cgpa": cgpa, "hrs": hrs, "internals": internals, "assignments": assignments, "pred_sgpa": pred_sgpa})

    st.divider()

    # --- MAIN INTERACTIVE DASHBOARD ---
    dash_col1, dash_col2, dash_col3 = st.columns([1, 1.5, 1])
    
    with dash_col1:
        st.markdown("#### OVERALL STATUS")
        st.metric(label="PROJECTED SGPA", value=f"{pred_sgpa:.2f}", delta=f"{pred_sgpa - cgpa:.2f} Delta")
        st.metric(label="SYSTEM HEALTH", value=risk_level)
        
        # Donut Chart for Attendance
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Attended', 'Missed'], 
            values=[att, 100-att], 
            hole=.7,
            marker_colors=['#a270ff', '#1c1a35'],
            textinfo='none'
        )])
        fig_donut.update_layout(
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10), height=180,
            annotations=[dict(text=f'{att}%<br>Attnd', x=0.5, y=0.5, font_size=20, font_color='#fff', showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with dash_col2:
        st.markdown("#### PERFORMANCE METRICS")
        # Interactive Bar Chart
        categories = ['Current CGPA', 'Pred SGPA', 'Internals (Scale 10)']
        values = [cgpa, pred_sgpa, (internals/30)*10]
        
        fig_bar = go.Figure(data=[go.Bar(
            x=categories, 
            y=values,
            marker_color=['#1c1a35', '#a270ff', '#00ffcc'],
            text=[f"{v:.1f}" for v in values],
            textposition='auto'
        )])
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ccc'),
            yaxis=dict(range=[0, 10], gridcolor='#3d396b'),
            margin=dict(t=20, b=0, l=0, r=0), height=280
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with dash_col3:
        st.markdown("#### ONGOING TASKS")
        st.markdown(f"<span style='color:#a270ff'>Assignments</span> ({assignments}%)", unsafe_allow_html=True)
        st.progress(assignments / 100)
        
        study_goal = min(hrs / 8, 1.0) # Assume 8 hours is 100% max capacity
        st.markdown(f"<span style='color:#00ffcc'>Daily Study Quota</span> ({hrs} Hrs)", unsafe_allow_html=True)
        st.progress(study_goal)
        
        days_progress = max(1.0 - (days / 120), 0.0) # Assume 120 days in a sem
        st.markdown(f"<span style='color:#ff0055'>Semester Timeline</span> ({days} Days Left)", unsafe_allow_html=True)
        st.progress(days_progress)

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
                st.session_state.user_data.update({"subject": sub, "syllabus_content": raw_syllabus})
            
            switch_page("chat")
            st.rerun()

# ==========================================
# PHASE 4: THE BEAST (Decision Support Chat)
# ==========================================
elif st.session_state.page == "chat":
    d = st.session_state.user_data
    
    with st.sidebar:
        st.markdown("<h2 style='color: #a270ff;'>[ CONTROLS ]</h2>", unsafe_allow_html=True)
        
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        if st.button("< BACK TO DASHBOARD"): 
            switch_page("analysis")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
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
                if client:
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
                else:
                    st.error("[ ERROR ]: LLM client not initialized. Check API key.")
