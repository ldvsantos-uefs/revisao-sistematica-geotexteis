#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os DOCX do pacote de submissão (ICP) a partir dos arquivos .md.

Wrapper para `4-CODIGOS/gerar-docx.py` (usa Pandoc por baixo).

Gera DOCX para:
- title_page.md -> title_page.docx
- cover_letter_en.md -> cover_letter_en.docx
- statements.md -> statements.docx
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
        description="Gera os DOCX do pacote ICP a partir dos .md usando gerar-docx.py"
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help=(
            "Diretório de saída para os DOCX gerados (padrão: 2-MANUSCRITO/submissao_icp/_build)."
        ),
    )
    return parser.parse_args()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    manuscript_dir = repo_root / "2-MANUSCRITO"
    icp_dir = manuscript_dir / "submissao_icp"
    gerar_docx_py = repo_root / "4-CODIGOS" / "gerar-docx.py"

    if not gerar_docx_py.exists():
        print(f"[ERRO] Não encontrei {gerar_docx_py}")
        return 2

    args = parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (icp_dir / "_build")
    out_dir.mkdir(parents=True, exist_ok=True)

    mapping: list[tuple[Path, Path]] = [
        (icp_dir / "title_page.md", out_dir / "title_page.docx"),
        (icp_dir / "cover_letter_en.md", out_dir / "cover_letter_en.docx"),
        (icp_dir / "statements.md", out_dir / "statements.docx"),
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

    if exit_code == 0:
        print("[OK] Pacote ICP: DOCX gerados com sucesso.")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
