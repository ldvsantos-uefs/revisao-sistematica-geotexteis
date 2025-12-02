import os
import pandas as pd
from pathlib import Path

BASE = Path(r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\1-REFERENCIAS\_EXTRAIDOS")
OUT_MD = Path(r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\_atualizacoes_consolidadas.md")

files = {
    "Dados_gerais_1.csv": None,
    "Dados tensão  tempos.csv": None,
    "Dados deformação tempos.csv": None,
    "Dados punção tempos.csv": None,
    "DADOS TABOA TRAÇÃO.csv": None,
    "DADOS TABOA PUNÇÃO.csv": None,
}

loaded = {}
for fname in files:
    fpath = BASE / fname
    if fpath.exists():
        df = pd.read_csv(fpath)
        loaded[fname] = df
    else:
        loaded[fname] = None

lines = []
lines.append("# Atualizações consolidadas (CSV)\n")
lines.append("\n## Sumários estatísticos por arquivo\n")

for fname, df in loaded.items():
    lines.append(f"\n### {fname}")
    if df is None:
        lines.append("\n- Arquivo não encontrado.")
        continue
    # pequena limpeza de nomes de colunas
    df.columns = [c.strip() for c in df.columns]
    # estatísticas básicas
    desc = df.select_dtypes(include=['float64','int64']).describe().round(3)
    lines.append("\nColunas: " + ", ".join(df.columns))
    lines.append(f"\nDimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
    lines.append("\nEstatísticas (numéricas):\n")
    lines.append(desc.to_markdown())

# derivar alguns indicadores chave
lines.append("\n## Indicadores derivados\n")
try:
    df_tensao = loaded.get("Dados tensão  tempos.csv")
    if df_tensao is not None:
        cols_t = [c for c in df_tensao.columns if "tensão_max_" in c]
        tensao_means = df_tensao[cols_t].mean().round(2)
        lines.append("\n- Tensão média por tempo (tensão_max_*):")
        for c, v in tensao_means.items():
            lines.append(f"  - {c}: {v}")
except Exception as e:
    lines.append(f"\n[WARN] Erro ao calcular tensão média: {e}")

try:
    df_punc = loaded.get("Dados punção tempos.csv")
    if df_punc is not None:
        cols_p = [c for c in df_punc.columns if "punção_" in c]
        p_means = df_punc[cols_p].mean().round(2)
        lines.append("\n- Punção média por tempo:")
        for c, v in p_means.items():
            lines.append(f"  - {c}: {v}")
except Exception as e:
    lines.append(f"\n[WARN] Erro ao calcular punção média: {e}")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print("[OK] Gerado:", OUT_MD)
