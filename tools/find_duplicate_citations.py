import argparse
import re
import collections
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Encontra citekeys duplicados no manuscrito Pandoc")
    parser.add_argument(
        "--manuscript",
        type=Path,
        default=repo_root / "2-MANUSCRITO" / "Review_Article_Draft.md",
        help="Caminho para o manuscrito .md (default: 2-MANUSCRITO/Review_Article_Draft.md)",
    )
    args = parser.parse_args()
    manuscript: Path = args.manuscript

    text = manuscript.read_text(encoding="utf-8")
    lines = text.splitlines()

    bracket_pat = re.compile(r"\[([^\]]*?@[^\]]*?)\]")
    key_pat = re.compile(r"@([A-Za-z][A-Za-z0-9_:\-]*)")
    # Narrative citations should not match emails like name@gmail.com.
    # Require that '@' is not preceded by a word char or '<'.
    narrative_key_pat = re.compile(r"(?<![A-Za-z0-9_<])@([A-Za-z][A-Za-z0-9_:\-]*)")

    locations: dict[str, list[tuple[int, str, str]]] = collections.defaultdict(list)

    for line_no, line in enumerate(lines, start=1):
        for m in bracket_pat.finditer(line):
            block = m.group(1)
            for km in key_pat.finditer(block):
                locations[km.group(1)].append((line_no, "bracket", line.strip()))

        scrub = bracket_pat.sub("", line)
        for km in narrative_key_pat.finditer(scrub):
            locations[km.group(1)].append((line_no, "narrative", line.strip()))

    duplicates = {k: v for k, v in locations.items() if len(v) > 1}

    print(f"distinct_citekeys={len(locations)}")
    print(f"duplicate_citekeys={len(duplicates)}")

    for key in sorted(duplicates, key=lambda k: len(duplicates[k]), reverse=True):
        occ = duplicates[key]
        print(f"\n{key}\t{len(occ)}")
        for (ln, kind, snip) in occ[:10]:
            s = snip
            if len(s) > 220:
                s = s[:217] + "..."
            print(f"  L{ln} {kind}: {s}")
        if len(occ) > 10:
            print(f"  ... +{len(occ) - 10} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
