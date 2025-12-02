from pathlib import Path
import re
md_path = Path(r'c:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/revisao-sistematica/2-MANUSCRITO/Review_Article_Draft.md')
bib_path = Path(r'c:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/revisao-sistematica/2-MANUSCRITO/referencias.bib')
md = md_path.read_text(encoding='utf8')
bib = bib_path.read_text(encoding='utf8')
# find all citation groups inside [@...]
keys = set()
for m in re.finditer(r'\[@([^\]]+)\]', md):
    inner = m.group(1)
    parts = re.split(r'[;,]\s*|\s+and\s+|\s*&\s*', inner)
    for p in parts:
        p = p.strip()
        if p.startswith('@'):
            p = p[1:]
        # remove page locators like @Smith2019, p.34
        p = re.sub(r'\s+.*$', '', p)
        if p:
            keys.add(p)
# find bib keys
bib_keys = set(re.findall(r'@\w+\{\s*([^,\n\r]+)', bib))
missing = sorted([k for k in keys if k and k not in bib_keys])
print('CITATION KEYS IN MANUSCRIPT:', len(keys))
print(sorted(keys))
print('\nBIB KEYS:', len(bib_keys))
print(sorted(list(bib_keys))[:40])
print('\nMISSING KEYS (used in manuscript but not in referencias.bib):')
if missing:
    for k in missing:
        print('-', k)
else:
    print('None')
