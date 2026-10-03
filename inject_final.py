with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_css = '''def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Remove black header bar */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }

    /* Full-screen India tricolor wallpaper */
    .stApp {
        background:
            radial-gradient(circle at 10% 30%, rgba(255,153,51,0.22), transparent 40%),
            radial-gradient(circle at 90% 70%, rgba(19,136,8,0.22), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(0,0,128,0.28), transparent 50%),
            url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
        min-height: 100vh !important;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(5,5,7,0.68);
        z-index: 0;
        pointer-events: none;
    }

    /* Glassmorphism content panel */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px !important;
        background: rgba(18,18,20,0.5) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-top: 1px solid rgba(255,153,51,0.25) !important;
        border-bottom: 1px solid rgba(19,136,8,0.25) !important;
        margin-top: 1rem !important;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6) !important;
        position: relative !important;
        z-index: 1 !important;
    }

    /* Glassmorphism sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(10,10,14,0.55) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
    }
    .sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 1rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 50px; height: 50px; background: linear-gradient(135deg, #FF9933 0%, #138808 100%); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.4rem; margin-bottom: 1rem; box-shadow: 0 0 20px rgba(255,153,51,0.25); }
    .sidebar-brand h2 { margin: 0; font-size: 1.1rem; color: #FAFAFA !important; font-weight: 700; }
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.7) !important; }

    /* Hide radio label */
    div[data-testid="stWidgetLabel"], div[data-testid="stRadio"] > label { display: none !important; }

    /* Full-width navigation tabs */
    div[data-testid="stRadio"] { width: 100% !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.25rem !important;
        padding: 0 0.5rem !important;
    }
    div[data-testid="stRadio"] label {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] label > div:first-child { display: none !important; }
    div[data-testid="stRadio"] label:hover { background-color: rgba(255,255,255,0.08) !important; }
    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] label:has(input:checked) {
        background-color: rgba(255,153,51,0.12) !important;
        border: 1px solid rgba(255,153,51,0.35) !important;
        border-left: 3px solid #FF9933 !important;
    }
    div[data-testid="stRadio"] label p { color: rgba(255,255,255,0.7) !important; font-weight: 500 !important; font-size: 0.95rem !important; margin: 0 !important; }
    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label:has(input:checked) p { color: #FAFAFA !important; font-weight: 600 !important; }

    /* Hamburger - sidebar OPEN state */
    [data-testid="stSidebarCollapseButton"] button {
        position: relative !important; background: transparent !important; border: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button svg { display: none !important; }
    [data-testid="stSidebarCollapseButton"] button::after {
        content: "\\2630" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important;
    }

    /* Hamburger - sidebar CLOSED state */
    [data-testid="stSidebarCollapsedControl"] button {
        position: relative !important; background: transparent !important; border: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] button svg { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "\\2630" !important;
        font-size: 1.6rem !important;
        color: #333333 !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%) !important;
        border: none !important; color: white !important; border-radius: 8px !important;
        font-weight: 600 !important; box-shadow: 0 4px 15px rgba(255,153,51,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FAFAFA !important; border-radius: 8px !important; font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover { background: rgba(255,255,255,0.15) !important; }

    /* Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card, .kpi-card {
        background: rgba(18,18,20,0.5) !important; backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 16px !important;
        padding: 2rem !important; margin-bottom: 1.5rem !important; color: #FAFAFA !important;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.6) !important;
    }
    .mota-kicker, .bharat-kicker, .application-tracker-kicker { color: #FF9933 !important; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .page-intro h2 { color: #FAFAFA !important; font-size: 2rem; font-weight: 700; }
    .page-intro p { color: rgba(255,255,255,0.7) !important; }

    /* Form inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        background-color: rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FAFAFA !important; border-radius: 8px !important;
    }

    /* Text */
    .stMarkdown p, .stMarkdown span { color: rgba(255,255,255,0.85) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FAFAFA !important; }
</style>
        """,
        unsafe_allow_html=True,
    )'''

import re
content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_css, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
