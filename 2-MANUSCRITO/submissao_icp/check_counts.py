from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9']+")


def _extract_docx_text(docx_path: Path) -> str:
    # DOCX is a ZIP; main body is word/document.xml
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="replace")

    # Keep paragraph boundaries as newlines (very rough)
    xml = xml.replace("</w:p>", "\n")

    # Remove tags
    text = re.sub(r"<[^>]+>", " ", xml)

    # Unescape the most common entities
    text = (
        text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
    )

    # Normalize whitespace
    text = re.sub(r"[\t\r ]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text.strip()


def _count_figures_docx(docx_path: Path) -> int:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="replace")

    # Count drawings/pictures (approx.)
    drawings = len(re.findall(r"<w:drawing\b", xml))
    picts = len(re.findall(r"<w:pict\b", xml))
    return drawings + picts


def _extract_abstract(text: str) -> str:
    # Heuristic: find 'Abstract' heading and capture until 'Keywords'
    # Works for typical DOCX exports where headings are plain text lines.
    lower = text.lower()
    start = lower.find("abstract")
    if start == -1:
        return ""

    after = text[start:]
    # Drop the heading word itself
    after = re.sub(r"^abstract\b\s*", "", after, flags=re.I)

    # Stop at Keywords (or Resumo)
    m = re.search(r"\bkeywords\b|\bresumo\b", after, flags=re.I)
    if not m:
        return after

    return after[: m.start()].strip()


def _count_words(s: str) -> int:
    return len(WORD_RE.findall(s))


def main() -> int:
    default_input = Path(
        r"C:/Users/vidal/OneDrive/Documentos/13 - CLONEGIT/artigo-posdoc/ARTIGO CREF/2 - MANUSCRITO/submissao_pmr/manuscript_anonymous_en.docx"
    )

    parser = argparse.ArgumentParser(
        description="Conta palavras e figuras (aprox.) do arquivo principal de submissão PMR."
    )
    parser.add_argument(
        "--input",
        default=str(default_input),
        help="Caminho do arquivo principal (DOCX). Padrão: manuscript_anonymous_en.docx",
    )
    parser.add_argument(
        "--nominal-words-per-figure",
        type=int,
        default=280,
        help="Regra nominal da PMR para contar figuras/tabelas como palavras (padrão: 280).",
    )

    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {input_path}")

    if input_path.suffix.lower() != ".docx":
        raise SystemExit("Este script está configurado para DOCX (.docx).")

    text = _extract_docx_text(input_path)
    abstract = _extract_abstract(text)

    total_words = _count_words(text)
    abstract_words = _count_words(abstract) if abstract else 0

    figures = _count_figures_docx(input_path)
    nominal_fig_words = figures * int(args.nominal_words_per_figure)

    print("INPUT", str(input_path))
    print("TOTAL_WORDS_APPROX", total_words)
    print("ABSTRACT_WORDS_APPROX", abstract_words)
    print("FIGURES_APPROX", figures)
    print("NOMINAL_FIGURE_WORDS", nominal_fig_words)
    print("TOTAL_SCREENING_APPROX", total_words + nominal_fig_words)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
