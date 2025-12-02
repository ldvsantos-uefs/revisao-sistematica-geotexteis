import os
import pandas as pd
import pyreadstat

BASE = r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\1-REFERENCIAS"

TARGETS = [
    os.path.join(BASE, "OURICURI", "Dados_gerais_1.sav"),
    os.path.join(BASE, "OURICURI", "Dados tensão  tempos.sav"),
    os.path.join(BASE, "OURICURI", "Dados deformação tempos.sav"),
    os.path.join(BASE, "OURICURI", "Dados punção tempos.sav"),
    os.path.join(BASE, "TABOA", "DADOS TABOA TRAÇÃO.sav"),
    os.path.join(BASE, "TABOA", "DADOS TABOA PUNÇÃO.sav"),
]

OUT_DIR = os.path.join(BASE, "_EXTRAIDOS")
os.makedirs(OUT_DIR, exist_ok=True)

for path in TARGETS:
    if not os.path.exists(path):
        print(f"[WARN] Missing: {path}")
        continue
    print("\n=== LENDO:", os.path.basename(path), "===")
    df, meta = pyreadstat.read_sav(path)
    print("Colunas:", list(df.columns))
    print("Dimensões:", df.shape)
    # Exporta CSV simplificado
    csv_name = os.path.splitext(os.path.basename(path))[0] + ".csv"
    out_csv = os.path.join(OUT_DIR, csv_name)
    df.to_csv(out_csv, index=False)
    print("[OK] Exportado:", out_csv)

print("\nConcluído.")
