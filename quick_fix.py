with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Make overlay much lighter so wallpaper looks vibrant like before
content = content.replace(
    'background: rgba(5,5,7,0.68);',
    'background: rgba(5,5,7,0.35);'
)
content = content.replace(
    'background: rgba(5, 5, 7, 0.68);',
    'background: rgba(5, 5, 7, 0.35);'
)

# Fix 2: The collapsed control (closed sidebar button) needs to be visible on screen
# When sidebar is closed, the button floats over the main content area.
# The button is dark (#333) which blends with wallpaper - make it white/light
content = content.replace(
    '''    /* Hamburger - sidebar CLOSED state */
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
    }''',
    '''    /* Hamburger - sidebar CLOSED state */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        position: relative !important;
        background: rgba(10,10,14,0.7) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        width: 2.5rem !important;
        height: 2.5rem !important;
        backdrop-filter: blur(10px) !important;
    }
    [data-testid="stSidebarCollapsedControl"] button svg { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] button::after {
        content: "\\2630" !important;
        font-size: 1.6rem !important;
        color: #FAFAFA !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        pointer-events: none !important;
    }'''
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
