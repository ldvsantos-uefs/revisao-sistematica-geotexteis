#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gerador de Figura FTIR para fibras de palmeira (Syagrus coronata - Ouricuri)
Baseado em dados de Oil Palm Mesocarp Fiber (MDPI article)
Data: Dezembro 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configurações globais
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300

def load_ftir_data(csv_path):
    """Carrega dados FTIR do arquivo CSV"""
    df = pd.read_csv(csv_path)
    return df

def create_ftir_figure(df, output_path):
    """Cria figura de espectro FTIR"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plotar espectro
    ax.plot(df['Wavenumber'], df['Transmittance'], 
            color='#2E86AB', linewidth=1.5, label='Syagrus coronata')
    
    # Adicionar anotações para picos principais
    annotations = [
        (3340, 75, '3340\nO-H', -20),
        (2852, 82, '2852\nC-H', -15),
        (1732, 88, '1732\nC=O', -15),
        (1590, 89, '1590\nSyringyl', -20),
        (1429, 87, '1429\nCH₂', -15),
        (1315, 88, '1315\nC-O', -15),
        (1234, 85, '1234\nC-O-C', -18),
        (1163, 84, '1163\nC-O', -15),
        (1035, 82, '1035\nC-O', -15),
        (896, 83, '896\nβ-glycosidic', -20)
    ]
    
    for wave, trans, label, offset in annotations:
        ax.annotate(label, 
                   xy=(wave, trans),
                   xytext=(wave, trans + offset),
                   fontsize=8,
                   ha='center',
                   arrowprops=dict(arrowstyle='->', lw=0.5, color='black'))
    
    # Configurações dos eixos
    ax.set_xlabel('Número de onda (cm⁻¹)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Transmitância (%)', fontsize=12, fontweight='bold')
    ax.set_title('Espectro FTIR - Fibra de Syagrus coronata (Ouricuri)', 
                fontsize=13, fontweight='bold', pad=15)
    
    # Inverter eixo x (4000 -> 400)
    ax.set_xlim(4000, 400)
    ax.invert_xaxis()
    
    # Limites do eixo y
    ax.set_ylim(70, 100)
    
    # Grade
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Legenda
    ax.legend(loc='lower left', fontsize=10, framealpha=0.9)
    
    # Layout
    plt.tight_layout()
    
    # Salvar
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figura salva em: {output_path}")
    
    # Mostrar
    plt.show()
    
    return fig

def main():
    """Função principal"""
    
    # Caminhos
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / '5-DADOS'
    output_dir = base_dir / '3-IMAGENS'
    
    csv_file = data_dir / 'FTIR_Ouricuri_Palm.csv'
    output_file = output_dir / 'figura_ftir_ouricuri.png'
    
    # Verificar se arquivo existe
    if not csv_file.exists():
        print(f"ERRO: Arquivo {csv_file} não encontrado!")
        return
    
    # Carregar dados
    print("Carregando dados FTIR...")
    df = load_ftir_data(csv_file)
    print(f"Dados carregados: {len(df)} pontos espectrais")
    
    # Criar figura
    print("Gerando figura FTIR...")
    fig = create_ftir_figure(df, output_file)
    
    print("\n=== Bandas FTIR principais identificadas ===")
    key_bands = df[df['Assignment'].str.contains('stretching|bending|glycosidic', case=False, na=False)]
    print(key_bands[['Wavenumber', 'Assignment', 'Description']].to_string(index=False))
    
    print("\n✓ Processamento concluído!")

if __name__ == "__main__":
    main()
