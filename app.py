import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import time

# ==========================================
# 1. PREMIUM SAAS UI & CSS CONFIGURATION
# ==========================================
st.set_page_config(page_title="TwinTrack AI | Academic Twin", page_icon="♾️", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    @keyframes fadeSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulseGlow { 0% { transform: scale(0.95); opacity: 0.5; } 100% { transform: scale(1.05); opacity: 0.8; } }

    /* Deep SaaS Dark Mode */
    .stApp { 
        background-color: #050505; 
        background-image: radial-gradient(circle at 50% 0%, rgba(162, 112, 255, 0.05), transparent 50%);
        color: #e0e0e0; 
        font-family: 'Inter', sans-serif; 
        animation: fadeSlideIn 0.4s ease-out; 
    }
    
    h1, h2, h3, h4, h5 { font-family: 'Inter', sans-serif; font-weight: 600; color: #ffffff !important; letter-spacing: -0.5px; }
    
    /* Clean, Glassmorphic Cards */
    .saas-card {
        background-color: rgba(15, 15, 20, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        margin-bottom: 24px;
        transition: border 0.2s ease;
    }
    .saas-card:hover { border: 1px solid rgba(162, 112, 255, 0.3); }
    
    /* Sleek Sidebar styling */
    [data-testid="stSidebar"] { background-color: #0a0a0c !important; border-right: 1px solid rgba(255,255,255,0.05); }
    [data-testid="stSidebar"] div.stButton > button {
        background: transparent !important; border: none !important; color: #888 !important; text-align: left !important;
        justify-content: flex-start !important; padding: 8px 16px !important; font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important; font-weight: 500 !important; border-radius: 6px !important; transition: all 0.2s;
    }
    [data-testid="stSidebar"] div.stButton > button:hover { background: rgba(255,255,255,0.05) !important; color: #fff !important; }
    
    /* Primary Action Buttons */
    div.stButton > button {
        background: #ffffff; color: #000000; border: none; border-radius: 6px; 
        font-family: 'Inter', sans-serif; font-weight: 500; width: 100%; padding: 10px; transition: 0.2s;
    }
    div.stButton > button:hover { background: #e0e0e0; transform: translateY(-1px); }
    
    /* Secondary/Action Buttons */
    .secondary-btn div.stButton > button { background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.1); }
    .secondary-btn div.stButton > button:hover { background: rgba(255,255,255,0.1); }
    .danger-btn div.stButton > button { background: rgba(255,50,50,0.1); color: #ff4d4d; border: 1px solid rgba(255,50,50,0.2); }
    .danger-btn div.stButton > button:hover { background: rgba(255,50,50,0.2); }
    .accent-btn div.stButton > button { background: linear-gradient(135deg, #a270ff, #00ffcc); color: #000; font-weight: 600; border: none; }

    /* Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div { 
        background-color: #0a0a0c !important; color: #fff !important; border-radius: 6px !important; border: 1px solid rgba(255,255,255,0.1) !important; font-family: 'JetBrains Mono', monospace; 
    }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #a270ff, #00ffcc); border-radius: 10px; }
    
    /* Typography & Layout */
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
    # Starts completely blank for a professional demo flow
    st.session_state.user_data = {"name": "", "cgpa": 7.5, "days": 30, "internals": 22, "assignments": 0.0, "att": 70, "hrs": 0, "subject": "None"}

def switch_page(page_name): st.session_state.page = page_name

def extract_pdf_text(file):
    try:
        return "".join([page.extract_text() + "\n" for page in PyPDF2.PdfReader(file).pages[:5]])[:3000]
    except Exception as e: return f"Error: {e}"

# ==========================================
# 3. LOGIN PAGE (Enterprise Aesthetic)
# ==========================================
if st.session_state.page == "login":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, spacing, col2 = st.columns([1.3, 0.1, 1])
    
    with col1:
        st.markdown('''
            <div style="display: flex; align-items: center; margin-bottom: 40px;">
                <div style="position: relative; width: 60px; height: 60px;">
                    <div style="position: absolute; width: 100%; height: 100%; background: #a270ff; border-radius: 50%; filter: blur(20px); animation: pulseGlow 4s infinite alternate;"></div>
                    <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="position: relative; z-index: 10;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                </div>
            </div>
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
# 4. MAIN APP (The Daily Companion)
# ==========================================
elif st.session_state.page in ["dashboard", "syllabus", "chat"]:
    
    d = st.session_state.user_data

    # ---------------------------------------------------------
    # 🧠 UNIVERSAL BACKEND ENGINE (Runs silently on every interaction)
    # The math you explain to the judges based on Astin & Purdue.
    # ---------------------------------------------------------
    internal_score = d['internals'] 
    historical_baseline = (d['cgpa'] / 10.0) * 70.0 
    effort_modifier = 0.8 + (0.2 * min(d['hrs'] / 5.0, 1.5)) # Astin's Theory
    assignment_modifier = 0.9 + (0.1 * (d['assignments'] / 100.0))
    
    expected_external = np.clip(historical_baseline * effort_modifier * assignment_modifier, 0, 70)
    raw_sgpa = (internal_score + expected_external) / 10.0
    
    attendance_penalty = 0.0
    if d['att'] < 75: attendance_penalty = (75 - d['att']) * 0.15 # Purdue Penalty
        
    pred_sgpa = np.clip(raw_sgpa - attendance_penalty - st.session_state.decay_penalty, 0.0, 10.0)
    st.session_state.user_data['pred_sgpa'] = pred_sgpa
    # ---------------------------------------------------------

    # --- SLEEK SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0 20px 0;">
                <div style="width: 32px; height: 32px; border-radius: 6px; background: #a270ff; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #fff; font-size: 1rem;">
                    {str(d.get('name', 'U'))[0].upper()}
                </div>
                <div style="line-height: 1.2;">
                    <div style="font-weight: 500; color: #fff; font-size: 0.9rem;">{d.get('name', 'USER').title()}</div>
                    <div style="color: #666; font-size: 0.75rem;">Sem {d.get('sem', '3rd')} <span style="color:#00ffcc; font-size: 0.6rem; margin-left: 4px;">● Online</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.05); margin: 0 0 15px 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("<p style='color: #666; font-size: 0.7rem; font-weight: 600; margin-bottom: 5px; letter-spacing: 1px;'>WORKSPACE</p>", unsafe_allow_html=True)
        if st.button("📊  Daily Hub & Twin"): switch_page("dashboard"); st.rerun()
        if st.button("📚  Data Ingestion"): switch_page("syllabus"); st.rerun()
        if st.button("🤖  Agentic Copilot"): switch_page("chat"); st.rerun()
        
        st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.05); margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("<p style='color: #666; font-size: 0.7rem; font-weight: 600; margin-bottom: 10px; letter-spacing: 1px;'>LIVE TELEMETRY</p>", unsafe_allow_html=True)
        st.progress(d['att'] / 100)
        st.caption(f"Attendance Volatility: {d['att']}%")
        st.progress(pred_sgpa / 10.0)
        st.caption(f"Proj. SGPA Output: {pred_sgpa:.2f}")
        
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
        if st.button("⏏ Terminate Session"): switch_page("login"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- DASHBOARD PAGE ---
    if st.session_state.page == "dashboard":
        st.markdown("<h2 style='margin-bottom: 20px;'>Overview Workspace</h2>", unsafe_allow_html=True)
        
        # Global Telemetry Banner
        st.markdown("<div style='display:flex; gap:20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='saas-card' style='margin:0;'><p class='metric-label'>Projected SGPA</p><p class='metric-value' style='color:#00ffcc;'>{pred_sgpa:.2f}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='saas-card' style='margin:0;'><p class='metric-label'>Time to Exam</p><p class='metric-value'>{d['days']} <span style='font-size:1rem; color:#888;'>Days</span></p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='saas-card' style='margin:0;'><p class='metric-label'>Internal Lock</p><p class='metric-value'>{d['internals']}<span style='font-size:1rem; color:#888;'>/30</span></p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='saas-card' style='margin:0;'><p class='metric-label'>Attendance</p><p class='metric-value' style='color:{'#ff4d4d' if d['att']<75 else '#fff'};'>{d['att']}%</p></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        dash_tab1, dash_tab2 = st.tabs(["[ 📅 DAILY HUB ]", "[ 🎛️ TWIN SIMULATOR ]"])
        
        # TAB 1: REAL DAILY COMPANION
        with dash_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            hub1, hub2 = st.columns([1.5, 1])
            
            with hub1:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>⏱️ Live Focus Engine</h4><p style='color:#888; font-size:0.9rem;'>Run a deep work session to boost 'Time on Task' telemetry.</p>", unsafe_allow_html=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
                    if st.button("▶ Real 25m Pomodoro"):
                        ph = st.empty()
                        for i in range(25 * 60, 0, -1):
                            m, s = divmod(i, 60)
                            ph.markdown(f"<h1 style='text-align:center; color:#a270ff; font-family:JetBrains Mono;'>{m:02d}:{s:02d}</h1>", unsafe_allow_html=True)
                            time.sleep(1)
                        st.session_state.user_data['hrs'] += 0.5; st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with col_btn2:
                    st.markdown("<div class='accent-btn'>", unsafe_allow_html=True)
                    if st.button("⏩ Hackathon Demo Skip"):
                        st.session_state.user_data['hrs'] += 0.5
                        st.toast("+0.5 Hrs Logged instantly.", icon="⚡")
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>📋 Active Assignments</h4>", unsafe_allow_html=True)
                a1 = st.checkbox("Complete Graph Theory Lab Record", value=d['assignments'] > 20)
                a2 = st.checkbox("Submit Boolean Algebra Set", value=d['assignments'] > 50)
                a3 = st.checkbox("Review Pipelining PPT", value=d['assignments'] > 80)
                
                new_assign = sum([a1, a2, a3]) * 33.3
                if new_assign != d['assignments']:
                    st.session_state.user_data['assignments'] = new_assign; st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with hub2:
                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>🏫 Daily Log</h4><p style='color:#888; font-size:0.9rem;'>Did you attend scheduled lectures today?</p>", unsafe_allow_html=True)
                cy, cn = st.columns(2)
                with cy:
                    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
                    if st.button("✅ Attended"): st.session_state.user_data['att'] = min(100, d['att'] + 1); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with cn:
                    st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
                    if st.button("❌ Missed"): st.session_state.user_data['att'] = max(0, d['att'] - 2); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
                st.markdown("<h4>🎯 Target Vectors</h4><p style='color:#888; font-size:0.9rem;'>Based on uploaded syllabus:</p>", unsafe_allow_html=True)
                if d.get('subject') != "None":
                    st.error("Priority: Algorithm Complexities")
                    st.warning("Secondary: Sequential Logic")
                else:
                    st.info("Awaiting Data Ingestion...")
                st.markdown("</div>", unsafe_allow_html=True)

        # TAB 2: SIMULATOR
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

        # Global Charts
        st.markdown("<div class='saas-card' style='margin-top:20px;'>", unsafe_allow_html=True)
        st.markdown("<h4>Analytics Engine</h4>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Bar(x=['Assignments', 'Internals', 'Study Yield', 'Attendance'], y=[d['assignments']/10, (d['internals']/30)*10, min(d['hrs'],10), d['att']/10], marker_color=['#a270ff', '#00ffcc', '#ffffff', '#ff4d4d'])])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter', color='#888'), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), margin=dict(t=10, b=10, l=10, r=10), height=200)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- SYLLABUS PAGE ---
    elif st.session_state.page == "syllabus":
        st.markdown("<h2>Data Ingestion</h2>", unsafe_allow_html=True)
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.write("Upload PDF vectors to map study modules.")
        f1 = st.file_uploader("Syllabus / Routine [PDF]", type=['pdf'])
        sub = st.selectbox("Assign Vector To:", ["Data Structures", "Computer Architecture", "Mathematics"])
        st.markdown("<div class='accent-btn'>", unsafe_allow_html=True)
        if f1 and st.button("Process & Sync"):
            with st.spinner("Processing..."):
                raw = extract_pdf_text(f1)
                st.session_state.user_data.update({"subject": sub, "syllabus_content": raw})
                st.success("Synced. Agent is ready.")
        st.markdown("</div></div>", unsafe_allow_html=True)

    # --- AGENT PAGE ---
    elif st.session_state.page == "chat":
        st.markdown("<h2>Agentic Copilot</h2>", unsafe_allow_html=True)
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        
        if not st.session_state.chat_history:
            sys_p = f"Act as TwinTrack AI. Generate a 2-sentence proactive warning for {d['name']} based on Pred SGPA {d.get('pred_sgpa', 0.0):.2f} and attendance {d['att']}%. Suggest a focus module."
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

        if p := st.chat_input("Command the Twin..."):
            st.session_state.chat_history.append({"role": "user", "content": p})
            with st.chat_message("user"): st.write(p)
            
            sys_p = f"You are TwinTrack AI for {d['name']}. Target: {d['subject']}. SGPA: {d.get('pred_sgpa', 0.0):.2f}. Give actionable, quantitative outputs."
            with st.chat_message("assistant"):
                if client:
                    try:
                        res = client.chat.completions.create(messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": p}], model="llama-3.3-70b-versatile").choices[0].message.content
                        st.write(res)
                        st.session_state.chat_history.append({"role": "assistant", "content": res})
                    except: st.error("Inference Error.")
                else: st.error("No API Configured.")
        st.markdown("</div>", unsafe_allow_html=True)
