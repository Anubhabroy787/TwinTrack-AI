import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai

st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1 { text-shadow: 0 0 10px #00d2ff; font-family: 'Orbitron', sans-serif; }
    div.stButton > button {
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        color: white; border: none; border-radius: 8px; transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0px 0px 15px rgba(0, 210, 255, 0.6); }
</style>
""", unsafe_allow_html=True)

# Pull the key safely from Streamlit's hidden secrets
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# state management
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def switch_page(page_name):
    st.session_state.page = page_name
    st.rerun()

if st.session_state.page == "landing":
    st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <h1 style="font-size: 60px; font-weight: 900; color: #1E88E5;">TwinTrack AI</h1>
            <h3 style="color: #43A047;">A Digital Twin for Student Life</h3>
            <p style="color: gray; margin-bottom: 0px;">An Initiative by <b>Royal Bengal Coders</b></p>
            <p style="font-size: 12px; color: gray;">(Ankit Biswas, Argha Banerjee, Priyanshu Saha, Anubhab Roy, Chandradeep Mondal)</p>
            <br>
            <h4 style="font-style: italic;"> "Stop guessing your future outcome - TwinTrack AI predicts your performance and guides you with a smart study roadmap." </h4>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.button("🚀 Start Your Journey", use_container_width=True, on_click=switch_page, args=("login",))

elif st.session_state.page == "login":
    st.markdown("<h2 style='text-align: center;'>Welcome to TwinTrack AI</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    with tab1:
        st.text_input("Email ID")
        st.text_input("Password", type="password")
        st.button("Sign In", use_container_width=True, on_click=switch_page, args=("intake",))
        st.divider()
        st.button("Continue with Google 🌐", use_container_width=True)
    with tab2:
        st.text_input("Full Name")
        st.text_input("Email ID", key="reg_email")
        st.button("Create Account", use_container_width=True, on_click=switch_page, args=("intake",))

elif st.session_state.page == "intake":
    st.markdown("## 📝 Academic Credentials")
    
    u_name = st.text_input("Your Name:", value=st.session_state.user_data.get("name", ""))
    col1, col2 = st.columns(2)
    with col1:
        course = st.selectbox("Pursuing Course:", ["Select", "B.Tech", "BBA", "BCA"])
        year = st.selectbox("Current Year of Study:", ["Select", "1st", "2nd", "3rd", "4th"])
    with col2:
        sem = st.selectbox("Current Semester:", ["Select", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"])
    
    if st.button("Next ➡️", use_container_width=True):
        if "Select" in [course, year, sem] or not u_name:
            st.error("Please fill all fields!")
        else:
            st.session_state.user_data.update({"name": u_name, "course": course, "year": year, "sem": sem})
            switch_page("analysis")

elif st.session_state.page == "analysis":
    d = st.session_state.user_data
    st.info(f"Hey {d['name']}, you are pursuing {d['course']}, Year {d['year']}, Sem {d['sem']}.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        att = st.number_input("Attendance percentage (0-100):", min_value=0, max_value=100, value=70)
        cgpa = st.number_input("Overall CGPA till now:", min_value=0.0, max_value=10.0, format="%.2f", value=7.5)
    with col_b:
        days = st.number_input("Days left for upcoming exam:", min_value=0, value=30)
        hrs = st.number_input("Hours of study at home:", min_value=0, value=2)

    # digital twin sim graph
    st.markdown("### 📈 Your Digital Twin Trajectory")
    hours_range = np.linspace(0, 10, 20)
    predicted_trend = np.clip(cgpa + (hours_range * 0.2) + ((att-75) * 0.01), 0, 10)
    df_trend = pd.DataFrame({"Study Hours": hours_range, "Predicted CGPA": predicted_trend})
    
    fig = px.line(df_trend, x="Study Hours", y="Predicted CGPA", template="plotly_dark")
    fig.add_scatter(x=[hrs], y=[np.clip(cgpa + (hrs * 0.2) + ((att-75) * 0.01), 0, 10)], 
                    mode='markers', marker=dict(size=12, color='red'), name="Your Current Twin")
    st.plotly_chart(fig, use_container_width=True)

    # check size before processing
    st.markdown("### 📂 Submit Your Syllabus")
    file = st.file_uploader("Upload Syllabus", type=['pdf', 'txt'])
    st.markdown("<p style='color:red; font-size:12px;'>(The file size should not exceed 50 MB)</p>", unsafe_allow_html=True)

    if file:
        if file.size > 50 * 1024 * 1024:
            st.error("File exceeds 50MB limit!")
        else:
            st.success("Syllabus analyzed!")
            subjects = ["Data Structures & Algorithms", "Computer Architecture", "Digital Logic", "Mathematics"]
            sub = st.selectbox("In which subject do you need help?", subjects)
            
            if st.button("Generate Strategy 🚀", use_container_width=True):
                st.session_state.user_data.update({"att": att, "days": days, "cgpa": cgpa, "hrs": hrs, "subject": sub})
                switch_page("chat")

elif st.session_state.page == "chat":
    d = st.session_state.user_data
    
    with st.sidebar:
        st.title("TwinTrack Controls")
        if st.button("➕ New Chat"):
            st.session_state.chat_history = []
            switch_page("intake")
        st.divider()
        st.write(f"**Target Subject:** {d['subject']}")
        st.write(f"**Current Attendance:** {d['att']}%")
        st.write(f"**Days to Exam:** {d['days']}")

    st.markdown("### 🤖 Virtual Educator")
    
    # init prompt constraints
    if not st.session_state.chat_history:
        att_msg = "Your attendance is above 75%. You can strategically bunk some non-essential classes to increase your home study hours." if d['att'] >= 75 else f"CRITICAL: Your attendance is {d['att']}%. You must attend the next classes to hit the 75% criteria. Do not bunk."
        cgpa_msg = "To improve your CGPA, let's focus on high-weightage topics."
        st.session_state.chat_history.append({"role": "assistant", "content": f"Hello {d['name']}! {att_msg} {cgpa_msg} Based on the syllabus for {d['subject']}, I have prepared the hot topics. What would you like to start with?"})

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Talk to your Virtual Educator..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        sys_prompt = f"System Instruction: You are a Virtual Educator for {d['name']}. ONLY discuss academics, exams, and study routines. If the user asks about anything outside of education, strictly reply with: 'Sorry to interrupt, I am your virtual educator. I will only give suggestions about your academics so I can't help you in this matter.' The current subject is {d['subject']}."
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = gemini_model.generate_content(f"{sys_prompt}\n\nUser Question: {prompt}")
                st.write(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
