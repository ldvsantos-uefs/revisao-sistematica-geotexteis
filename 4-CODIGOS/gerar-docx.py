#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar arquivo Word da revisão de escopo a partir do Markdown.

Uso: python gerar-docx.py

Gera o arquivo revisao_artigo.docx a partir do Review_Article_Draft.md.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
import time

def _resource_path_arg(paths: list[Path]) -> str:
    unique: list[str] = []
    for p in paths:
        s = str(p)
        if s not in unique:
            unique.append(s)
    return os.pathsep.join(unique)


def _ensure_list[T](value: T | list[T]) -> list[T]:
    return value if isinstance(value, list) else [value]


def gerar_docx(
    md_file: Path,
    output_file: Path,
    bib_file: Path | list[Path],
    csl_file: Path,
    reference_doc: Path | None = None,
    apendices_file: Path | None = None,
    cwd: Path | None = None,
    resource_paths: list[Path] | None = None,
):
    """
    Gera arquivo DOCX usando Pandoc.
    
    Args:
        md_file: Arquivo Markdown de entrada
        output_file: Arquivo DOCX de saída
        bib_file: Arquivo(s) de bibliografia
        csl_file: Arquivo de estilo de citação
        apendices_file: Arquivo de apêndices (opcional)
    
    Returns:
        0 se sucesso, 1 se erro
    """
    print(f"\nGerando {output_file.name}...")
    
    # Remover arquivo antigo se existir
    if output_file.exists():
        print(f"[INFO] Removendo arquivo antigo: {output_file.name}")
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                output_file.unlink()
                break
            except PermissionError:
                if attempt < max_attempts - 1:
                    print(f"[AVISO] Tentativa {attempt + 1}/{max_attempts}: Arquivo em uso, aguardando...")
                    time.sleep(0.6)
                else:
                    print(f"Erro: nao foi possivel remover '{output_file.name}'.")
                    print("Certifique-se de que o arquivo não está aberto no Word ou OneDrive.")
                    return 1
    
    if cwd is None:
        cwd = md_file.parent

    # Comando Pandoc
    cmd = [
        "pandoc",
        str(md_file),
    ]
    
    # Adicionar apêndices ANTES do --citeproc
    if apendices_file and apendices_file.exists():
        cmd.append(str(apendices_file))
        print(f"[INFO] Incluindo apendices: {apendices_file.name}")
    
    # Adicionar resource-path para encontrar CSL/BIB/figuras (compatível com Windows via os.pathsep)
    if resource_paths is None:
        resource_paths = [Path("."), Path("..")]  # manuscrito + raiz do repositório
    cmd.extend(["--resource-path", _resource_path_arg(resource_paths)])
    
    # Adicionar processamento de citações
    cmd.append("--citeproc")

    for bf in _ensure_list(bib_file):
        cmd.extend([
            "--bibliography",
            str(bf),
        ])

    cmd.extend([
        "--csl",
        str(csl_file),
    ])
    
    # Adicionar modelo de formatação se existir
    if reference_doc is not None:
        reference_doc = Path(reference_doc)
        if reference_doc.exists():
            cmd.extend([
                "--reference-doc",
                str(reference_doc),
            ])
    
    cmd.extend(["-o", str(output_file)])
    
    print("Executando Pandoc...")
    
    try:
        # Executar Pandoc
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(cwd),
        )
        
        # Mostrar warnings/erros do Pandoc
        if result.stderr:
            print(f"\nAvisos do Pandoc para {output_file.name}:")
            print(result.stderr)
        
        # Verificar código de saída do Pandoc
        if result.returncode != 0:
            print(f"\nErro: Pandoc retornou código {result.returncode} ao gerar {output_file.name}.")
            if result.stdout:
                print("Saída:", result.stdout)
            return 1
        
        # Verificar se o arquivo foi criado
        if output_file.exists():
            print(f"\nArquivo {output_file.name} gerado com sucesso.")
            print(f"Localização: {output_file.absolute()}")
            print(f"Tamanho: {output_file.stat().st_size / 1024:.1f} KB")
            return 0
        else:
            print(f"\nErro: o arquivo {output_file.name} não foi gerado.")
            if result.stdout:
                print("Saída:", result.stdout)
            return 1
            
    except FileNotFoundError:
        print("\nErro: Pandoc não está instalado ou não está no PATH do sistema.")
        print("Instale o Pandoc em: https://pandoc.org/installing.html")
        return 1
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        return 1

