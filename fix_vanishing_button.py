import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # We will replace the entire styling section for the hamburger buttons
    # with the universal button[kind="header"] approach that we know works perfectly.
    
    # First, let's remove the two blocks of CSS related to collapsed control
    # to avoid any duplicates.
    
    # Remove old stSidebarCollapsedControl rules
    content = re.sub(r'/\* Hamburger - sidebar CLOSED state \*/.*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\[data-testid="stSidebarCollapsedControl"\].*?\}', '', content, flags=re.DOTALL)
    
    # Remove old stSidebarCollapseButton rules
    content = re.sub(r'/\* Hamburger - sidebar OPEN state \*/.*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\[data-testid="stSidebarCollapseButton"\].*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'/\* Force collapsed control always visible with high z-index \*/', '', content)
    
    universal_hamburger = '''
    /* ─── BULLETPROOF UNIVERSAL HAMBURGER (Both Open & Closed) ─── */
    button[kind="header"] {
        position: fixed !important;
        top: 1rem !important;
        left: 1rem !important;
        z-index: 99999999 !important;
        background: rgba(20, 20, 24, 0.85) !important;
        border: 1px solid rgba(255,153,51,0.4) !important;
        border-radius: 10px !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: all !important;
    }
    button[kind="header"] svg {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    button[kind="header"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important; 
    }
    
    /* Make sure header container doesn't hide it */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        pointer-events: none !important; /* Let clicks pass through empty header area */
        z-index: 99999998 !important;
    }
    header[data-testid="stHeader"] button[kind="header"] {
        pointer-events: all !important; /* Re-enable clicks for the button */
    }
    '''

    # Inject it before </style>
    content = content.replace('</style>', universal_hamburger + '\n</style>')

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Reverted to universal button[kind='header'] styling.")

if __name__ == '__main__':
    main()
