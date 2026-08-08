import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Lowercase ONLY the keys in I18N_DICT_LOWER
content = re.sub(
    r'(I18N_DICT_LOWER\[")([^"]+)("\])', 
    lambda m: m.group(1) + m.group(2).lower() + m.group(3), 
    content
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
