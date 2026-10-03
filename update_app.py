import re

def main():
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove SIH references
        content = content.replace("SIH26239", "")
        content = content.replace("SIH Problem Statement  - ", "")
        content = content.replace("SIH Problem Statement - ", "")
        content = content.replace("SIH Problem Statement ", "")
        content = content.replace(" (SIH)", "")
        content = content.replace(" SIH ", " ")
        content = content.replace("SIH ", "")
        content = content.replace("_SIH26239", "")
        content = content.replace("  Local operations console", "Local operations console")
        content = content.replace("· Local operations console", "Local operations console")

        # Fix the CSS issues
        
        # 1. We want to ensure text in the Hero banner isn't being overridden. 
        # Remove the global !important from .stMarkdown headers
        content = content.replace(
            ".stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {\n        color: #0F172A !important;\n    }", 
            ".stMarkdown h2, .stMarkdown h3 {\n        color: #0F172A;\n    }"
        )
        content = content.replace(
            ".stMarkdown p {\n        color: #334155 !important;\n    }",
            ".stMarkdown p {\n        color: inherit;\n    }"
        )
        
        # 2. To fix the sidebar toggle arrow -> Hamburger:
        # We need to inject CSS for [data-testid="stSidebarCollapseButton"] and [data-testid="stSidebarCollapsedControl"]
        hamburger_css = '''
    /* Change Sidebar arrow to Hamburger menu */
    [data-testid="stSidebarCollapseButton"] svg { display: none !important; }
    [data-testid="stSidebarCollapseButton"]::before {
        content: "☰";
        font-size: 1.5rem;
        color: #64748B;
        display: block;
        line-height: 1;
    }
    [data-testid="stSidebarCollapsedControl"] svg { display: none !important; }
    [data-testid="stSidebarCollapsedControl"]::before {
        content: "☰";
        font-size: 1.5rem;
        color: #64748B;
        display: block;
        line-height: 1;
    }
'''
        # Insert hamburger CSS into the inject_theme string right before </style>
        content = content.replace("</style>", hamburger_css + "\n</style>")

        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Updated app.py successfully.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
