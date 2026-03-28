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

# --- PHASE 2: PLACEHOLDER (Up Next) ---
elif st.session_state.page == "intake":
    st.success("Authentication Successful! Welcome to the inside of the app.")
    st.button("⬅️ Restart Demo", on_click=switch_page, args=("landing",))