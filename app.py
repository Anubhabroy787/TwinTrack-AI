import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import PyPDF2
import time

# --- UI & CSS CONFIGURATION (The "Cool & Smooth" Factor) ---
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    /* Dark Theme & Smooth Transitions */
    .stApp { background-color: #0b0f19; color: #e0e6ed; }
    
    /* Glowing Title */
    h1 { 
        text-shadow: 0 0 20px rgba(0, 210, 255, 0.8); 
        font-family: 'Orbitron', sans-serif; 
        text-align: center;
    }
    
    /* Animated Gradient Buttons */
    div.stButton > button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white; 
        border: none; 
        border-radius: 10px; 
        transition: all 0.4s ease;
        font-weight: bold;
        box-shadow: 0px 4px 15px rgba(0, 114, 255, 0.4);
    }
    div.stButton > button:hover { 
        transform: translateY(-3px) scale(1.02); 
        box-shadow: 0px 8px 25px rgba(0, 210, 255, 0.8); 
    }
    
    /* Clean Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #161b22;
        color: #00d2ff;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- API & BACKEND SETUP (GEMINI 2.0 FLASH) ---
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def switch_page(page_name):
    st.session_state.page = page_name
    # st.rerun() removed to kill the yellow warning bug!

# --- PDF SMART SCANNER ---
def extract_semester_syllabus(file, subject_name, semester_val):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        sem_str = f"Semester {semester_val}"
        sem_alt = f"{semester_val} Semester"
        sem_short = f"Sem {semester_val}"
        
        relevant_pages = []
        for page in pdf_reader.pages:
            p_text = page.extract_text()
            if p_text and any(s.lower() in p_text.lower() for s in [sem_str, sem_alt, sem_short]):
                if subject_name.lower() in p_text.lower():
                    relevant_pages.append(p_text)
        
        if not relevant_pages: # Fallback if specific semester string isn't perfectly matched
            for page in pdf_reader.pages:
                p_text = page.extract_text()
                if p_text and subject_name.lower() in p_text.lower():
                    relevant_pages.append(p_text)
                    
        return "\n".join(relevant_pages)[:6000] # Cap for speed
    except Exception as e:
        return f"Syllabus extraction failed: {e}"

# ==========================================
# PHASE 1: LANDING PAGE
# ==========================================
if st.session_state.page == "landing":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 70px; font-weight: 900; background: -webkit-linear-gradient(#00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TwinTrack AI</h1>
            <h3 style="color: #a3b8cc; letter-spacing: 2px;">THE ACADEMIC DIGITAL TWIN</h3>
            <p style="color: #58a6ff; font-family: monospace;">Developed by the Royal Bengal Coders</p>
            <br>
            <h5 style="font-style: italic; color: #8b949e; max-width: 600px; margin: auto;">"Stop guessing your trajectory. Upload your syllabus, visualize your future, and let Gemini 2.0 calculate your exact survival path."</h5>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("⚡ INITIALIZE SYSTEM", use_container_width=True, on_click=switch_page, args=("login",))

# ==========================================
# PHASE 1.5: AUTHENTICATION
# ==========================================
elif st.session_state.page == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #00d2ff;'>Access Portal</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        with tab1:
            st.text_input("Email ID", value="anubhab@narula.edu")
            st.text_input("Password", type="password", value="********")
            st.button("Secure Login", use_container_width=True, on_click=switch_page, args=("intake",))
        with tab2:
            st.text_input("Full Name")
            st.text_input("Email ID", key="register_email") # Duplicate ID Bug Fixed!
            st.button("Create Account", use_container_width=True, on_click=switch_page, args=("intake",))

# ==========================================
# PHASE 2: INTAKE (Pre-filled for Demo)
# ==========================================
elif st.session_state.page == "intake":
    st.markdown("<h2 style='color: #00d2ff;'>📝 Calibration Matrix</h2>", unsafe_allow_html=True)
    st.markdown("Enter your current academic vectors.")
    
    u_name = st.text_input("Student Designation:", value=st.session_state.user_data.get("name", "Anubhab Roy"))
    col1, col2 = st.columns(2)
    with col1:
        course = st.selectbox("Program:", ["B.Tech", "BBA", "BCA", "Select"], index=0)
        year = st.selectbox("Year:", ["1st", "2nd", "3rd", "4th", "Select"], index=1)
    with col2:
        sem = st.selectbox("Semester:", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "Select"], index=2)
    
    st.write("")
    if st.button("Generate Trajectory ➡️", use_container_width=True):
        st.session_state.user_data.update({"name": u_name, "course": course, "year": year, "sem": sem})
        switch_page("analysis")

# ==========================================
# PHASE 3: THE 3D DIGITAL TWIN & PDF SCAN
# ==========================================
elif st.session_state.page == "analysis":
    d = st.session_state.user_data
    st.toast(f"Profile Synced: {d['name']} | {d['course']} Sem {d['sem']}", icon="✅")
    
    col_a, col_b = st.columns(2)
    with col_a:
        att = st.number_input("Current Attendance (%):", min_value=0, max_value=100, value=70)
        cgpa = st.number_input("Current CGPA:", min_value=0.0, max_value=10.0, format="%.2f", value=7.5)
    with col_b:
        days = st.number_input("Days to Exam:", min_value=0, value=30)
        hrs = st.number_input("Daily Study Hours:", min_value=0, value=2)

    st.divider()
    
    # --- COOL 3D GRAPHIC ---
    st.markdown("<h3 style='color: #00d2ff;'>🌌 3D Digital Twin Projection</h3>", unsafe_allow_html=True)
    
    # Create mesh data for 3D surface
    study_mesh = np.linspace(0, 10, 20)
    att_mesh = np.linspace(0, 100, 20)
    study_grid, att_grid = np.meshgrid(study_mesh, att_mesh)
    cgpa_grid = np.clip(cgpa + (study_grid * 0.15) + ((att_grid - 75) * 0.01), 0, 10)

    fig = go.Figure(data=[go.Surface(z=cgpa_grid, x=study_grid, y=att_grid, colorscale='Tealgrn', opacity=0.8)])
    
    # Plot the user's EXACT current position as a glowing red orb
    current_predicted_cgpa = np.clip(cgpa + (hrs * 0.15) + ((att - 75) * 0.01), 0, 10)
    fig.add_trace(go.Scatter3d(
        x=[hrs], y=[att], z=[current_predicted_cgpa],
        mode='markers', marker=dict(size=8, color='red', symbol='circle', line=dict(color='white', width=2)),
        name='Your Current Twin'
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Study Hours', yaxis_title='Attendance %', zaxis_title='Predicted CGPA',
            xaxis=dict(backgroundcolor="black", gridcolor="gray"),
            yaxis=dict(backgroundcolor="black", gridcolor="gray"),
            zaxis=dict(backgroundcolor="black", gridcolor="gray")
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=0), height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- PDF UPLOAD & SMART SCAN ---
    st.markdown("<h3 style='color: #00d2ff;'>📂 Inject Syllabus Data</h3>", unsafe_allow_html=True)
    file = st.file_uploader("Upload University Syllabus (PDF)", type=['pdf'])

    if file:
        st.success("File verified. Ready for extraction.")
        subjects = ["Data Structures & Algorithms", "Computer Organization", "Digital Logic", "Mathematics"]
        sub = st.selectbox("Target Extraction Subject:", subjects, index=0)
        
        if st.button("🔥 INITIALIZE BEAST MODE", use_container_width=True):
            # Simulated smooth loading bar for presentation wow-factor
            progress_text = "Parsing Vector Data..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            my_bar.empty()
            
            with st.spinner(f"Executing Smart Scan for '{sub}' in Sem {d['sem']}..."):
                raw_syllabus = extract_semester_syllabus(file, sub, d['sem'])
                
                st.session_state.user_data.update({
                    "att": att, "days": days, "cgpa": cgpa, 
                    "hrs": hrs, "subject": sub, 
                    "syllabus_content": raw_syllabus
                })
            st.balloons()
            switch_page("chat")

# ==========================================
# PHASE 4: THE BEAST (GEMINI 2.0 Chat)
# ==========================================
elif st.session_state.page == "chat":
    d = st.session_state.user_data
    
    # -- Navigation & Metrics Sidebar --
    with st.sidebar:
        st.markdown("<h2 style='color: #00d2ff;'>Twin Controls</h2>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Analysis"): switch_page("analysis")
        if st.button("🔄 System Reset"): 
            st.session_state.chat_history = []
            switch_page("intake")
        
        st.divider()
        st.markdown(f"**Target Subject:** `{d['subject']}`")
        st.markdown(f"**Attendance:** `{d['att']}%`")
        st.markdown(f"**Exam T-Minus:** `{d['days']} Days`")
        st.markdown(f"**Daily Output:** `{d['hrs']} Hrs`")

    st.markdown("<h2 style='color: #00d2ff;'>🤖 Tactical Virtual Educator</h2>", unsafe_allow_html=True)
    
    # -- Initial Contextual Output --
    if not st.session_state.chat_history:
        status = "🔴 CRITICAL - ATTENDANCE RISK" if d['att'] < 75 else "🟢 STABLE - TACTICAL BUNK AUTHORIZED"
        with st.status("Syncing Gemini 2.0 Neural Link...", expanded=True) as status_box:
            st.write("Injecting syllabus matrix...")
            st.write("Calibrating attendance constraints...")
            st.write("Generating optimal survival path...")
            time.sleep(1) # Dramatic effect
            status_box.update(label="Digital Twin Synced!", state="complete", expanded=False)

        initial_msg = f"**System Initialized.** Status: {status}. \n\n{d['name']}, we have {d['days']} days to secure {d['subject']}. I have scanned the university syllabus. Based on your current {d['cgpa']} CGPA, I have formulated a specific attack plan. What topic are we starting with?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_msg})

    # -- Render Chat --
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): 
            st.write(msg["content"])

    # -- User Input & AI Processing --
    if prompt := st.chat_input("Command your TwinTrack Strategist..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.write(prompt)
        
        # The Context-Heavy "Beast" Prompt adapted for Gemini
        syllabus_data = d.get('syllabus_content', 'General topics only.')
        
        # Gemini takes everything natively as text context.
        gemini_prompt = f"""
        SYSTEM INSTRUCTIONS:
        You are 'TwinTrack AI', a high-performance, slightly strict Academic Strategist for an engineering student named {d['name']}.
        
        USER DATA:
        - Student: {d['name']} | Semester: {d['sem']}
        - Target: {d['subject']} in {d['days']} days
        - Current Stats: {d['att']}% Attendance | {d['cgpa']} CGPA | Studies {d['hrs']} hrs/day.
        
        RAW SYLLABUS DATA EXTRACTED FROM PDF:
        {syllabus_data}
        
        STRATEGY RULES:
        1. Base your teaching ONLY on the 'RAW SYLLABUS DATA' provided above. Mention specific topics from it.
        2. If attendance < 75%, rigidly warn them they are failing the 75% criteria rule.
        3. Determine if studying {d['hrs']} hours a day is actually enough math to cover the syllabus in {d['days']} days. Tell them the truth.
        4. If they ask about games, movies, or non-academics, shut it down immediately and redirect to {d['subject']}.
        5. Keep responses highly structured, using bullet points and bold text for readability.

        ------------------
        USER COMMAND:
        {prompt}
        """
        
        with st.chat_message("assistant"):
            with st.spinner("Processing tactical response via Gemini 2.0..."):
                try:
                    # Request generation from Gemini
                    response = model.generate_content(gemini_prompt)
                    bot_response = response.text
                    
                    st.write(bot_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                    
                except Exception as e:
                    # Provide debug info inside the app to catch issues during hackathon prep
                    st.error(f"⚠️ Neural Link Error: Check your Streamlit Secrets and API Quota. Details: {e}")
