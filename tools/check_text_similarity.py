#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Heurística local de similaridade entre textos (anti-plágio).

Objetivo
- Dar um alerta rápido de *similaridade textual* entre dois arquivos (ex.: Markdown).
- Não substitui softwares/serviços de detecção de similaridade usados por periódicos.

Métricas
- Cosine (bag-of-words simples, com stopwords PT básicas)
- Jaccard de 3-gramas de palavras
- SequenceMatcher ratio (difflib) no texto normalizado
- Principais blocos idênticos/altamente similares (trechos)

Uso
  python tools/check_text_similarity.py --a <arquivoA> --b <arquivoB>
  python tools/check_text_similarity.py --a <arquivoA> --b <arquivoB> --top 12
"""

from __future__ import annotations

import argparse
import difflib
import math
import re
from collections import Counter
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]+", re.UNICODE)

# lista curta (intencionalmente) para não distorcer demais
STOP_PT = {
    "a","à","ao","aos","aquela","aquelas","aquele","aqueles","aquilo","as","até",
    "com","como","da","das","de","dela","dele","deles","demais","depois","do","dos",
    "e","é","ela","elas","ele","eles","em","entre","era","eram","essa","essas","esse","esses",
    "esta","está","estão","estas","este","estes","foi","foram","há","isso","isto","já",
    "lhe","lhes","mais","mas","me","mesmo","muito","na","nas","nem","no","nos","nós",
    "o","os","ou","para","pela","pelas","pelo","pelos","por","porque","que","se","sem",
    "ser","são","sua","suas","também","tem","têm","tendo","ter","teu","teus","toda","todas",
    "todo","todos","um","uma","você","vocês",
}


def strip_frontmatter_md(text: str) -> str:
    lines = text.splitlines(True)
    if len(lines) >= 2 and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "".join(lines[i + 1 :])
    return text


def strip_code_fences_md(text: str) -> str:
    # remove blocos ```...```
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "".join(out)


def normalize_text(text: str) -> str:
    text = strip_frontmatter_md(text)
    text = strip_code_fences_md(text)

    # links markdown: [texto](url) -> texto
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

    # remove urls
    text = re.sub(r"https?://\S+", " ", text)

    # remove citekeys estilo pandoc/quarto (@Key) e [@Key; @Key2]
    text = re.sub(r"\[@[^\]]+\]", " ", text)
    text = re.sub(r"@[_:A-Za-z0-9\-]+", " ", text)

    # remove comandos/figuras típicos
    text = re.sub(r"\{[^}]+\}", " ", text)

    # normaliza números e pontuação
    text = text.lower()
    text = re.sub(r"\d+", "0", text)
    text = re.sub(r"[^a-zà-ÿ0\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_words(text: str) -> list[str]:
    toks = [t.lower() for t in WORD_RE.findall(text)]
    toks = [t for t in toks if t not in STOP_PT and len(t) >= 2]
    return toks


def cosine_sim(counter_a: Counter[str], counter_b: Counter[str]) -> float:
    if not counter_a or not counter_b:
        return 0.0
    dot = 0.0
    for k, va in counter_a.items():
        vb = counter_b.get(k)
        if vb:
            dot += va * vb
    na = math.sqrt(sum(v * v for v in counter_a.values()))
    nb = math.sqrt(sum(v * v for v in counter_b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def jaccard_ngrams(words_a: list[str], words_b: list[str], n: int = 3) -> float:
    def grams(ws: list[str]) -> set[tuple[str, ...]]:
        if len(ws) < n:
            return set()
        return {tuple(ws[i : i + n]) for i in range(0, len(ws) - n + 1)}

    ga = grams(words_a)
    gb = grams(words_b)
    if not ga or not gb:
        return 0.0
    inter = len(ga & gb)
    union = len(ga | gb)
    return inter / union if union else 0.0


def summarize_blocks(
    sm: difflib.SequenceMatcher,
    text_a: str,
    text_b: str,
    top: int,
    min_chars: int,
) -> list[dict]:
    blocks = [b for b in sm.get_matching_blocks() if b.size > 0]
    blocks.sort(key=lambda b: b.size, reverse=True)

    out = []
    used = 0
    for b in blocks:
        if used >= top:
            break
        # filtra blocos muito curtos (ruído)
        if b.size < min_chars:
            continue
        snippet_a = text_a[b.a : b.a + b.size]
        snippet_b = text_b[b.b : b.b + b.size]
        out.append(
            {
                "chars": b.size,
                "a_pos": b.a,
                "b_pos": b.b,
                "snippet": snippet_a[:300] + ("…" if len(snippet_a) > 300 else ""),
            }
        )
        used += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Varredura local de similaridade textual entre dois arquivos.")
    ap.add_argument("--a", required=True, help="Arquivo A (ex.: modelo)")
    ap.add_argument("--b", required=True, help="Arquivo B (ex.: manuscrito novo)")
    ap.add_argument("--top", type=int, default=8, help="Quantos blocos similares mostrar (padrão: 8)")
    ap.add_argument(
        "--min-chars",
        type=int,
        default=200,
        help="Tamanho mínimo (em caracteres) para reportar um bloco similar (padrão: 200)",
    )
    args = ap.parse_args()

    path_a = Path(args.a).expanduser().resolve()
    path_b = Path(args.b).expanduser().resolve()

    if not path_a.exists():
        raise SystemExit(f"Arquivo A não encontrado: {path_a}")
    if not path_b.exists():
        raise SystemExit(f"Arquivo B não encontrado: {path_b}")

    raw_a = path_a.read_text(encoding="utf-8", errors="replace")
    raw_b = path_b.read_text(encoding="utf-8", errors="replace")

    norm_a = normalize_text(raw_a)
    norm_b = normalize_text(raw_b)

    wa = tokenize_words(norm_a)
    wb = tokenize_words(norm_b)

    bow_a = Counter(wa)
    bow_b = Counter(wb)

    cos = cosine_sim(bow_a, bow_b)
    jac3 = jaccard_ngrams(wa, wb, n=3)

    sm = difflib.SequenceMatcher(a=norm_a, b=norm_b, autojunk=True)
    seq = sm.ratio()

    blocks = summarize_blocks(sm, norm_a, norm_b, top=args.top, min_chars=args.min_chars)

    print("A", str(path_a))
    print("B", str(path_b))
    print("WORDS_A", len(wa))
    print("WORDS_B", len(wb))
    print("COSINE_BOW", f"{cos:.4f}")
    print("JACCARD_WORD3", f"{jac3:.4f}")
    print("SEQMATCH_RATIO", f"{seq:.4f}")

    if blocks:
        print("\nTOP_BLOCKS")
        for i, b in enumerate(blocks, 1):
            print(f"#{i} CHARS {b['chars']} A_POS {b['a_pos']} B_POS {b['b_pos']}")
            print(b["snippet"])
            print("---")
    else:
        print(f"\nTOP_BLOCKS (nenhum bloco >= {args.min_chars} chars após normalização)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
