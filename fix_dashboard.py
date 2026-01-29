
import re
import os

file_path = r"c:\Users\Ashen\OneDrive\Documents\lab-timetabling-system\backend\src\templates\admin_dashboard.html"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix Jinja Tags (remove newlines inside tags)
# Pattern: { followed by optional whitespace/newline followed by %
content = re.sub(r'\{\s*\n\s*%', '{%', content)
content = re.sub(r'%\s*\n\s*\}', '%}', content)
content = re.sub(r'\{\s*\n\s*\{', '{{', content)
content = re.sub(r'\}\s*\n\s*\}', '}}', content)

# Fix corrupted artifacts
# Based on observed output: "dY?>,?" -> "🏛️"
# "dY"'" -> "🔒"  (Note: dY"' in output might be quotes)
# I will just replace known bad strings if I can match them, or just re-insert emojis where appropriate.
# Or better, I will assume the emojis are gone/garbled and re-add them based on context context.

# Header
content = re.sub(r'<h1>.*?Admin Dashboard', '<h1>🏛️ Admin Dashboard', content)
content = re.sub(r'>.*?Change Pwd', '>🔒 Change Pwd', content)

# Tabs
content = content.replace('🗓️', '🗓️') # Might be valid or not
# If I can't match specific garbage, I'll fix the tags first, then manually fix emojis if verification fails on text.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Jinja tags.")
