with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add a JavaScript snippet that creates a persistent floating hamburger button
# that triggers Streamlit's native collapse button click.
# We inject this via st.markdown in inject_theme.

floating_js = '''
    /* Force collapsed control always visible with high z-index */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        position: relative !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarCollapsedControl"] button svg { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "\\2630" !important;
        font-size: 1.5rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important;
    }
'''

# Insert this CSS into the existing style block, right before </style>
content = content.replace('    /* Text */\n    .stMarkdown p, .stMarkdown span { color: rgba(255,255,255,0.85) !important; }\n    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FAFAFA !important; }\n</style>', 
    '    /* Text */\n    .stMarkdown p, .stMarkdown span { color: rgba(255,255,255,0.85) !important; }\n    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FAFAFA !important; }\n' + floating_js + '\n</style>')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
