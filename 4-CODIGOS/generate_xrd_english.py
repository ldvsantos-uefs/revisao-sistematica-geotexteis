"""
X-Ray Diffraction (XRD) Analysis Plot
Typha domingensis vs Syagrus coronata
English Version

Author: Diego Vidal
Date: December 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def load_and_plot_xrd():
    # Paths
    data_path = Path("./5-DADOS/Planilha DRX (1).xlsx")
    output_dir = Path("./5-DADOS/MEV-ANALISE/resultados_en")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        return

    print("Loading XRD data...")
    try:
        # Load sheets
        df_taboa = pd.read_excel(data_path, sheet_name='TABOA', header=None)
        df_ouricuri = pd.read_excel(data_path, sheet_name='OURICURI', header=None)
        
        # Process data
        # Assuming Col 0 is 2Theta * 1000, Col 1 is Intensity
        # We need to normalize intensity for comparison
        
        # Taboa
        x_taboa = df_taboa[0] / 1000.0
        y_taboa = df_taboa[1]
        # Normalize to 0-1 or just offset? Usually normalized or offset.
        # Let's normalize to max intensity = 1 for better comparison
        y_taboa_norm = (y_taboa - y_taboa.min()) / (y_taboa.max() - y_taboa.min())
        
        # Ouricuri
        x_ouricuri = df_ouricuri[0] / 1000.0
        y_ouricuri = df_ouricuri[1]
        y_ouricuri_norm = (y_ouricuri - y_ouricuri.min()) / (y_ouricuri.max() - y_ouricuri.min())
        
        # Plot
        plt.figure(figsize=(10, 6))
        
        # Plot with offset for clarity
        plt.plot(x_ouricuri, y_ouricuri_norm + 1.2, label='Syagrus coronata (Licuri)', color='#D84315', linewidth=1.5)
        plt.plot(x_taboa, y_taboa_norm, label='Typha domingensis (Cattail)', color='#2E7D32', linewidth=1.5)
        
        # Annotations for Cellulose I peaks
        # 2theta approx 14.8, 16.4, 22.6
        peaks = [14.8, 16.4, 22.6]
        peak_labels = ['(1-10)', '(110)', '(200)']
        
        for peak, label in zip(peaks, peak_labels):
            plt.axvline(x=peak, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
            plt.text(peak, 2.3, label, ha='center', fontsize=9, color='#444444')

        plt.xlabel('2θ (degrees)', fontsize=12, fontweight='bold')
        plt.ylabel('Intensity (a.u.)', fontsize=12, fontweight='bold')
        plt.title('X-Ray Diffraction (XRD) Patterns', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10, loc='upper right')
        plt.grid(True, alpha=0.2)
        plt.xlim(5, 40) # Typical range for cellulose
        plt.ylim(-0.1, 2.5)
        
        # Remove y ticks as it's arbitrary units
        plt.yticks([])
        
        plt.tight_layout()
        
        # Save
        output_file = output_dir / "fig_drx_english.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"XRD Figure saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing XRD data: {e}")

if __name__ == "__main__":
    load_and_plot_xrd()
