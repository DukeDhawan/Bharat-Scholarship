import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Hide Open Workspace label natively in Streamlit
    content = content.replace(
        'selected_navigation = st.radio(\n            "Open workspace",',
        'selected_navigation = st.radio(\n            "Open workspace",\n            label_visibility="collapsed",'
    )

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
        background: rgba(5, 5, 7, 0.7);
        z-index: -1;
    }
    
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
    
    /* Hide Radio Label Natively via CSS as fallback */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    /* Modern Navigation Tabs (FULL WIDTH) */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { 
        gap: 0.3rem; 
        padding: 0 0.5rem; 
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
    }
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
        width: 100% !important; /* Force full width */
        box-sizing: border-box !important;
        margin-bottom: 0.25rem !important;
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
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }

    /* Fix Sidebar Hamburger (BULLETPROOF NO ARROWS) */
    [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"] {
        position: relative !important;
    }
    [data-testid="stSidebarCollapseButton"] svg, [data-testid="stSidebarCollapsedControl"] svg { 
        visibility: hidden !important; 
        opacity: 0 !important;
        display: none !important;
    }
    [data-testid="stSidebarCollapseButton"]::before, [data-testid="stSidebarCollapsedControl"]::before {
        content: "☰" !important;
        font-size: 1.75rem !important;
        color: #FAFAFA !important;
        visibility: visible !important;
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; /* Let clicks pass to the button */
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

    content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_theme, content, flags=re.DOTALL)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
