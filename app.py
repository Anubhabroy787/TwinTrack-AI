import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import time
import io
# ==========================================
# 1. PREMIUM SAAS UI & CSS CONFIGURATION
# ==========================================
st.set_page_config(page_title="TwinTrack AI | Academic Twin", page_icon="♾️", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    @keyframes fadeSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulseGlow { 0% { transform: scale(0.95); opacity: 0.5; } 100% { transform: scale(1.05); opacity: 0.8; } }

    .stApp { 
        background-color: #050505; 
        background-image: radial-gradient(circle at 50% 0%, rgba(162, 112, 255, 0.05), transparent 50%);
        color: #e0e0e0; font-family: 'Inter', sans-serif; animation: fadeSlideIn 0.4s ease-out; 
    }
    
    h1, h2, h3, h4, h5 { font-family: 'Inter', sans-serif; font-weight: 600; color: #ffffff !important; letter-spacing: -0.5px; }
    
    .saas-card {
        background-color: rgba(15, 15, 20, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        margin-bottom: 24px; transition: border 0.2s ease;
    }
    .saas-card:hover { border: 1px solid rgba(162, 112, 255, 0.3); }
    
    [data-testid="stSidebar"] { background-color: #0a0a0c !important; border-right: 1px solid rgba(255,255,255,0.05); }
    [data-testid="stSidebar"] div.stButton > button {
        background: transparent !important; border: none !important; color: #888 !important; text-align: left !important;
        justify-content: flex-start !important; padding: 8px 16px !important; font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important; font-weight: 500 !important; border-radius: 6px !important; transition: all 0.2s;
    }
    [data-testid="stSidebar"] div.stButton > button:hover { background: rgba(255,255,255,0.05) !important; color: #fff !important; }
    
    div.stButton > button {
        background: #ffffff; color: #000000; border: none; border-radius: 6px; 
        font-family: 'Inter', sans-serif; font-weight: 500; width: 100%; padding: 10px; transition: 0.2s;
    }
    div.stButton > button:hover { background: #e0e0e0; transform: translateY(-1px); }
    
    .secondary-btn div.stButton > button { background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); }
    .secondary-btn div.stButton > button:hover { background: rgba(255,255,255,0.1); }
    .danger-btn div.stButton > button { background: rgba(255,50,50,0.1); color: #ff4d4d; border: 1px solid rgba(255,50,50,0.2); }
    .danger-btn div.stButton > button:hover { background: rgba(255,50,50,0.2); }
    .accent-btn div.stButton > button { background: linear-gradient(135deg, #a270ff, #00ffcc); color: #000; font-weight: 600; border: none; }

    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div { 
        background-color: #0a0a0c !important; color: #fff !important; border-radius: 6px !important; border: 1px solid rgba(255,255,255,0.1) !important; font-family: 'JetBrains Mono', monospace; 
    }
    hr { border-color: rgba(255,255,255,0.05); }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: #fff; margin:0; }
    .metric-label { font-family: 'Inter', sans-serif; font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
</style>
''', unsafe_allow_html=True)

# ==========================================
# 2. STATE & API MANAGEMENT
# ==========================================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

if "page" not in st.session_state: st.session_state.page = "login"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "decay_penalty" not in st.session_state: st.session_state.decay_penalty = 0.0
if "user_data" not in st.session_state: 
    st.session_state.user_data = {
        "name": "", "cgpa": 7.5, "days": 30, "internals": 22, "assignments": 0.0, "att": 70, "hrs": 0, 
        "subject": "None", "syllabus_content": "",
        "dynamic_tasks": ["Complete Module 1 Assignment", "Review Lecture Notes", "Prepare for upcoming Quiz"],
        "dynamic_topics": ["Pending Data Ingestion", "Upload syllabus to analyze weaknesses"]
    }

def switch_page(page_name): st.session_state.page = page_name

# SMART PDF EXTRACTOR: Actually searches for the subject in the massive PDF
def extract_pdf_text(file, subject_keyword):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = ""
        # Search the PDF for the specific subject keyword
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text and subject_keyword.lower() in text.lower():
                extracted_text += text + "\n"
        
        # If the keyword wasn't found, just grab the first 5 pages as a fallback
        if not extracted_text.strip():
            extracted_text = "".join([page.extract_text() + "\n" for page in pdf_reader.pages[:5]])
            
        return extracted_text[:4000] # Cap length for API limits
    except Exception as e: 
        return f"Error: {e}"

# ==========================================
# 3. LOGIN PAGE
# ==========================================
if st.session_state.page == "login":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, spacing, col2 = st.columns([1.3, 0.1, 1])
    
    with col1:
        st.markdown('''
            <h1 style="font-size: 4rem; font-weight: 800; line-height: 1; margin-bottom: 10px;">TwinTrack<span style="color:#a270ff;">.ai</span></h1>
            <p style="font-family: 'JetBrains Mono', monospace; color: #888; letter-spacing: 2px;">AUTONOMOUS ACADEMIC ENGINE</p>
            <p style="color: #a0a0b0; font-size: 1.1rem; margin-top: 30px; max-width: 85%; line-height: 1.6;">
                The daily workspace that builds a predictive mathematical model of your semester. Ingest your syllabus, log your focus, and let the agent engineer your success.
            </p>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 25px;'>Initialize Workspace</h3>", unsafe_allow_html=True)
        u_name = st.text_input("STUDENT IDENTIFIER", value="", placeholder="e.g. Anubhab Roy")
        pwd = st.text_input("ACCESS KEY", type="password", value="", placeholder="••••••••")
        sem = st.selectbox("ACADEMIC SEMESTER", ["Select Semester...", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"], index=0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='accent-btn'>", unsafe_allow_html=True)
        if st.button("Access Dashboard →"):
            if u_name.strip() == "" or sem == "Select Semester...":
                st.error("Authentication Error: Missing Parameters.")
            else:
                st.session_state.user_data.update({"name": u_name, "sem": sem})
                switch_page("dashboard")
                st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN APP 
# ==========================================
elif st.session_state.page in ["dashboard", "syllabus", "chat"]:
    
    d = st.session_state.user_data

    # --- MATH ENGINE ---
    internal_score = d['internals'] 
    historical_baseline = (d['cgpa'] / 10.0) * 70.0 
    effort_modifier = 0.8 + (0.2 * min(d['hrs'] / 5.0, 1.5))
    assignment_modifier = 0.9 + (0.1 * (d['assignments'] / 100.0))
    expected_external = np.clip(historical_baseline * effort_modifier * assignment_modifier, 0, 70)
    raw_sgpa = (internal_score + expected_external) / 10.0
    attendance_penalty = (75 - d['att']) * 0.15 if d['att'] < 75 else 0.0
    pred_sgpa = np.clip(raw_sgpa - attendance_penalty - st.session_state.decay_penalty, 0.0, 10.0)
    st.session_state.user_data['pred_sgpa'] = pred_sgpa

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"#### 👤 {d.get('name', 'USER').title()}\n<span style='color:#888; font-size:0.8rem;'>Sem {d.get('sem', '3rd')} CSE</span>", unsafe_allow_html=True)
        st.divider()
        if st.button("📊  Daily Hub & Twin"): switch_page("dashboard"); st.rerun()
        if st.button("📚  Data Ingestion"): switch_page("syllabus"); st.rerun()
        if st.button("🤖  Agentic Copilot"): switch_page("chat"); st.rerun()
        st.divider()
        st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
        if st.button("⏏ Logout"): switch_page("login"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DASHBOARD PAGE ---
    if st.session_state.page == "dashboard":
        st.markdown("<h2 style='margin-bottom: 20px;'>Overview Workspace</h2>", unsafe_allow_html=True)
        
        # Telemetry Banner
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='saas-card'><p class='metric-label'>Proj. SGPA</p><p class='metric-value' style='color:#00ffcc;'>{pred_sgpa:.2f}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='saas-card'><p class='metric-label'>Days Left</p><p class='metric-value'>{d['days']}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='saas-card'><p class='metric-label'>Internals</p><p class='metric-value'>{d['internals']}<span style='font-size:1rem; color:#888;'>/30</span></p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='saas-card'><p class='metric-label'>Attendance</p><p class='metric-value' style='color:{'#ff4d4d' if d['att']<75 else '#fff'};'>{d['att']}%</p></div>", unsafe_allow_html=True)

        dash_tab1, dash_tab2 = st.tabs(["[ 📅 DAILY HUB ]", "[ 🎛️ TWIN SIMULATOR ]"])
        
        with dash_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            hub1, hub2 = st.columns([1.5, 1])
            
            with hub1:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>⏱️ Live Focus Engine</h4><p style='color:#888; font-size:0.9rem;'>Run a deep work session to boost 'Time on Task' telemetry.</p>", unsafe_allow_html=True)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
                    if st.button("▶ Start 25m Pomodoro"):
                        st.session_state.user_data['hrs'] += 0.5; st.toast("Focus Logged!", icon="⏱️"); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with col_btn2:
                    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
                    if st.button("✅ Log Daily Class Attendance"):
                        st.session_state.user_data['att'] = min(100, d['att'] + 1); st.toast("Attendance Logged!", icon="📈"); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>📋 Active Assignments ({d.get('subject', 'General')})</h4>", unsafe_allow_html=True)
                # THESE ARE NOW DYNAMIC BASED ON THE PDF
                a1 = st.checkbox(d['dynamic_tasks'][0], value=d['assignments'] > 20)
                a2 = st.checkbox(d['dynamic_tasks'][1] if len(d['dynamic_tasks'])>1 else "Task 2", value=d['assignments'] > 50)
                a3 = st.checkbox(d['dynamic_tasks'][2] if len(d['dynamic_tasks'])>2 else "Task 3", value=d['assignments'] > 80)
                
                new_assign = sum([a1, a2, a3]) * 33.3
                if new_assign != d['assignments']:
                    st.session_state.user_data['assignments'] = new_assign; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with hub2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>🎯 AI Target Vectors</h4><p style='color:#888; font-size:0.9rem;'>Extracted weak points from syllabus:</p>", unsafe_allow_html=True)
                # DYNAMIC TOPICS FROM PDF
                st.error(f"Priority: {d['dynamic_topics'][0]}")
                if len(d['dynamic_topics']) > 1:
                    st.warning(f"Secondary: {d['dynamic_topics'][1]}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # INTERACTIVE DONUT CHART
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>Attendance Health</h4>", unsafe_allow_html=True)
                fig_pie = go.Figure(data=[go.Pie(labels=['Attended', 'Missed'], values=[d['att'], 100-d['att']], hole=0.7, marker_colors=['#00ffcc', '#ff4d4d'])])
                fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0, b=0, l=0, r=0), height=150)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with dash_tab2:
            st.markdown("<br><p style='color:#888;'>Simulate parameters to test the deterministic heuristic engine.</p>", unsafe_allow_html=True)
            with st.expander("⚙️ OVERRIDE TELEMETRY", expanded=True):
                s1, s2, s3 = st.columns(3)
                with s1:
                    n_cgpa = st.number_input("Base CGPA", min_value=0.0, max_value=10.0, value=float(d['cgpa']), step=0.1)
                    n_days = st.number_input("Days Left", min_value=0, value=int(d['days']))
                with s2:
                    n_int = st.number_input("Internals (/30)", min_value=0, max_value=30, value=int(d['internals']))
                    st.markdown("<div class='danger-btn' style='margin-top:28px;'>", unsafe_allow_html=True)
                    if st.button("Simulate Decay Penalty (-0.15)"): st.session_state.decay_penalty += 0.15; st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with s3:
                    n_att = st.slider("Simulate Attendance", 0, 100, int(d['att']))
                    n_hrs = st.slider("Simulate Study Hrs", 0, 12, int(d['hrs']))

                if n_cgpa != d['cgpa'] or n_days != d['days'] or n_int != d['internals'] or n_att != d['att'] or n_hrs != d['hrs']:
                    st.session_state.user_data.update({"cgpa": n_cgpa, "days": n_days, "internals": n_int, "att": n_att, "hrs": n_hrs}); st.rerun()

        # CLEAN, COMPARATIVE BAR CHART
        st.markdown("<div class='saas-card' style='margin-top:20px;'>", unsafe_allow_html=True)
        st.markdown("<h4>Trajectory Analysis</h4>", unsafe_allow_html=True)
        fig_bar = go.Figure(data=[
            go.Bar(name='Current Metrics', x=['CGPA', 'Internals (Scaled)', 'Assignments'], y=[d['cgpa'], (d['internals']/30)*10, d['assignments']/10], marker_color='#1c1a35'),
            go.Bar(name='Projected Outcome', x=['CGPA', 'Internals (Scaled)', 'Assignments'], y=[pred_sgpa, 0, 0], marker_color='#a270ff')
        ])
        fig_bar.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', color='#888'), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), margin=dict(t=10, b=10, l=10, r=10), height=250)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- SYLLABUS PAGE (NOW WITH PERMANENT MEMORY) ---
    elif st.session_state.page == "syllabus":
        st.markdown("<h2>Data Ingestion</h2>", unsafe_allow_html=True)
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        
        # 1. Check if we already have a PDF in memory
        if "pdf_bytes" not in st.session_state:
            st.session_state.pdf_bytes = None
            
        st.write("Upload your PDF once. TwinTrack caches it in memory so you can extract multiple subjects without re-uploading.")
        
        f1 = st.file_uploader("Syllabus / Routine [PDF]", type=['pdf'])
        
        # 2. Save to permanent memory the second it is uploaded
        if f1:
            st.session_state.pdf_bytes = f1.getvalue()
            st.success("📄 PDF successfully cached in system memory! You can safely switch tabs.")

        # 3. Only show the extraction tool if a PDF is in memory
        if st.session_state.pdf_bytes:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h4>Extract Subject Data</h4>", unsafe_allow_html=True)
            
            sub = st.text_input("Enter Subject Name (e.g., Computer Networks, Operating Systems):", value="Operating Systems")
            
            st.markdown("<div class='accent-btn'>", unsafe_allow_html=True)
            if st.button("Process & Sync with LLaMA"):
                with st.spinner(f"Searching memory for '{sub}' and generating tasks..."):
                    
                    # Convert the saved bytes back into a readable PDF file
                    pdf_file_obj = io.BytesIO(st.session_state.pdf_bytes)
                    
                    # Extract text
                    raw = extract_pdf_text(pdf_file_obj, sub)
                    st.session_state.user_data.update({"subject": sub, "syllabus_content": raw})
                    
                    # --- ACTUAL AI DATA PARSING ---
                    if client and raw.strip():
                        try:
                            parse_prompt = f"Based on this syllabus for {sub}, generate 3 short assignment tasks and 2 weak topics to study. Format exactly like this: Task1|Task2|Task3||Topic1|Topic2. Keep them short. Syllabus text: {raw[:2000]}"
                            res = client.chat.completions.create(messages=[{"role": "user", "content": parse_prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
                            parts = res.split('||')
                            if len(parts) == 2:
                                tasks = parts[0].split('|')
                                topics = parts[1].split('|')
                                st.session_state.user_data['dynamic_tasks'] = [t.strip() for t in tasks if t.strip()]
                                st.session_state.user_data['dynamic_topics'] = [t.strip() for t in topics if t.strip()]
                        except Exception as e:
                            st.warning("LLM formatting failed, using extracted text defaults.")
                    
                    st.success("Successfully Extracted! Dashboard tasks and AI Agent are now synced.")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- AGENT PAGE (NOW WITH PDF MEMORY) ---
    elif st.session_state.page == "chat":
        st.markdown("<h2>Agentic Copilot</h2>", unsafe_allow_html=True)
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        
        # THE FIX: WE INJECT THE SYLLABUS CONTENT INTO THE PROMPT SO IT CAN ACTUALLY READ IT
        syl_memory = d.get('syllabus_content', 'No syllabus uploaded yet.')
        
        if not st.session_state.chat_history:
            sys_p = f"Act as TwinTrack AI. Generate a 2-sentence proactive warning for {d['name']} based on Pred SGPA {d.get('pred_sgpa', 0.0):.2f}. Suggest a focus module based on this syllabus data: {syl_memory[:1000]}"
            with st.spinner("Connecting to Groq Inference..."):
                if client:
                    try:
                        res = client.chat.completions.create(messages=[{"role": "system", "content": sys_p}], model="llama-3.3-70b-versatile").choices[0].message.content
                        init_msg = f"**[ SYSTEM ALERT ]**\n\n{res}"
                    except: init_msg = f"**[ READY ]** SGPA: {d.get('pred_sgpa', 0.0):.2f}. Awaiting command."
                else: init_msg = f"**[ READY ]** SGPA: {d.get('pred_sgpa', 0.0):.2f}. API key missing."
            st.session_state.chat_history.append({"role": "assistant", "content": init_msg})

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.write(msg["content"])

        if p := st.chat_input("Ask a specific question about your uploaded PDF..."):
            st.session_state.chat_history.append({"role": "user", "content": p})
            with st.chat_message("user"): st.write(p)
            
            # THE LLM NOW HAS FULL CONTEXT OF THE PDF
            sys_p = f"You are TwinTrack AI for {d['name']}. Target: {d['subject']}. SGPA: {d.get('pred_sgpa', 0.0):.2f}. You must base your answers on this syllabus: {syl_memory[:3000]}"
            with st.chat_message("assistant"):
                if client:
                    try:
                        res = client.chat.completions.create(messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": p}], model="llama-3.3-70b-versatile").choices[0].message.content
                        st.write(res)
                        st.session_state.chat_history.append({"role": "assistant", "content": res})
                    except Exception as e: st.error(f"Inference Error: {e}")
                else: st.error("No API Configured.")
        st.markdown("</div>", unsafe_allow_html=True)
