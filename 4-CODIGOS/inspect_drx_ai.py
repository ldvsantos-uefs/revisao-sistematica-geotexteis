from __future__ import annotations

from pathlib import Path

import fitz

AI_PATH = Path("3-IMAGENS/fig_drx_taboa.ai")


def main() -> int:
    doc = fitz.open(AI_PATH)
    page = doc[0]

    # Text inventory
    texts: list[str] = []
    dd = page.get_text("dict")
    for b in dd.get("blocks", []):
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            for span in line.get("spans", []):
                t = (span.get("text") or "").strip()
                if t:
                    texts.append(t)

    uniq = sorted(set(texts))
    print(f"AI: {AI_PATH}")
    print(f"Page size: {page.rect.width:.1f} x {page.rect.height:.1f}")
    print(f"Unique text spans: {len(uniq)}")
    for t in uniq:
        print(f"  {t}")

    # Drawing inventory
    drawings = page.get_drawings()
    print(f"\nDrawings: {len(drawings)}")

    dash_counts: dict[str, int] = {}
    widths: dict[float, int] = {}
    colors: dict[str, int] = {}

    def rgb_hex(rgb):
        if not rgb:
            return "None"
        r, g, b = rgb
        return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"

    for d in drawings:
        dashes = d.get("dashes")
        dash_key = str(dashes)
        dash_counts[dash_key] = dash_counts.get(dash_key, 0) + 1
        w = float(d.get("width") or 0.0)
        widths[w] = widths.get(w, 0) + 1
        c = rgb_hex(d.get("color"))
        colors[c] = colors.get(c, 0) + 1

    print("\nTop dash patterns:")
    for k, v in sorted(dash_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]:
        print(f"  {v:>4}  {k}")

    print("\nTop stroke widths:")
    for k, v in sorted(widths.items(), key=lambda kv: kv[1], reverse=True)[:10]:
        print(f"  {v:>4}  {k}")

    print("\nTop colors:")
    for k, v in sorted(colors.items(), key=lambda kv: kv[1], reverse=True)[:10]:
        print(f"  {v:>4}  {k}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