def gerar_pdf(
    md_file: Path,
    output_file: Path,
    bib_file: Path | list[Path],
    csl_file: Path,
    pdf_engine: str = "xelatex",
) -> int:
    """
    Gera arquivo PDF usando Pandoc com um motor LaTeX (xelatex por padrão).

    Args:
        md_file: Arquivo Markdown de entrada
        output_file: Arquivo PDF de saída
        bib_file: Arquivo de bibliografia
        csl_file: Arquivo de estilo de citação
        pdf_engine: Motor de conversão para PDF (xelatex, lualatex, pdflatex)

    Returns:
        0 se sucesso, 1 se erro
    """
    print(f"\nGerando {output_file.name}...")

    # Remover arquivo antigo se existir
    if output_file.exists():
        print(f"📝 Removendo arquivo antigo: {output_file.name}")
        try:
            output_file.unlink()
        except PermissionError:
            print(f"Erro: não foi possível remover '{output_file.name}'. Verifique se está aberto.")
            return 1

    cmd = [
        "pandoc",
        str(md_file),
        "--citeproc",
    ]

    for bf in _ensure_list(bib_file):
        cmd.extend(["--bibliography", str(bf)])

    cmd.extend([
        "--csl", str(csl_file),
        "-o", str(output_file),
        "--pdf-engine", pdf_engine,
    ])

    print("Executando Pandoc para PDF...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            print("Avisos do Pandoc (PDF):")
            print(result.stderr)
        if result.returncode != 0:
            print(f"Erro: Pandoc retornou código {result.returncode} ao gerar {output_file.name}.")
            return 1
        if output_file.exists():
            print(f"Arquivo {output_file.name} gerado com sucesso.")
            return 0
        else:
            print(f"Erro: o arquivo {output_file.name} não foi gerado.")
            return 1
    except FileNotFoundError:
        print("Erro: Pandoc não encontrado. Instale Pandoc antes de continuar.")
        return 1
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gera DOCX via Pandoc a partir de Markdown. Sem argumentos, gera os DOCX padrão do manuscrito. "
            "Com --input/--output, gera um DOCX específico (ex.: pacote de submissão)."
        )
    )
    parser.add_argument("--input", default=None, help="Arquivo Markdown de entrada")
    parser.add_argument("--output", default=None, help="Arquivo DOCX de saída")
    parser.add_argument("--pdf", "-p", action="store_true", help="(modo padrão) também gerar PDF do manuscrito PT")
    return parser.parse_args()

