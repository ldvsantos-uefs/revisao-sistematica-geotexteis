
import pandas as pd
import pyreadstat
import os

files = [
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\1-REFERENCIAS\TABOA\DADOS TABOA PUNÇÃO.completo.sav",
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\1-REFERENCIAS\OURICURI\Dados punção tempos.sav"
]

for f in files:
    print(f"--- Inspecting {os.path.basename(f)} ---")
    if not os.path.exists(f):
        print("File not found.")
        continue
        
    try:
        df, meta = pyreadstat.read_sav(f)
        print("Columns:", df.columns.tolist())
        
        if 'DADOS TABOA PUNÇÃO.completo.sav' in f:
            print("Head:\n", df.head())
            
        if 'Dados punção tempos.sav' in f:
            # Check Treatment 3
            t3 = df[df['Tratamentos'] == 3.0]
            print("Treatment 3 count:", len(t3))
            if not t3.empty:
                print("Treatment 3 sample:\n", t3.head())
            
    except Exception as e:
        print(f"Error: {e}")
    print("\n")
