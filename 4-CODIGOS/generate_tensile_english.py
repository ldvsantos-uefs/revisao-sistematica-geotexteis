"""
Tensile Strength Analysis Plot
Typha domingensis vs Syagrus coronata
English Version

Author: Diego Vidal
Date: December 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_and_plot_tensile():
    # Paths
    data_path = Path("./5-DADOS/TABELA PARA ESTATÍSTICA.xlsx")
    output_dir = Path("./5-DADOS/MEV-ANALISE/resultados_en")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        return

    print("Loading Tensile data...")
    try:
        df = pd.read_excel(data_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Filter for Typha (Taboa) and Syagrus (Ouricuri) - exclude Junco
        df = df[df['Geotextil'].isin(['Taboa', 'Ouricuri'])]
        
        # Rename for English
        df['Species'] = df['Geotextil'].map({
            'Taboa': 'Typha domingensis',
            'Ouricuri': 'Syagrus coronata'
        })
        
        # Define treatments
        treatments = {
            '0x resina': 'Untreated',
            '1x resina': 'Monolayer Resin',
            '2x resina': 'Bilayer Resin' # Note: original might have space, strip() handled it
        }
        
        # Check unique treatments after strip
        # print(df['Tratamentos'].unique())
        
        df['Treatment_En'] = df['Tratamentos'].map(treatments)
        
        # Setup plot
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        fig.suptitle('Tensile Strength Evolution (UTS)', fontsize=16, fontweight='bold')
        
        # Plot configuration
        palette = {'Typha domingensis': '#2E7D32', 'Syagrus coronata': '#D84315'}
        markers = {'Typha domingensis': 'o', 'Syagrus coronata': 's'}
        
        # Subplot 1: Untreated
        ax1 = axes[0]
        data_untreated = df[df['Treatment_En'] == 'Untreated']
        sns.lineplot(data=data_untreated, x='Tempos (dias)', y='Tensão Max de ruptura (N/mm)', 
                    hue='Species', style='Species', palette=palette, markers=markers, 
                    ax=ax1, linewidth=2.5, markersize=9)
        ax1.set_title('(a) Untreated Fibers', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Exposure Time (days)', fontsize=12)
        ax1.set_ylabel('Tensile Strength (N/mm)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(title=None, fontsize=10)
        
        # Subplot 2: Monolayer
        ax2 = axes[1]
        data_mono = df[df['Treatment_En'] == 'Monolayer Resin']
        sns.lineplot(data=data_mono, x='Tempos (dias)', y='Tensão Max de ruptura (N/mm)', 
                    hue='Species', style='Species', palette=palette, markers=markers, 
                    ax=ax2, linewidth=2.5, markersize=9)
        ax2.set_title('(b) Monolayer Resin', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Exposure Time (days)', fontsize=12)
        ax2.set_ylabel('')
        ax2.grid(True, alpha=0.3)
        ax2.legend().remove() # Shared legend
        
        # Subplot 3: Bilayer
        ax3 = axes[2]
        data_bi = df[df['Treatment_En'] == 'Bilayer Resin']
        sns.lineplot(data=data_bi, x='Tempos (dias)', y='Tensão Max de ruptura (N/mm)', 
                    hue='Species', style='Species', palette=palette, markers=markers, 
                    ax=ax3, linewidth=2.5, markersize=9)
        ax3.set_title('(c) Bilayer Resin', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Exposure Time (days)', fontsize=12)
        ax3.set_ylabel('')
        ax3.grid(True, alpha=0.3)
        ax3.legend().remove()
        
        plt.tight_layout()
        
        # Save
        output_file = output_dir / "fig_tensile_english.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Tensile Figure saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing Tensile data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_and_plot_tensile()