def main():
    # Resolver caminhos a partir da raiz do repositório (Windows-friendly)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    manuscript_dir = repo_root / "2-MANUSCRITO"

    if not manuscript_dir.exists():
        print(f"\nErro: pasta 2-MANUSCRITO não encontrada em: {manuscript_dir}")
        return 1
    
    print("=" * 70)
    print("GERADOR DE REVISÃO DE ESCOPO - WORD")
    print("=" * 70)

    args = _parse_args()
    
    # Arquivos comuns (sempre dentro de 2-MANUSCRITO)
    bib_file = manuscript_dir / "referencias.bib"
    bib_extra = manuscript_dir / "bibliografia_extra.bib"
    csl_file = manuscript_dir / "springer-vancouver.csl"
    reference_doc = manuscript_dir / "modelo_formatacao.docx"
    
    # Verificar arquivos necessários
    # `library.bib` é opcional: quando existe, agrega mais referências ao citeproc
    arquivos_necessarios = [bib_file, csl_file]
    arquivos_faltando = [f for f in arquivos_necessarios if not f.exists()]
    
    if arquivos_faltando:
        print("\nErro: arquivos necessários não encontrados:")
        for arquivo in arquivos_faltando:
            print(f"   - {arquivo}")
        return 1
    
    # Contador de sucesso
    sucessos = 0
    total = 0
    
    # ========================================================================
    # GERAR REVISÃO DE ESCOPO
    # ========================================================================
    # Resource-path: manuscrito + raiz do repositório (resolve imagens em ../3-IMAGENS etc.)
    resource_paths = [manuscript_dir, repo_root]

    bib_files: list[Path] = [bib_file]
    if bib_extra.exists():
        bib_files.append(bib_extra)

    # ========================================================================
    # MODO: gerar um DOCX específico (wrapper para pacotes de submissão)
    # ========================================================================
    if args.input or args.output:
        if not (args.input and args.output):
            print("\nErro: use --input e --output juntos.")
            return 1

        input_md = Path(args.input).expanduser().resolve()
        output_docx = Path(args.output).expanduser().resolve()
        if not input_md.exists():
            print(f"\nErro: arquivo de entrada não encontrado: {input_md}")
            return 1

        output_docx.parent.mkdir(parents=True, exist_ok=True)

        # Inclui o diretório do input no resource-path para resolver imagens/arquivos relativos
        rp = [input_md.parent, manuscript_dir, repo_root]
        rc = gerar_docx(
            input_md,
            output_docx,
            bib_files,
            csl_file,
            reference_doc=reference_doc,
            cwd=input_md.parent,
            resource_paths=rp,
        )
        return 0 if rc == 0 else 1

    # Versão PT
    md_pt = manuscript_dir / "Review_Article_Draft.md"
    docx_pt = manuscript_dir / "Review_Article_Draft.docx"
    if md_pt.exists():
        total += 1
        result_pt = gerar_docx(
            md_pt,
            docx_pt,
            bib_files,
            csl_file,
            reference_doc=reference_doc,
            cwd=manuscript_dir,
            resource_paths=resource_paths,
        )
        if result_pt == 0:
            sucessos += 1
    else:
        print(f"\n[AVISO] Arquivo não encontrado (PT): {md_pt}")

    # Versão EN
    md_en = manuscript_dir / "Review_Article_English.md"
    docx_en = manuscript_dir / "Review_Article_English.docx"
    if md_en.exists():
        total += 1
        result_en = gerar_docx(
            md_en,
            docx_en,
            bib_files,
            csl_file,
            reference_doc=reference_doc,
            cwd=manuscript_dir,
            resource_paths=resource_paths,
        )
        if result_en == 0:
            sucessos += 1
    else:
        print(f"\n[AVISO] Arquivo não encontrado (EN): {md_en}")

    # Gerar PDF opcionalmente
    # Use argumento de linha de comando: python gerar-docx.py --pdf
    if args.pdf:
        pdf_output = manuscript_dir / "Review_Article_Draft.pdf"
        print("\n[INFO] Opcao de PDF detectada - gerando PDF com xelatex...")
        if md_pt.exists():
            total += 1
            result_pdf = gerar_pdf(md_pt, pdf_output, bib_files, csl_file, pdf_engine="xelatex")
            if result_pdf == 0:
                sucessos += 1
        else:
            print("[AVISO] Arquivo Markdown não encontrado para gerar PDF")
    
    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 RESUMO DA GERAÇÃO")
    print("=" * 70)
    print(f"[OK] Arquivos gerados com sucesso: {sucessos}/{total}")
    
    if sucessos == total:
        print("\nTodos os arquivos foram gerados com sucesso.")
        return 0
    elif sucessos > 0:
        print(f"\nAlguns arquivos não foram gerados ({total - sucessos} falharam).")
        return 1
    else:
        print("\nNenhum arquivo foi gerado.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
