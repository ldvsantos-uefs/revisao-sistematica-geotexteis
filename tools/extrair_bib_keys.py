#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Extrai entradas BibTeX por citekey de um arquivo .bib.

Uso:
  python tools/extrair_bib_keys.py --source 2-MANUSCRITO/library.bib --out 2-MANUSCRITO/bibliografia_extra.bib --keys Key1 Key2 ...

Observações:
- Não exige que o arquivo .bib de origem esteja 100% válido (ele apenas busca blocos @...{key, ... } por contagem de chaves).
- Útil quando `library.bib` é grande e contém entradas quebradas, mas você só precisa de algumas referências.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _extract_entries_by_keys(source_text: str, keys: list[str]) -> tuple[dict[str, str], list[str]]:
    wanted = {k.strip() for k in keys if k.strip()}
    found: dict[str, str] = {}

    current_key: str | None = None
    capturing = False
    brace_depth = 0
    buf: list[str] = []

    def flush_if_complete() -> None:
        nonlocal current_key, capturing, brace_depth, buf
        if capturing and current_key is not None and brace_depth == 0:
            found[current_key] = "".join(buf).rstrip() + "\n"
            current_key = None
            capturing = False
            buf = []

    i = 0
    n = len(source_text)

    # Processa linha a linha, mas contando chaves por caractere para robustez.
    line_start = 0
    while i < n:
        if source_text[i] == "\n":
            line = source_text[line_start : i + 1]
            line_start = i + 1

            if not capturing:
                # início de entrada: @type{Key,
                if line.lstrip().startswith("@"):  # rápida poda
                    stripped = line.strip()
                    if "{" in stripped and "," in stripped:
                        try:
                            before, after = stripped.split("{", 1)
                            key_part = after.split(",", 1)[0].strip()
                        except ValueError:
                            key_part = ""
                        if key_part in wanted and key_part not in found:
                            capturing = True
                            current_key = key_part
                            buf = [line]
                            brace_depth = line.count("{") - line.count("}")
                            flush_if_complete()
            else:
                buf.append(line)
                brace_depth += line.count("{") - line.count("}")
                flush_if_complete()

        i += 1

    # Fecha último bloco caso o arquivo não termine com \n
    if line_start < n:
        line = source_text[line_start:]
        if capturing:
            buf.append(line)
            brace_depth += line.count("{") - line.count("}")
            if capturing and current_key is not None and brace_depth == 0:
                found[current_key] = "".join(buf).rstrip() + "\n"

    missing = [k for k in keys if k not in found]
    return found, missing


def main() -> int:
    ap = argparse.ArgumentParser(description="Extrai entradas BibTeX por citekey.")
    ap.add_argument("--source", required=True, type=Path, help="Arquivo .bib de origem")
    ap.add_argument("--out", required=True, type=Path, help="Arquivo .bib de saída (somente chaves solicitadas)")
    ap.add_argument("--keys", required=True, nargs="+", help="Lista de citekeys a extrair")
    args = ap.parse_args()

    src: Path = args.source
    out: Path = args.out
    keys: list[str] = args.keys

    if not src.exists():
        raise SystemExit(f"Arquivo de origem não encontrado: {src}")

    source_text = src.read_text(encoding="utf-8", errors="replace")
    found, missing = _extract_entries_by_keys(source_text, keys)

    out.parent.mkdir(parents=True, exist_ok=True)

    blocks: list[str] = []
    for k in keys:
        if k in found:
            blocks.append(found[k])

    out.write_text("\n".join(b.rstrip() for b in blocks).rstrip() + "\n", encoding="utf-8")

    print(f"[OK] Gerado: {out} ({len(blocks)}/{len(keys)} entradas)")
    if missing:
        print("[AVISO] Chaves não encontradas:")
        for k in missing:
            print(f"  - {k}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
