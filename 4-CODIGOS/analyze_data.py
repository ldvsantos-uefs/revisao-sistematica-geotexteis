import pandas as pd
import os

# Arquivos Excel identificados
excel_files = [
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\1-REFERENCIAS\OURICURI\Dados ouricuri (exemplo).xlsx",
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\1-REFERENCIAS\OURICURI\DADOS_TABELADOS.xlsx",
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\1-REFERENCIAS\TABOA\TABELA PARA ESTATÍSTICA.xlsx",
    r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\1-REFERENCIAS\TABOA\Tabela-Punção.xlsx"
]

for filepath in excel_files:
    if os.path.exists(filepath):
        print(f"\n{'='*80}")
        print(f"ARQUIVO: {os.path.basename(filepath)}")
        print(f"{'='*80}\n")
        
        try:
            # Ler todas as sheets
            excel_file = pd.ExcelFile(filepath)
            print(f"Sheets disponíveis: {excel_file.sheet_names}\n")
            
            # Ler primeira sheet
            df = pd.read_excel(filepath, sheet_name=0)
            print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"\nColunas: {list(df.columns)}\n")
            print("Primeiras 15 linhas:")
            print(df.head(15).to_string())
            print("\n")
            
            # Estatísticas descritivas para colunas numéricas
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                print("Estatísticas descritivas:")
                print(df[numeric_cols].describe().to_string())
                
        except Exception as e:
            print(f"Erro ao processar: {e}")
    else:
        print(f"\nArquivo não encontrado: {filepath}")
