import streamlit as st

# --- PAGE CONFIGURATION ---
# This sets the browser tab name and sets the layout to center for a clean look
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="centered")

# --- SESSION STATE (The "Memory" of the App) ---
# This tells the app which page to show. It starts on the "landing" page.
if "page" not in st.session_state:
    st.session_state.page = "landing"

def switch_page(page_name):
    st.session_state.page = page_name

# --- PHASE 1: THE LANDING PAGE ---
if st.session_state.page == "landing":
    
    # Custom HTML/CSS to make the text bold, centered, and premium
    st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <h1 style="font-size: 65px; font-weight: 900; margin-bottom: 0px; color: #1E88E5;">TwinTrack AI</h1>
            <h3 style="margin-top: 5px; color: #43A047;">A Digital Twin for Student Life</h3>
            <br>
            <p style="font-size: 16px; color: gray; margin-bottom: 0px;">An Initiative by <b>Royal Bengal Coders</b></p>
            <p style="font-size: 14px; color: gray; margin-top: 0px;">(Ankit Biswas, Argha Banerjee, Priyanshu Saha, Anubhab Roy, Chandradeep Mondal)</p>
            <br><br>
            <h4 style="font-weight: 500; font-style: italic; line-height: 1.5;">
                "Stop guessing your future outcome - TwinTrack AI predicts your performance and guides you with a smart study roadmap."
            </h4>
        </div>
    """, unsafe_allow_html=True)

    # Centering the start button using columns
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        # When clicked, it changes the session state to "login"
        st.button("🚀 Start Your Journey", use_container_width=True, type="primary", on_click=switch_page, args=("login",))

# --- PHASE 1.5: THE AUTHENTICATION SCREEN ---
elif st.session_state.page == "login":
    
    # The Dark/Light Mode Note (Streamlit does this natively via the top-right menu)
    st.markdown("<div style='text-align: right; color: gray;'>🌗 <i>Toggle Dark/Light mode in the top right menu (⋮)</i></div>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>Welcome to TwinTrack AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sign in to access your Digital Twin</p>", unsafe_allow_html=True)
    
    # Create Sign In and Sign Up tabs
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.text_input("Email ID")
        st.text_input("Password", type="password")
        # For the hackathon demo, clicking login moves us to the next phase
        st.button("Sign In", type="primary", use_container_width=True, on_click=switch_page, args=("intake",))
        
        st.divider()
        # Mock Social Logins
        st.button("Continue with Google 🌐", use_container_width=True)
        st.button("Continue with GitHub 🐙", use_container_width=True)
        st.button("Continue with Microsoft 🪟", use_container_width=True)

    with tab2:
        st.text_input("Full Name")
        st.text_input("Email ID ", key="signup_email")
        st.text_input("Create Password", type="password")
        st.button("Create Account", type="primary", use_container_width=True, on_click=switch_page, args=("intake",))

import google.generativeai as genai

# --- 2. INITIALIZE GEMINI API ---
# Using the key you generated earlier
genai.configure(api_key="AIzaSyATyZtvD5t_XscM3b7ZFdvh7gFfSjhvp7U")
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# --- SESSION STATE INITIALIZATION ---
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- PHASE 2: THE ACADEMIC INTAKE ENGINE ---
elif st.session_state.page == "intake":
    st.markdown("<h2 style='text-align: center;'>🎓 Academic Credentials</h2>", unsafe_allow_html=True)
    
    # Pre-filling credentials if they exist (for "New Chat" functionality)
    u_name = st.text_input("Your Name:", value=st.session_state.user_data.get("name", ""))
    
    col1, col2 = st.columns(2)
    with col1:
        course = st.selectbox("Pursuing Course:", ["Select", "B.Tech", "BBA", "BCA"], 
                              index=0 if not st.session_state.user_data.get("course") else ["Select", "B.Tech", "BBA", "BCA"].index(st.session_state.user_data["course"]))
        year = st.selectbox("Current Year of Study:", ["Select", "1st", "2nd", "3rd", "4th"],
                             index=0 if not st.session_state.user_data.get("year") else ["Select", "1st", "2nd", "3rd", "4th"].index(st.session_state.user_data["year"]))
    
    with col2:
        semester = st.selectbox("Current Semester:", ["Select", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"],
                                 index=0 if not st.session_state.user_data.get("sem") else ["Select", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"].index(st.session_state.user_data["sem"]))

    if st.button("Next ➡️", type="primary", use_container_width=True):
        if "Select" in [course, year, semester] or not u_name:
            st.error("Please fill all fields to continue.")
        else:
            st.session_state.user_data.update({"name": u_name, "course": course, "year": year, "sem": semester})
            switch_page("metrics")

# --- PHASE 3: ATTENDANCE & SYLLABUS ANALYSIS ---
elif st.session_state.page == "metrics":
    data = st.session_state.user_data
    st.markdown(f"### Hey {data['name']}!")
    st.info(f"You are pursuing {data['course']}, Year {data['year']}, Semester {data['sem']}.")
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        att_pct = st.number_input("Attendance percentage in your college:", min_value=0, max_value=100)
        cgpa = st.number_input("Overall CGPA till now:", min_value=0.0, max_value=10.0, format="%.2f")
    with col_b:
        days_left = st.number_input("How many days left for the upcoming exam:", min_value=0)
        home_study = st.number_input("Hour of study in home:", min_value=0)

    # Syllabus Upload with 50MB Constraint
    st.markdown("#### 📂 Submit Your Syllabus")
    uploaded_syllabus = st.file_uploader("Upload File (PDF/TXT)", type=["pdf", "txt"])
    st.markdown("<p style='color:red; font-size:12px;'>(The file size should not exceed 50 MB)</p>", unsafe_allow_html=True)

    if uploaded_syllabus:
        if uploaded_syllabus.size > 50 * 1024 * 1024:
            st.error("File is too large! Please upload a file smaller than 50MB.")
        else:
            st.success("Syllabus received.")
            # For hackathon demo, we simulate subject extraction
            st.markdown(f"**Subjects detected for {data['sem']} Semester:**")
            subjects = ["Data Structures", "Digital Electronics", "Computer Organization", "Mathematics"]
            selected_sub = st.selectbox("In which subject you need help?", subjects)
            
            if st.button("Generate Study Roadmap 🚀"):
                st.session_state.user_data.update({
                    "att": att_pct, "days": days_left, "cgpa": cgpa, 
                    "hrs": home_study, "subject": selected_sub
                })
                switch_page("chat")

# --- PHASE 4: THE VIRTUAL EDUCATOR CHAT ---
elif st.session_state.page == "chat":
    # Sidebar for "New Chat" and Status
    with st.sidebar:
        st.title("Settings")
        if st.button("➕ New Chat"):
            # Reset chat but keep credentials for pre-filling
            st.session_state.chat_history = []
            switch_page("intake")
        st.divider()
        st.write(f"**Subject:** {st.session_state.user_data['subject']}")
        st.write(f"**Attendance:** {st.session_state.user_data['att']}%")

    st.markdown(f"### 🤖 TwinTrack AI: Virtual Educator")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about your academics..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini AI Logic with Strict Education Guardrails
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                system_instruction = f"""
                You are a 'Virtual Educator'. 
                User Context: {st.session_state.user_data['name']} is a {st.session_state.user_data['course']} student.
                Subject: {st.session_state.user_data['subject']}. Days left for exam: {st.session_state.user_data['days']}.
                Attendance: {st.session_state.user_data['att']}%. CGPA: {st.session_state.user_data['cgpa']}.
                
                STRICT RULES:
                1. ONLY discuss academics, exam suggestions, and study strategies.
                2. If the user asks about non-educational topics, strictly say: 'Sorry to interrupt, I am your virtual educator. I will only give suggestions about your academics so I can't help you in this matter.'
                3. If attendance < 75%, suggest attending key classes to reach 75%. If > 75%, suggest how to balance study time.
                """
                
                full_prompt = f"{system_instruction}\n\nUser Question: {prompt}"
                response = gemini_model.generate_content(full_prompt)
                
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})