import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match the rogue CSS blocks scattered in the file
    rogue_pattern = r'\s*/\* Change Sidebar arrow to Hamburger menu \*/.*?\[data-testid="stSidebarCollapsedControl"\]::before \{.*?line-height: 1;\s*\}'

    # Remove all instances
    content = re.sub(rogue_pattern, '', content, flags=re.DOTALL)
    
    # Let's also verify that my correct CSS for the collapsed control in inject_theme is perfectly positioned.
    # We want it to be z-index: 999999 so it floats above everything.
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Purged all rogue CSS blocks.")

if __name__ == '__main__':
    main()
