import re

def main():
    # 1. Update config.toml
    config = """[server]
address = "127.0.0.1"
port = 8501

[client]
toolbarMode = "minimal"

[theme]
base = "dark"
primaryColor = "#3B82F6"
backgroundColor = "#09090b"
secondaryBackgroundColor = "#121214"
textColor = "#FAFAFA"
font = "sans serif"
"""
    with open('.streamlit/config.toml', 'w', encoding='utf-8') as f:
        f.write(config)

    # 2. Update app.py CSS and Dashboard
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_theme = '''def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #09090b !important;
        color: #FAFAFA !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1100px !important;
    }
    
    /* Elegant Dark Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #121214 !important;
        border-right: 1px solid #27272A !important;
    }
    .sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid #27272A; margin-bottom: 1rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 50px; height: 50px; background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem; }
    .sidebar-brand h2 { margin: 0; font-size: 1.1rem; color: #FAFAFA !important; font-weight: 700; letter-spacing: -0.01em; }
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.75rem; color: #A1A1AA !important; font-weight: 500; }
    
    /* Modern Navigation Tabs (replacing radio buttons) */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.3rem; padding: 0 0.5rem; }
    /* Completely hide the radio circle */
    [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display: none !important; width: 0 !important; }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.65rem 1rem !important;
        border-radius: 6px !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        cursor: pointer;
        transition: all 0.15s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: #18181B !important;
    }
    /* Active Tab */
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: #27272A !important;
        border: 1px solid #3F3F46 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    /* Tab Text */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: #A1A1AA !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }

    /* Fix Sidebar Hamburger (No SVG arrow) */
    [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarCollapseButton"] button {
        color: transparent !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg { 
        display: none !important; opacity: 0 !important; width: 0 !important; height: 0 !important; 
    }
    [data-testid="stSidebarCollapseButton"]::after, [data-testid="stSidebarCollapsedControl"]::after {
        content: "\\2630";
        font-size: 1.5rem;
        color: #A1A1AA;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        display: block;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: #FAFAFA !important;
        border: none !important;
        color: #09090b !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #E4E4E7 !important;
    }
    .stButton > button[kind="secondary"] {
        background: #18181B !important;
        border: 1px solid #3F3F46 !important;
        color: #FAFAFA !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: #27272A !important;
        border-color: #52525B !important;
    }

    /* Modern Dark Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card, .kpi-card {
        background: #121214 !important; 
        border: 1px solid #27272A !important; 
        border-radius: 12px !important; 
        padding: 1.5rem !important; 
        margin-bottom: 1.5rem !important; 
        color: #FAFAFA !important;
    }
    
    .mota-kicker, .application-tracker-kicker { color: #60A5FA !important; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .page-intro h2 { color: #FAFAFA !important; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; }
    .page-intro p { color: #A1A1AA !important; }
    
    /* Form inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        background-color: #18181B !important;
        border: 1px solid #3F3F46 !important;
        color: #FAFAFA !important;
        border-radius: 6px !important;
    }
    
    /* Text overrides */
    .stMarkdown p, .stMarkdown span { color: #D4D4D8 !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FAFAFA !important; }
</style>
        """,
        unsafe_allow_html=True,
    )'''

    new_dashboard = '''def render_dashboard(applicants: list[ApplicantProfile], results: list[CompositeEvaluationResult]) -> None:
    profile = st.session_state.get("user_profile", {})
    missing_fields = [field for field in PROFILE_REQUIRED_FIELDS if not profile.get(field)]
    profile_complete = bool(st.session_state.get("profile_complete", False)) or profile_is_complete(profile)

    st.markdown(
        """
        <div style="background: radial-gradient(circle at 10% 20%, #171717 0%, #09090b 100%); padding: 3.5rem 3rem; border-radius: 16px; margin-bottom: 3rem; border: 1px solid #27272A; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="position: absolute; right: -50px; top: -50px; width: 300px; height: 300px; background: rgba(59,130,246,0.1); filter: blur(80px); border-radius: 50%;"></div>
            <div style="position: relative; z-index: 1;">
                <h1 style="margin: 0 0 1rem 0; font-size: 3rem; font-weight: 800; color: #FAFAFA; line-height: 1.1; letter-spacing: -0.03em;">Smart Scholarship<br>Audit Engine</h1>
                <p style="margin: 0; font-size: 1.15rem; color: #A1A1AA; max-width: 600px; line-height: 1.5; font-weight: 400;">
                    A unified, AI-driven platform for eligibility matching, document compliance, and rapid disbursements.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3 style='margin-bottom: 1.5rem; font-size: 1.25rem; color: #FAFAFA; font-weight: 600; letter-spacing: -0.01em;'>Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="background: #121214; border: 1px solid #27272A; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%;">
                <div style="width: 40px; height: 40px; background: #18181B; border: 1px solid #3F3F46; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FAFAFA;">👤</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">1. My Profile</h3>
                <p style="color: #A1A1AA; font-size: 0.9rem; margin: 0; line-height: 1.5;">Ensure your demographic and academic details are up to date for precise AI matching.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Update Profile", use_container_width=True, key="dashboard_profile_btn"):
            st.session_state["pending_workspace_view"] = "My Profile"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div style="background: #121214; border: 1px solid #3B82F6; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; position: relative; box-shadow: inset 0 0 0 1px rgba(59,130,246,0.2);">
                <div style="position: absolute; top: -10px; right: 20px; background: #3B82F6; color: #09090b; font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.6rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em;">Primary Step</div>
                <div style="width: 40px; height: 40px; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #60A5FA;">✨</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">2. Find Scholarships</h3>
                <p style="color: #A1A1AA; font-size: 0.9rem; margin: 0; line-height: 1.5;">Discover and evaluate your eligibility against active schemes instantly.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Check Eligibility", use_container_width=True, type="primary", key="dashboard_find"):
            if profile_complete:
                st.session_state["dashboard_profile_error"] = False
                st.session_state["pending_workspace_view"] = "Scholarship Results"
                st.session_state["step"] = 2
                st.rerun()
            else:
                st.session_state["dashboard_profile_error"] = True
                
        if st.session_state.get("dashboard_profile_error", False):
            st.error("⚠️ Profile is incomplete. Please complete your profile first.")

    with col3:
        st.markdown(
            """
            <div style="background: #121214; border: 1px solid #27272A; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%;">
                <div style="width: 40px; height: 40px; background: #18181B; border: 1px solid #3F3F46; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FAFAFA;">📊</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">3. Track Status</h3>
                <p style="color: #A1A1AA; font-size: 0.9rem; margin: 0; line-height: 1.5;">Monitor your document audits, deficiency notices, and approval statuses.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("View Applications", use_container_width=True, key="dashboard_track_btn"):
            st.session_state["pending_workspace_view"] = "My Applications"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background: #121214; border: 1px solid #27272A; border-radius: 12px; padding: 1.5rem; display: flex; gap: 1.5rem; align-items: center;">
            <div style="width: 50px; height: 50px; background: #18181B; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; border: 1px solid #3F3F46;">🛡️</div>
            <div>
                <h4 style="margin: 0 0 0.25rem 0; color: #FAFAFA; font-size: 1rem; font-weight: 600;">Enterprise Grade Intelligence</h4>
                <p style="margin: 0; color: #A1A1AA; font-size: 0.85rem; line-height: 1.5;">
                    The Audit Engine automatically evaluates strict multi-constraint policy rules for Pre-Matric, Post-Matric, Higher Education, National Fellowship, and NOS schemes. It features real-time demographic validation, academic scoring checks, and risk flagging based on historical data.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )'''

    content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_theme, content, flags=re.DOTALL)
    content = re.sub(r'def render_dashboard\(.*?\).*?def render_saved_scholarship_results', new_dashboard + '\n\ndef render_saved_scholarship_results', content, flags=re.DOTALL)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        print("Successfully applied professional Dark Mode, Tabs, and Arrow overrides!")

if __name__ == "__main__":
    main()
