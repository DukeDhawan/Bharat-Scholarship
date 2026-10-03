import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. NEW INJECT THEME (Very polished SaaS look)
new_theme = '''def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC !important;
    }
    
    /* Hide default Streamlit chrome for a cleaner app look */
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Layout adjustments */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1100px !important;
    }
    
    /* Beautiful Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #F1F5F9 !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important;
    }
    .sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid #F1F5F9; margin-bottom: 1.5rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 56px; height: 56px; background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 10px rgba(37,99,235,0.2); }
    .sidebar-brand h2 { margin: 0; font-size: 1.15rem; color: #0F172A !important; font-weight: 700; letter-spacing: -0.02em; }
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.8rem; color: #64748B; font-weight: 500; }
    
    /* Modern Navigation Links (converting radio buttons) */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.25rem; padding: 0 0.5rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.65rem 1rem !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        border: none !important;
        cursor: pointer;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: #F8FAFC !important;
    }
    /* Hide the radio circle */
    [data-testid="stSidebar"] [data-testid="stRadio"] label div:first-child { display: none !important; }
    /* Checked state */
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: #EFF6FF !important;
    }
    /* Text styling for nav links */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: #1D4ED8 !important;
        font-weight: 600 !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(37,99,235,0.2) !important;
        transition: transform 0.1s, box-shadow 0.1s !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 8px -1px rgba(37,99,235,0.3) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: white !important;
        border: 1px solid #CBD5E1 !important;
        color: #334155 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #94A3B8 !important;
        background: #F8FAFC !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] { padding-top: 1rem; padding-bottom: 1rem; color: #64748B; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #1E40AF !important; font-weight: 600; border-bottom-color: #1E40AF !important; }

    /* Custom Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card {
        background: #ffffff; border: 1px solid #F1F5F9; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .scholarship-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.04); }
    
    .mota-kicker, .application-tracker-kicker { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3B82F6; margin-bottom: 0.75rem; }
    .page-intro { border-bottom: 1px solid #F1F5F9; padding-bottom: 1.5rem; margin-bottom: 2rem; }
    .page-intro h2 { color: #0F172A !important; font-size: 2rem; margin-bottom: 0.5rem; font-weight: 700; letter-spacing: -0.02em; }
    .page-intro p { color: #64748B; font-size: 1.1rem; margin: 0; }

    /* Forms & Inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        border-radius: 8px !important;
        border-color: #CBD5E1 !important;
    }
    
    /* Metrics */
    .kpi-card { background: #ffffff; border-radius: 12px; padding: 1.5rem; border: 1px solid #F1F5F9; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .kpi-label { font-size: 0.85rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #0F172A; margin: 0.5rem 0; letter-spacing: -0.02em; }
    
    /* Badges */
    .match-badge { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 1rem; }
    .match-eligible { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
    .match-ineligible { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
    
    /* Workflow Tracker */
    .workflow-tracker { display: flex; align-items: center; margin: 2rem 0; padding: 1rem 0; }
    .workflow-step { display: flex; flex-direction: column; align-items: center; position: relative; z-index: 1; flex: 1; }
    .workflow-marker { width: 36px; height: 36px; border-radius: 50%; background: #ffffff; border: 2px solid #CBD5E1; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #64748B; margin-bottom: 0.75rem; transition: all 0.2s; }
    .workflow-step.complete .workflow-marker { background: #3B82F6; border-color: #3B82F6; color: white; }
    .workflow-step.current .workflow-marker { border-color: #3B82F6; color: #3B82F6; box-shadow: 0 0 0 4px rgba(59,130,246,0.1); }
    .workflow-label { font-size: 0.85rem; font-weight: 500; color: #64748B; text-align: center; }
    .workflow-step.current .workflow-label { color: #1E40AF; font-weight: 700; }
    .workflow-line { height: 2px; background: #E2E8F0; flex: 2; margin-top: -30px; position: relative; z-index: 0; }
    .workflow-line.filled { background: #3B82F6; }
</style>
        """,
        unsafe_allow_html=True,
    )
'''

content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_theme, content, flags=re.DOTALL)


