
import pandas as pd
import os

files = [
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\1-REFERENCIAS\OURICURI\Dados ouricuri (exemplo).xlsx",
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO\1-REFERENCIAS\TABOA\Tabela-Punção.xlsx"
]

for f in files:
    print(f"--- Inspecting {os.path.basename(f)} ---")
    if not os.path.exists(f):
        print("File not found.")
        continue
        
    try:
        xls = pd.ExcelFile(f)
        print("Sheet names:", xls.sheet_names)
        
        for sheet in xls.sheet_names:
            print(f"\nSheet: {sheet}")
            df = pd.read_excel(f, sheet_name=sheet, nrows=5)
            print(df.head())
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")
    print("\n")
