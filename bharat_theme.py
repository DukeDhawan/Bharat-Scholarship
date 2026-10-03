import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements for Ministry/Tricolor themes
    content = content.replace("Ministry of Tribal Affairs", "Government of India")
    content = content.replace("MINISTRY OF TRIBAL AFFAIRS", "GOVERNMENT OF INDIA")
    content = content.replace("MoTA", "Bharat")
    content = content.replace("mota", "bharat")
    content = content.replace("MOTA", "BHARAT")
    
    # I should also update the CSS sidebar-brand-mark which was 'MoTA' to something like '🇮🇳' or 'BHARAT'
    # Wait, the code has: <div class="sidebar-brand-mark">MoTA</div> 
    # That will become <div class="sidebar-brand-mark">Bharat</div>, which is fine, 
    # but the text is slightly long for a 50x50 icon box. I'll replace it with "IN" or "🇮🇳" or "GOI"
    content = content.replace('<div class="sidebar-brand-mark">Bharat</div>', '<div class="sidebar-brand-mark">IN</div>')

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Successfully replaced MoTA and Ministry of Tribal Affairs with Bharat/India theme!")

if __name__ == '__main__':
    main()
