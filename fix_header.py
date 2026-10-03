with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The root cause: header height:0 also hides the collapsed sidebar button.
# Fix: make header fully transparent (not height 0), so button stays clickable.
content = content.replace(
    '''    /* Remove black header bar */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }''',
    '''    /* Make header transparent - DO NOT set height:0 or the sidebar button disappears */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }
    /* Hide only the toolbar items inside header (deploy button etc), keep sidebar toggle */
    header[data-testid="stHeader"] [data-testid="stToolbar"] {
        display: none !important;
    }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }'''
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
