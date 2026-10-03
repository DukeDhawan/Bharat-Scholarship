import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # The buggy string contains label_visibility before the list
    bad_code = """        selected_navigation = st.radio(
            "Open workspace",
            label_visibility="collapsed",
            [
                "Dashboard",
                "My Profile",
                "My Applications",
                "AI Policy Assistant",
                "Internal Audit",
            ],
            label_visibility="collapsed",
            key="workspace_navigation",
            on_change=sync_workspace_navigation,
        )"""

    good_code = """        selected_navigation = st.radio(
            "Open workspace",
            [
                "Dashboard",
                "My Profile",
                "My Applications",
                "AI Policy Assistant",
                "Internal Audit",
            ],
            label_visibility="collapsed",
            key="workspace_navigation",
            on_change=sync_workspace_navigation,
        )"""

    if bad_code in content:
        content = content.replace(bad_code, good_code)
    else:
        # Fallback regex if formatting slightly differs
        content = re.sub(
            r'selected_navigation = st\.radio\(\s*"Open workspace",\s*label_visibility="collapsed",\s*\[(.*?)\](,\s*label_visibility="collapsed")?,\s*key="workspace_navigation",\s*on_change=sync_workspace_navigation,\s*\)',
            r'selected_navigation = st.radio(\n            "Open workspace",\n            [\1],\n            label_visibility="collapsed",\n            key="workspace_navigation",\n            on_change=sync_workspace_navigation,\n        )',
            content,
            flags=re.DOTALL
        )

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        print("Fixed SyntaxError")

if __name__ == '__main__':
    main()