# 2. NEW DASHBOARD (Very Aesthetic)
new_dashboard = '''def render_dashboard(applicants: list[ApplicantProfile], results: list[CompositeEvaluationResult]) -> None:
    profile = st.session_state.get("user_profile", {})
    missing_fields = [field for field in PROFILE_REQUIRED_FIELDS if not profile.get(field)]
    profile_complete = bool(st.session_state.get("profile_complete", False)) or profile_is_complete(profile)

    st.markdown(
        """
        <div style="background: url('https://www.transparenttextures.com/patterns/cubes.png'), linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); padding: 4rem 3rem; border-radius: 20px; margin-bottom: 3rem; color: white; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50px; right: -20px; opacity: 0.08; font-size: 300px; transform: rotate(-15deg); user-select: none;">🇮🇳</div>
            <div style="position: relative; z-index: 1;">
                <div style="display: inline-block; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.1em; color: #E0E7FF; margin-bottom: 1.5rem; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.2);">
                    Ministry of Tribal Affairs
                </div>
                <h1 style="margin: 0 0 1.25rem 0; font-size: 3.25rem; font-weight: 800; color: white; line-height: 1.1; letter-spacing: -0.03em;">Smart Scholarship<br>Audit Engine</h1>
                <p style="margin: 0; font-size: 1.25rem; color: #93C5FD; max-width: 600px; line-height: 1.6; font-weight: 400;">
                    A unified, AI-driven platform for eligibility matching, document compliance, and rapid disbursements.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3 style='margin-bottom: 1.5rem; font-size: 1.5rem; color: #0F172A; font-weight: 700; letter-spacing: -0.02em;'>Quick Actions</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; margin-bottom: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); height: 100%; transition: all 0.2s ease;">
                <div style="width: 48px; height: 48px; background: #F1F5F9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 1.5rem; color: #475569;">👤</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.25rem; font-weight: 700;">1. My Profile</h3>
                <p style="color: #64748B; font-size: 0.95rem; margin: 0; line-height: 1.6;">Ensure your demographic and academic details are up to date for precise AI matching.</p>
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
            <div style="background: white; border: 2px solid #3B82F6; border-radius: 16px; padding: 2rem; margin-bottom: 1rem; box-shadow: 0 10px 15px -3px rgba(59,130,246,0.1); height: 100%; position: relative;">
                <div style="position: absolute; top: -12px; right: 24px; background: #3B82F6; color: white; font-size: 0.7rem; font-weight: 700; padding: 0.25rem 0.75rem; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em; box-shadow: 0 2px 4px rgba(59,130,246,0.3);">Primary Step</div>
                <div style="width: 48px; height: 48px; background: #EFF6FF; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 1.5rem; color: #3B82F6;">✨</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.25rem; font-weight: 700;">2. Find Scholarships</h3>
                <p style="color: #64748B; font-size: 0.95rem; margin: 0; line-height: 1.6;">Discover and evaluate your eligibility against active schemes instantly.</p>
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
            <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; margin-bottom: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); height: 100%; transition: all 0.2s ease;">
                <div style="width: 48px; height: 48px; background: #F1F5F9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 1.5rem; color: #475569;">📊</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.25rem; font-weight: 700;">3. Track Status</h3>
                <p style="color: #64748B; font-size: 0.95rem; margin: 0; line-height: 1.6;">Monitor your document audits, deficiency notices, and approval statuses.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("View Applications", use_container_width=True, key="dashboard_track_btn"):
            st.session_state["pending_workspace_view"] = "My Applications"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; display: flex; gap: 1.5rem; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);">
            <div style="width: 64px; height: 64px; background: #F8FAFC; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; flex-shrink: 0; border: 4px solid #F1F5F9;">🛡️</div>
            <div>
                <h4 style="margin: 0 0 0.5rem 0; color: #0F172A; font-size: 1.1rem; font-weight: 700;">Enterprise Grade Intelligence</h4>
                <p style="margin: 0; color: #64748B; font-size: 0.95rem; line-height: 1.6;">
                    The Audit Engine automatically evaluates strict multi-constraint MoTA policy rules for Pre-Matric, Post-Matric, Higher Education, National Fellowship, and NOS schemes. It features real-time demographic validation, academic scoring checks, and risk flagging based on historical data.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_saved_scholarship_results'''

content = re.sub(r'def render_dashboard\(.*?\).*?def render_saved_scholarship_results', new_dashboard, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
