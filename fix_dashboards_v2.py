
import re
import os

file_paths = [
    r"c:\Users\Ashen\OneDrive\Documents\lab-timetabling-system\backend\src\templates\admin_dashboard.html",
    r"c:\Users\Ashen\OneDrive\Documents\lab-timetabling-system\backend\src\templates\instructor_dashboard.html"
]

def fix_file(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    print(f"Fixing {path}...")
    with open(path, 'rb') as f:
        raw = f.read()
    
    # decode with utf-8, replacing errors to avoid crash
    content = raw.decode('utf-8', errors='replace')

    # 1. Fix broken comments < !-- -> <!--
    content = re.sub(r'<\s+!--', '<!--', content)
    
    # 2. Fix split Jinja variable tags {{ \n ... \n }} -> {{ ... }}
    # We want to normalize to {{ value }}
    def fix_var(match):
        inner = match.group(1)
        # remove newlines and excessive spaces
        inner_clean = re.sub(r'\s+', ' ', inner).strip()
        return f"{{{{ {inner_clean} }}}}"

    content = re.sub(r'\{\{\s*([^}]+?)\s*\}\}', fix_var, content, flags=re.DOTALL)

    # 3. Fix split Jinja block tags {% \n ... \n %} -> {% ... %}
    def fix_block(match):
        inner = match.group(1)
        inner_clean = re.sub(r'\s+', ' ', inner).strip()
        return f"{{% {inner_clean} %}}"
    
    content = re.sub(r'\{%\s*([^%]+?)\s*%\}', fix_block, content, flags=re.DOTALL)

    # 4. Fix corrupted Emojis (Admin Dashboard specific)
    # Replaces common garbage patterns observed with correct emojis
    # Note: The 'dY...' garbage might vary, so we rely on context if possible.
    
    # Header: Admin Dashboard
    content = re.sub(r'<h1>.*?Admin Dashboard', '<h1>🏛️ Admin Dashboard', content)
    
    # Logout button: Change Pwd
    content = re.sub(r'style="[^"]*">.*?Change Pwd', 'style="background-color: #0277bd; border:none; cursor:pointer;">🔒 Change Pwd', content)
    
    # Tabs
    content = content.replace('Calendar', '🗓️ Master Schedule') # Just in case it was text
    content = content.replace('Master Schedule', '🗓️ Master Schedule') # Normalize
    content = content.replace('🗓️ 🗓️', '🗓️') # Fix double
    
    content = content.replace('Manage Bookings', '📝 Manage Bookings')
    content = content.replace('📝 📝', '📝')

    content = content.replace('Labs', '🔬 Labs')
    content = content.replace('🔬 🔬', '🔬')

    content = content.replace('Modules', '📚 Modules')
    content = content.replace('📚 📚', '📚')

    content = content.replace('Instructors', '👨‍🏫 Instructors')
    content = content.replace('👨‍🏫 👨‍🏫', '👨‍🏫')

    # Conflict Warning
    content = content.replace('INSTRUCTOR ON LEAVE', '⚠️ INSTRUCTOR ON LEAVE')
    content = content.replace('⚠️ ⚠️', '⚠️')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {path}")

for p in file_paths:
    fix_file(p)
