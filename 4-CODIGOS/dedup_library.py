import re
from pathlib import Path

# Build paths relative to this script's directory
script_dir = Path(__file__).resolve().parent
repo_root = script_dir.parent
lib_path = repo_root / '2-MANUSCRITO' / 'library.bib'
out_path = repo_root / '2-MANUSCRITO' / 'library.dedup.bib'

print(f"Reading {lib_path}")
text = lib_path.read_text(encoding='utf-8')
entries = re.split(r'(?=^@)', text, flags=re.MULTILINE)

seen = set()
kept = []
duplicate_count = 0

def normalize_title(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

for e in entries:
    if not e.strip():
        continue
    m_doi = re.search(r"doi\s*=\s*\{([^}]+)\}", e, flags=re.IGNORECASE)
    if m_doi:
        key = ('doi', m_doi.group(1).strip().lower())
    else:
        m_title = re.search(r"title\s*=\s*\{([^}]+)\}", e, flags=re.IGNORECASE)
        if m_title:
            key = ('title', normalize_title(m_title.group(1)))
        else:
            key = ('text', e[:120])
    if key in seen:
        duplicate_count += 1
    else:
        seen.add(key)
        kept.append(e)

out_path.write_text('\n'.join(kept), encoding='utf-8')
print(f"Original entries: {len(entries)}")
print(f"Kept entries: {len(kept)}")
print(f"Duplicates removed: {duplicate_count}")
print(f"Wrote deduplicated file: {out_path}")
