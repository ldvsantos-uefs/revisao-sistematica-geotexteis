#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os DOCX do pacote de submissão PMR a partir dos arquivos .md.

Este script é um wrapper para `2 - MANUSCRITO/gerar-docx.py`.

Ele gera DOCX para:
- title_page.md -> title_page.docx
- cover_letter_en.md -> cover_letter_en.docx
- statements.md -> statements.docx
- biographical_notes.md -> biographical_notes.docx

Além disso, por padrão, também gera:
- artigo_cref_2.md -> artigo_cref_2.docx
- apendice_tabelas_informacionais.md -> apendice_tabelas_informacionais.docx

Opcionalmente, pode gerar/atualizar o manuscrito anônimo (DOCX) se você informar
um Markdown de entrada em inglês e anonimizado.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_gerar_docx(gerar_docx_py: Path, input_md: Path, output_docx: Path) -> int:
    cmd = [
        sys.executable,
        str(gerar_docx_py),
        "--input",
        str(input_md),
        "--output",
        str(output_docx),
    ]
    print(f"[INFO] Gerando: {output_docx.name} (a partir de {input_md.name})")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[ERRO] Falha ao gerar {output_docx.name}")
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera os DOCX do pacote PMR a partir dos .md usando gerar-docx.py"
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help=(
            "Diretório de saída para os DOCX gerados (padrão: 2 - MANUSCRITO/submissao_pmr/_build)."
        ),
    )
    parser.add_argument(
        "--manuscript-input",
        default=None,
        help=(
            "Markdown do manuscrito anônimo (em inglês) para gerar manuscript_anonymous_en.docx. "
            "Se não informado, o manuscrito não é gerado por este script."
        ),
    )
    return parser.parse_args()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]  # .../2 - MANUSCRITO
    gerar_docx_py = repo_root / "gerar-docx.py"
    pmr_dir = repo_root / "submissao_pmr"

    if not gerar_docx_py.exists():
        print(f"[ERRO] Não encontrei {gerar_docx_py}")
        return 2

    args = parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (pmr_dir / "_build")
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping: list[tuple[Path, Path]] = [
        (pmr_dir / "title_page.md", out_dir / "title_page.docx"),
        (pmr_dir / "cover_letter_en.md", out_dir / "cover_letter_en.docx"),
        (pmr_dir / "statements.md", out_dir / "statements.docx"),
        (pmr_dir / "biographical_notes.md", out_dir / "biographical_notes.docx"),
        (repo_root / "artigo_cref_2.md", out_dir / "artigo_cref_2.docx"),
        (repo_root / "apendice_tabelas_informacionais.md", out_dir / "apendice_tabelas_informacionais.docx"),
    ]

    missing = [str(inp) for (inp, _) in mapping if not inp.exists()]
    if missing:
        print("[ERRO] Arquivos de entrada não encontrados:")
        for m in missing:
            print(f" - {m}")
        return 2

    exit_code = 0
    for input_md, output_docx in mapping:
        rc = run_gerar_docx(gerar_docx_py, input_md, output_docx)
        if rc != 0:
            exit_code = rc

    if args.manuscript_input:
        manuscript_md = Path(args.manuscript_input).expanduser().resolve()
        manuscript_out = out_dir / "manuscript_anonymous_en.docx"
        if not manuscript_md.exists():
            print(f"[ERRO] manuscript-input não encontrado: {manuscript_md}")
            return 2
        rc = run_gerar_docx(gerar_docx_py, manuscript_md, manuscript_out)
        if rc != 0:
            exit_code = rc
    else:
        print(
            "[INFO] manuscript_anonymous_en.docx não foi gerado por este script (use --manuscript-input)."
        )

    if exit_code == 0:
        print("[OK] Pacote PMR: DOCX gerados com sucesso.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
