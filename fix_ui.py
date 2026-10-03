import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. FIX INJECT THEME (Safe and Professional)
new_theme = '''def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
    }
    
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
    .sidebar-brand p { margin: 0.35rem 0 0 0; font-size: 0.8rem; color: #64748B !important; font-weight: 500; }
    
    /* Modern Navigation Links (safely styling radio buttons) */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 0.25rem; padding: 0 0.5rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        border: none !important;
        cursor: pointer;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: #EFF6FF !important;
    }
    /* Enforce Dark Text Visibility */
    [data-testid="stSidebar"] [data-testid="stRadio"] label p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label span,
    [data-testid="stSidebar"] [data-testid="stRadio"] label div {
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
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
    .stTabs [data-baseweb="tab"] { padding-top: 1rem; padding-bottom: 1rem; color: #64748B !important; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #1E40AF !important; font-weight: 600; border-bottom-color: #1E40AF !important; }

    /* Custom Cards */
    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card {
        background: #ffffff !important; border: 1px solid #F1F5F9 !important; border-radius: 16px !important; padding: 2rem !important; margin-bottom: 1.5rem !important; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.02) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .mota-kicker, .application-tracker-kicker { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #3B82F6 !important; margin-bottom: 0.75rem; }
    .page-intro { border-bottom: 1px solid #F1F5F9; padding-bottom: 1.5rem; margin-bottom: 2rem; }
    .page-intro h2 { color: #0F172A !important; font-size: 2rem; margin-bottom: 0.5rem; font-weight: 700; letter-spacing: -0.02em; }
    .page-intro p { color: #64748B !important; font-size: 1.1rem; margin: 0; }

    /* Forms & Inputs */
    div[data-baseweb="select"] > div, input, div[data-baseweb="textarea"] > div {
        border-radius: 8px !important;
        border-color: #CBD5E1 !important;
        background-color: #ffffff !important;
        color: #0F172A !important;
    }
    
    /* Metrics */
    .kpi-card { background: #ffffff !important; border-radius: 12px; padding: 1.5rem; border: 1px solid #F1F5F9 !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .kpi-label { font-size: 0.85rem; color: #64748B !important; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #0F172A !important; margin: 0.5rem 0; letter-spacing: -0.02em; }
    
    /* General Text overrides to fix hidden text */
    p, span, h1, h2, h3, h4, h5, h6, li, label, div {
        /* We DO NOT force color on everything to avoid breaking tooltips/inputs, 
           but we ensure basic typography elements are visible if they fall back. */
    }
    
    /* Specifically force readable text on markdown paragraphs */
    .stMarkdown p {
        color: #334155 !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #0F172A !important;
    }

    /* Badges */
    .match-badge { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 1rem; }
    .match-eligible { background: #DCFCE7 !important; color: #166534 !important; border: 1px solid #BBF7D0 !important; }
    .match-ineligible { background: #FEE2E2 !important; color: #991B1B !important; border: 1px solid #FECACA !important; }
    
    /* Workflow Tracker */
    .workflow-tracker { display: flex; align-items: center; margin: 2rem 0; padding: 1rem 0; }
    .workflow-step { display: flex; flex-direction: column; align-items: center; position: relative; z-index: 1; flex: 1; }
    .workflow-marker { width: 36px; height: 36px; border-radius: 50%; background: #ffffff !important; border: 2px solid #CBD5E1 !important; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #64748B !important; margin-bottom: 0.75rem; transition: all 0.2s; }
    .workflow-step.complete .workflow-marker { background: #3B82F6 !important; border-color: #3B82F6 !important; color: white !important; }
    .workflow-step.current .workflow-marker { border-color: #3B82F6 !important; color: #3B82F6 !important; box-shadow: 0 0 0 4px rgba(59,130,246,0.1) !important; }
    .workflow-label { font-size: 0.85rem; font-weight: 500; color: #64748B !important; text-align: center; }
    .workflow-step.current .workflow-label { color: #1E40AF !important; font-weight: 700; }
    .workflow-line { height: 2px; background: #E2E8F0 !important; flex: 2; margin-top: -30px; position: relative; z-index: 0; }
    .workflow-line.filled { background: #3B82F6 !important; }
</style>
        """,
        unsafe_allow_html=True,
    )'''

content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_theme, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
