from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_citekeys_from_pandoc_markdown(text: str) -> set[str]:
    # Pandoc cite syntax includes @key in multiple forms: @key, [@key], [-@key]
    # We capture "key" and ignore email addresses because of the @.
    # This regex matches @ at word boundary-like positions.
    return set(re.findall(r"(?<![\w.-])@([A-Za-z0-9_:\\-]+)", text))


def extract_bibtex_keys(text: str) -> set[str]:
    # Simple BibTeX key extraction: @type{key,
    return set(re.findall(r"^@\w+\{([^,\s]+)", text, flags=re.M))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Verifica citekeys no manuscrito vs entradas .bib")
    parser.add_argument(
        "--manuscript",
        type=Path,
        default=repo_root / "2-MANUSCRITO" / "Review_Article_Draft.md",
        help="Caminho para o manuscrito .md (default: 2-MANUSCRITO/Review_Article_Draft.md)",
    )
    args = parser.parse_args()

    manuscript: Path = args.manuscript
    bib_files = [
        repo_root / "2-MANUSCRITO" / "referencias.bib",
        repo_root / "2-MANUSCRITO" / "library.bib",
    ]

    md = manuscript.read_text(encoding="utf-8")
    used_keys = extract_citekeys_from_pandoc_markdown(md)

    bib_keys: set[str] = set()
    existing_bibs = []
    for bib_path in bib_files:
        if bib_path.exists():
            existing_bibs.append(bib_path)
            bib_keys |= extract_bibtex_keys(bib_path.read_text(encoding="utf-8"))

    missing = sorted(k for k in used_keys if k not in bib_keys)

    placeholder_used = sorted(k for k in used_keys if re.fullmatch(r"Ref\d+", k))

    print(f"Manuscrito: {manuscript}")
    print(f"Bib(s) lidos: {', '.join(str(p) for p in existing_bibs) if existing_bibs else '(nenhum)'}")
    print(f"Total de citekeys no manuscrito: {len(used_keys)}")
    print(f"Total de entries no(s) .bib: {len(bib_keys)}")
    print(f"Citekeys SEM entrada no .bib: {len(missing)}")
    print()

    if missing:
        for k in missing:
            print(k)

    if placeholder_used:
        print("\nCitekeys do tipo RefN detectados no manuscrito (mesmo que existam no .bib, normalmente são placeholders):")
        print(", ".join(placeholder_used))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
