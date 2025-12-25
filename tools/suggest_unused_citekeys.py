import argparse
import re
from pathlib import Path

MANUSCRIPT = Path(
    r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\2-MANUSCRITO\Review_Article_Draft.md"
)
BIBS = [
    Path(
        r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\2-MANUSCRITO\referencias.bib"
    ),
    Path(
        r"C:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\2-MANUSCRITO\library.bib"
    ),
]


def load_bib_keys_and_text() -> tuple[set[str], str]:
    key_pat = re.compile(r"^\s*@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
    all_text_parts: list[str] = []
    keys: set[str] = set()

    for bib in BIBS:
        t = bib.read_text(encoding="utf-8", errors="ignore")
        all_text_parts.append(t)
        keys.update(key_pat.findall(t))

    return keys, "\n".join(all_text_parts)


def load_used_keys(bib_keys: set[str]) -> set[str]:
    txt = MANUSCRIPT.read_text(encoding="utf-8")
    # Extract @Key in both narrative and bracket contexts, then filter to those that exist in bib
    key_pat = re.compile(r"@([A-Za-z][A-Za-z0-9_:\-]*)")
    found = set(key_pat.findall(txt))
    return {k for k in found if k in bib_keys}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="palavras-chave para buscar no .bib (case-insensitive)")
    ap.add_argument("--limit", type=int, default=25)
    args = ap.parse_args()

    bib_keys, bib_text = load_bib_keys_and_text()
    used = load_used_keys(bib_keys)

    # Find entries that contain all query tokens (very simple AND search)
    tokens = [t for t in re.split(r"\s+", args.query.strip()) if t]
    if not tokens:
        return 0

    # Split into entries to allow returning citekeys
    entries = re.split(r"\n(?=\s*@\w+\s*\{)", bib_text)
    key_pat = re.compile(r"^\s*@\w+\s*\{\s*([^,\s]+)", re.MULTILINE)

    matches: list[str] = []
    for ent in entries:
        low = ent.lower()
        if all(tok.lower() in low for tok in tokens):
            m = key_pat.search(ent)
            if not m:
                continue
            k = m.group(1)
            if k in used:
                continue
            matches.append(k)
            if len(matches) >= args.limit:
                break

    for k in matches:
        print(k)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
