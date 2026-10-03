import re
import sys

def main():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        new_theme = '''def inject_theme() -> None:
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
    }
    
    /* Semantic UI Classes for Smart Audit Engine */
    .mota-hero { padding: 2.5rem 2rem; background: linear-gradient(135deg, var(--primary-color) 0%, #1A4B8C 100%); border-radius: 12px; color: white; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); position: relative; overflow: hidden; }
    .mota-hero::before { content: "🏛️"; position: absolute; right: -20px; top: -30px; font-size: 150px; opacity: 0.1; }
    .mota-hero h1 { color: white !important; margin-top: 0; margin-bottom: 0.5rem; font-size: 2.25rem; font-weight: 700; position: relative; z-index: 1; }
    .mota-hero p { color: rgba(255,255,255,0.9) !important; font-size: 1.1rem; max-width: 600px; position: relative; z-index: 1; margin-bottom: 0; }
    .mota-emblem { font-size: 2.5rem; }

    .page-intro { border-bottom: 1px solid var(--border-color, rgba(128,128,128,0.2)); padding-bottom: 1rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-end; }
    .page-intro h2 { color: var(--text-color) !important; font-size: 1.8rem; margin-bottom: 0.25rem; font-weight: 700; }
    .page-intro p { color: var(--text-color); opacity: 0.7; margin: 0; }

    .profile-card, .scholarship-card, .anomaly-card, .application-tracker-card {
        background: var(--secondary-background-color); border: 1px solid var(--border-color, rgba(128,128,128,0.2)); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .mota-kicker, .application-tracker-kicker { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--primary-color); margin-bottom: 0.5rem; }
    .document-name { font-weight: 600; color: var(--text-color); }
    .required-marker { color: #dc2626; margin-left: 0.25rem; }
    .required-note { font-size: 0.8rem; color: #dc2626; margin-top: -0.5rem; display: block; }

    .dossier-metric { margin-bottom: 1rem; }
    .dossier-metric-label { font-size: 0.8rem; color: var(--text-color); opacity: 0.7; margin-bottom: 0.15rem; }
    .dossier-metric-value { font-size: 1.05rem; font-weight: 600; color: var(--text-color); }
    .document-audit-kpi { margin-bottom: 0.5rem; }

    .kpi-card { background: var(--secondary-background-color); border-radius: 10px; padding: 1.25rem; border: 1px solid var(--border-color, rgba(128,128,128,0.2)); text-align: center; }
    .kpi-label { font-size: 0.85rem; color: var(--text-color); opacity: 0.7; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: var(--primary-color); margin: 0.5rem 0; }
    .kpi-hint { font-size: 0.75rem; color: var(--text-color); opacity: 0.5; }

    .match-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 1rem; }
    .match-eligible { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .match-ineligible { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    .rule-fail { color: #dc2626; font-size: 0.85rem; margin-top: 0.25rem; }
    .failed-gates { background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 4px; margin-top: 1rem; }

    .status-pill { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
    .qr-status { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .qr-status-verified { background: #dcfce7; color: #166534; }
    .qr-status-invalid { background: #fee2e2; color: #991b1b; }

    .workflow-tracker { display: flex; align-items: center; margin: 2rem 0; padding: 1rem 0; border-bottom: 1px solid var(--border-color, rgba(128,128,128,0.2)); }
    .workflow-step { display: flex; flex-direction: column; align-items: center; position: relative; z-index: 1; flex: 1; }
    .workflow-marker { width: 32px; height: 32px; border-radius: 50%; background: var(--secondary-background-color); border: 2px solid #cbd5e1; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #64748b; margin-bottom: 0.5rem; transition: all 0.2s; }
    .workflow-step.complete .workflow-marker { background: var(--primary-color); border-color: var(--primary-color); color: white; }
    .workflow-step.current .workflow-marker { border-color: var(--primary-color); color: var(--primary-color); box-shadow: 0 0 0 4px rgba(26,75,140,0.1); }
    .workflow-label { font-size: 0.8rem; font-weight: 500; color: #64748b; text-align: center; }
    .workflow-step.complete .workflow-label { color: var(--text-color); }
    .workflow-step.current .workflow-label { color: var(--primary-color); font-weight: 700; }
    .workflow-line { height: 2px; background: #cbd5e1; flex: 2; margin-top: -24px; position: relative; z-index: 0; }
    .workflow-line.filled { background: var(--primary-color); }

    .sidebar-brand { padding: 1rem 0 1.5rem; border-bottom: 1px solid var(--border-color, rgba(128,128,128,0.2)); margin-bottom: 1.5rem; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .sidebar-brand-mark { width: 48px; height: 48px; background: var(--primary-color); color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.25rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(26,75,140,0.2); }
    .sidebar-brand h2 { margin: 0; font-size: 1.2rem; color: var(--text-color) !important; font-weight: 700; }
    .sidebar-brand p { margin: 0.25rem 0 0 0; font-size: 0.85rem; color: var(--text-color); opacity: 0.7; }
    
    .sidebar-status { border-top: 1px solid var(--border-color, rgba(128,128,128,0.2)); margin-top: 1.5rem; padding-top: 1.5rem; font-size: 0.8rem; color: var(--text-color); opacity: 0.7; text-align: center; }
</style>
        """,
        unsafe_allow_html=True,
    )'''

        content = re.sub(r'def inject_theme\(\) -> None:.*?unsafe_allow_html=True,\n    \)', new_theme, content, flags=re.DOTALL)

        main_clean = '''def main() -> None:
    st.set_page_config(
        page_title="MoTA Scholarship Verification | SIH26239",
        page_icon="🇮🇳",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
        <style>
        .backend-banner-box {
            background-color: var(--secondary-background-color) !important;
            padding: 18px 24px !important;
            border-radius: 10px !important;
            margin-bottom: 24px !important;
            border-left: 6px solid var(--primary-color) !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            border: 1px solid var(--border-color, rgba(128,128,128,0.2));
        }
        .backend-banner-title {
            color: var(--text-color) !important;
            margin: 0 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
        }
        .backend-banner-sub {
            color: var(--primary-color) !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 1.2px !important;
            text-transform: uppercase !important;
            display: block !important;
            margin-bottom: 4px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    inject_theme()'''

        content = re.sub(r'def main\(\) -> None:.*?inject_theme\(\)', main_clean, content, flags=re.DOTALL)

        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully updated app.py styling!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
