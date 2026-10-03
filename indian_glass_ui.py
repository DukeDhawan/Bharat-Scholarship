import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_theme = '''def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Breathtaking "Made in India" Abstract Dark Wallpaper */
    .stApp {
        background: 
            radial-gradient(circle at 10% 30%, rgba(255, 153, 51, 0.2), transparent 40%),
            radial-gradient(circle at 90% 70%, rgba(19, 136, 8, 0.2), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(0, 0, 128, 0.25), transparent 50%),
            url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(5, 5, 7, 0.7); /* Dark overlay to keep UI legible */
        z-index: -1;
    }
    
    /* Glassmorphism Main Container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px !important;
        background: rgba(18, 18, 20, 0.5) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(255, 153, 51, 0.25);
        border-bottom: 1px solid rgba(19, 136, 8, 0.25);
        margin-top: 2rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
    }
    
    /* Glassmorphism Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(18, 18, 20, 0.5) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 1rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 50px; height: 50px; background: linear-gradient(135deg, #FF9933 0%, #138808 100%); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem; box-shadow: 0 0 20px rgba(255,153,51,0.2); }
    .sidebar-brand h2 { margin: 0; font-size: 1.1rem; color: #FAFAFA !important; font-weight: 700; letter-spacing: -0.01em; }
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.7) !important; font-weight: 500; }
    
    /* Hide Radio Label */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    /* Modern Navigation Tabs */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.3rem; padding: 0 0.5rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display: none !important; width: 0 !important; }
    
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        cursor: pointer;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: rgba(255,255,255,0.08) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: rgba(255,255,255,0.15) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-left: 4px solid #FF9933 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: rgba(255,255,255,0.75) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }

    /* Fix Sidebar Hamburger Clickability Bug */
    [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg { 
        display: none !important; 
    }
    [data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapsedControl"] button {
        color: transparent !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button::before, [data-testid="stSidebarCollapsedControl"] button::before {
        content: "☰" !important;
        font-size: 1.75rem !important;
        color: #FAFAFA !important;
        display: block !important;
        line-height: 1 !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(255, 153, 51, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(19, 136, 8, 0.4) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FAFAFA !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        backdrop-filter: blur(12px) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.15) !important;
        border-color: rgba(255,255,255,0.25) !important;
    }

    /* Glassmorphism Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card, .kpi-card {
        background: rgba(18, 18, 20, 0.5) !important; 
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important; 
        border-radius: 16px !important; 
        padding: 2rem !important; 
        margin-bottom: 1.5rem !important; 
        color: #FAFAFA !important;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.6) !important;
    }
    
    .mota-kicker, .application-tracker-kicker { color: #FF9933 !important; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .page-intro h2 { color: #FAFAFA !important; font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; }
    .page-intro p { color: rgba(255,255,255,0.7) !important; }
    
    /* Form inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        background-color: rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FAFAFA !important;
        border-radius: 8px !important;
    }
    
    /* Text overrides */
    .stMarkdown p, .stMarkdown span { color: rgba(255,255,255,0.85) !important; }
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
        <div style="background: radial-gradient(circle at 10% 20%, rgba(255, 153, 51, 0.15) 0%, rgba(0,0,0,0) 60%), radial-gradient(circle at 90% 80%, rgba(19, 136, 8, 0.15) 0%, rgba(0,0,0,0) 60%), rgba(0,0,0,0.4); padding: 3.5rem 3rem; border-radius: 16px; margin-bottom: 3rem; border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="position: absolute; right: -50px; top: -50px; width: 300px; height: 300px; background: rgba(255,153,51,0.1); filter: blur(80px); border-radius: 50%;"></div>
            <div style="position: relative; z-index: 1;">
                <h1 style="margin: 0 0 1rem 0; font-size: 3rem; font-weight: 800; color: #FAFAFA; line-height: 1.1; letter-spacing: -0.03em;">Smart Scholarship<br>Audit Engine</h1>
                <p style="margin: 0; font-size: 1.15rem; color: rgba(255,255,255,0.8); max-width: 600px; line-height: 1.5; font-weight: 400;">
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
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; backdrop-filter: blur(10px);">
                <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FAFAFA;">👤</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">1. My Profile</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.5;">Ensure your demographic and academic details are up to date for precise AI matching.</p>
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
            <div style="background: rgba(255,153,51,0.08); border: 1px solid rgba(255,153,51,0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; position: relative; box-shadow: inset 0 0 0 1px rgba(255,153,51,0.15); backdrop-filter: blur(10px);">
                <div style="position: absolute; top: -10px; right: 20px; background: #FF9933; color: #09090b; font-size: 0.65rem; font-weight: 700; padding: 0.15rem 0.6rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em;">Primary Step</div>
                <div style="width: 40px; height: 40px; background: rgba(255,153,51,0.15); border: 1px solid rgba(255,153,51,0.25); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FF9933;">✨</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">2. Find Scholarships</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.5;">Discover and evaluate your eligibility against active schemes instantly.</p>
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
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; height: 100%; backdrop-filter: blur(10px);">
                <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 1rem; color: #FAFAFA;">📊</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #FAFAFA; font-size: 1.1rem; font-weight: 600;">3. Track Status</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0; line-height: 1.5;">Monitor your document audits, deficiency notices, and approval statuses.</p>
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
        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; display: flex; gap: 1.5rem; align-items: center; backdrop-filter: blur(10px);">
            <div style="width: 50px; height: 50px; background: rgba(255,255,255,0.08); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; border: 1px solid rgba(255,255,255,0.15);">🛡️</div>
            <div>
                <h4 style="margin: 0 0 0.25rem 0; color: #FAFAFA; font-size: 1rem; font-weight: 600;">Enterprise Grade Intelligence</h4>
                <p style="margin: 0; color: rgba(255,255,255,0.7); font-size: 0.85rem; line-height: 1.5;">
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

if __name__ == '__main__':
    main()
