
"""Puncture Strength Analysis Plot (English)

Generates figures for Puncture Strength vs Time:

Figure 8A (Resin):
- Typha domingensis and Syagrus coronata
- Resin coatings (Untreated / Monolayer / Bilayer)

Figure 8B (NaOH):
- Typha domingensis (Syagrus data missing/incomplete)
- NaOH treatments (0%, 3%, 6%, 9%)

Author: GitHub Copilot
Date: December 2025
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pyreadstat
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path(r"c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\artigo-posdoc\2-ARTIGO_REVISAO")
TABOA_RESIN_PATH = BASE_DIR / "1-REFERENCIAS/TABOA/anova_punção.sav"
TABOA_NAOH_PATH = BASE_DIR / "1-REFERENCIAS/TABOA/DADOS TABOA PUNÇÃO.completo.sav"
SYAGRUS_RESIN_PATH = BASE_DIR / "1-REFERENCIAS/OURICURI/Dados punção tempos.sav"
OUTPUT_DIR = BASE_DIR / "3-IMAGENS"

def load_taboa_resin():
    df, meta = pyreadstat.read_sav(TABOA_RESIN_PATH)
    # Columns: Tratamentos, Tempos, geotextil, punção
    # Tratamentos: 1=Sem, 2=Mono, 3=Bi
    df['Species'] = 'Typha domingensis'
    df['Treatment_Type'] = 'Resin'
    treatment_map = {1.0: 'Untreated', 2.0: 'Monolayer Resin', 3.0: 'Bilayer Resin'}
    df['Treatment_Level'] = df['Tratamentos'].map(treatment_map)
    df = df.rename(columns={'Tempos': 'Days', 'punção': 'Load'})
    return df[['Species', 'Treatment_Type', 'Treatment_Level', 'Days', 'Load']]

def load_taboa_naoh():
    df, meta = pyreadstat.read_sav(TABOA_NAOH_PATH)
    # Columns: Tratamentos, Tempos, Controle, tres, seis, nove
    # Wide format. Melt it.
    # Tratamentos column seems useless (all 0).
    df = df.drop(columns=['Tratamentos'])
    df = df.melt(id_vars=['Tempos'], var_name='Treatment_Code', value_name='Load')
    
    code_map = {
        'Controle': '0% NaOH',
        'tres': '3% NaOH',
        'seis': '6% NaOH',
        'nove': '9% NaOH'
    }
    df['Treatment_Level'] = df['Treatment_Code'].map(code_map)
    df['Species'] = 'Typha domingensis'
    df['Treatment_Type'] = 'NaOH'
    df = df.rename(columns={'Tempos': 'Days'})
    return df[['Species', 'Treatment_Type', 'Treatment_Level', 'Days', 'Load']]

def load_syagrus_resin():
    df, meta = pyreadstat.read_sav(SYAGRUS_RESIN_PATH)
    # Columns: Tratamentos, Repetição, punção_30, punção_60...
    # Wide format. Melt it.
    # Tratamentos: 0=Sem, 1=Mono, 2=Bi
    
    # Filter only Resin treatments (0, 1, 2)
    df = df[df['Tratamentos'].isin([0, 1, 2])]
    
    id_vars = ['Tratamentos', 'Repetição']
    value_vars = [c for c in df.columns if c.startswith('punção_')]
    
    df_long = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='Time_Str', value_name='Load')
    
    # Extract days from 'punção_30' -> 30
    df_long['Days'] = df_long['Time_Str'].str.extract(r'(\d+)').astype(float)
    
    treatment_map = {0.0: 'Untreated', 1.0: 'Monolayer Resin', 2.0: 'Bilayer Resin'}
    df_long['Treatment_Level'] = df_long['Tratamentos'].map(treatment_map)
    df_long['Species'] = 'Syagrus coronata'
    df_long['Treatment_Type'] = 'Resin'
    
    return df_long[['Species', 'Treatment_Type', 'Treatment_Level', 'Days', 'Load']]

def plot_resin(df):
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Define order and colors
    hue_order = ['Untreated', 'Monolayer Resin', 'Bilayer Resin']
    palette = {'Untreated': 'gray', 'Monolayer Resin': 'blue', 'Bilayer Resin': 'green'}
    
    g = sns.lineplot(
        data=df,
        x="Days",
        y="Load",
        hue="Treatment_Level",
        style="Species",
        hue_order=hue_order,
        palette=palette,
        markers=True,
        dashes=True,
        err_style="bars",
        errorbar=("ci", 95),
        linewidth=2,
        markersize=8
    )
    
    plt.title("Puncture Strength vs Time (Resin Treatments)", fontsize=14)
    plt.xlabel("Exposure Time (days)", fontsize=12)
    plt.ylabel("Puncture Load (N)", fontsize=12)
    plt.legend(title="Treatment / Species", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "puncture_resin_english.png", dpi=300)
    plt.close()

def plot_naoh(df):
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    hue_order = ['0% NaOH', '3% NaOH', '6% NaOH', '9% NaOH']
    palette = sns.color_palette("Reds", n_colors=4)
    
    g = sns.lineplot(
        data=df,
        x="Days",
        y="Load",
        hue="Treatment_Level",
        style="Species",
        hue_order=hue_order,
        palette=palette,
        markers=True,
        dashes=True,
        err_style="bars",
        errorbar=("ci", 95),
        linewidth=2,
        markersize=8
    )
    
    plt.title("Puncture Strength vs Time (NaOH Treatments)", fontsize=14)
    plt.xlabel("Exposure Time (days)", fontsize=12)
    plt.ylabel("Puncture Load (N)", fontsize=12)
    plt.legend(title="Treatment / Species", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "puncture_naoh_english.png", dpi=300)
    plt.close()

def main():
    print("Loading data...")
    try:
        df_taboa_resin = load_taboa_resin()
        df_syagrus_resin = load_syagrus_resin()
        df_resin = pd.concat([df_taboa_resin, df_syagrus_resin], ignore_index=True)
        
        print(f"Resin Data: {len(df_resin)} rows")
        plot_resin(df_resin)
        print("Resin plot created.")
        
    except Exception as e:
        print(f"Error processing Resin data: {e}")

    try:
        df_taboa_naoh = load_taboa_naoh()
        # Syagrus NaOH missing
        df_naoh = df_taboa_naoh
        
        print(f"NaOH Data: {len(df_naoh)} rows")
        plot_naoh(df_naoh)
        print("NaOH plot created.")
        
    except Exception as e:
        print(f"Error processing NaOH data: {e}")

if __name__ == "__main__":
    main()
