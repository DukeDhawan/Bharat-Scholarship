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
    
    /* Breathtaking Dark Abstract Wallpaper */
    .stApp {
        background: url("https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=2070&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(9, 9, 11, 0.75);
        z-index: -1;
    }
    
    /* Glassmorphism Main Container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px !important;
        background: rgba(18, 18, 20, 0.4) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 2rem !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    
    /* Glassmorphism Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(18, 18, 20, 0.3) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    .sidebar-brand { padding: 1.5rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 1rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 50px; height: 50px; background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem; box-shadow: 0 0 20px rgba(59,130,246,0.4); }
    .sidebar-brand h2 { margin: 0; font-size: 1.1rem; color: #FAFAFA !important; font-weight: 700; letter-spacing: -0.01em; }
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.75rem; color: rgba(255,255,255,0.6) !important; font-weight: 500; }
    
    /* Hide Radio Label ("Open workspace") */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    /* Modern Navigation Tabs (replacing radio buttons) */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.3rem; padding: 0 0.5rem; }
    /* Completely hide the radio circle */
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
        background-color: rgba(255,255,255,0.05) !important;
    }
    /* Active Tab */
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: rgba(59,130,246,0.15) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    /* Tab Text */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: rgba(255,255,255,0.7) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }

    /* Fix Sidebar Hamburger (ABSOLUTELY NO ARROWS) */
    [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] *, [data-testid="stSidebarCollapsedControl"] * { 
        display: none !important; opacity: 0 !important; width: 0 !important; height: 0 !important; 
    }
    [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"] {
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        width: 48px !important;
        height: 48px !important;
        position: relative !important;
    }
    [data-testid="stSidebarCollapseButton"]::before, [data-testid="stSidebarCollapsedControl"]::before {
        content: "☰" !important;
        font-size: 1.75rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37,99,235,0.6) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #FAFAFA !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        backdrop-filter: blur(10px) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
    }

    /* Glassmorphism Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card, .kpi-card {
        background: rgba(18, 18, 20, 0.4) !important; 
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255,255,255,0.08) !important; 
        border-radius: 16px !important; 
        padding: 2rem !important; 
        margin-bottom: 1.5rem !important; 
        color: #FAFAFA !important;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5) !important;
    }
    
    .mota-kicker, .application-tracker-kicker { color: #60A5FA !important; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
    .page-intro h2 { color: #FAFAFA !important; font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; }
    .page-intro p { color: rgba(255,255,255,0.6) !important; }
    
    /* Form inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        background-color: rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #FAFAFA !important;
        border-radius: 8px !important;
    }
    
    /* Text overrides */
    .stMarkdown p, .stMarkdown span { color: rgba(255,255,255,0.8) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FAFAFA !important; }
</style>
        """,
        unsafe_allow_html=True,
    )'''

    content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_theme, content, flags=re.DOTALL)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
