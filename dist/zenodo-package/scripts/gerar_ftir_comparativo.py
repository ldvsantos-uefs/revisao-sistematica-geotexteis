"""
Script para gerar figura comparativa de FTIR entre Typha domingensis e Syagrus coronata
Baseado nos dados reais extraídos dos artigos
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configurações de estilo
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.2

def load_taboa_data(csv_path):
    """Carrega dados de FTIR da Taboa"""
    data = pd.read_csv(
        csv_path,
        sep=';',
        skiprows=1,  # Pular linha de cabeçalho
        decimal=','
    )
    # Renomear colunas
    data.columns = ['wavenumber', 'transmittance']
    # Remover NaN e linhas inválidas
    data = data.dropna()
    # Garantir que são números
    data['wavenumber'] = pd.to_numeric(data['wavenumber'], errors='coerce')
    data['transmittance'] = pd.to_numeric(data['transmittance'], errors='coerce')
    data = data.dropna()
    return data

def load_palm_data(csv_path):
    """Carrega dados de FTIR do Palm/Ouricuri"""
    data = pd.read_csv(csv_path)
    # Renomear colunas se necessário
    if 'Wavenumber' in data.columns:
        data.rename(columns={'Wavenumber': 'wavenumber', 'Transmittance': 'transmittance'}, inplace=True)
    return data

def create_comparative_figure(taboa_df, palm_df, output_path):
    """Cria figura comparativa com dois espectros sobrepostos"""
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plotar espectro da Taboa
    ax.plot(taboa_df['wavenumber'], taboa_df['transmittance'], 
            color='#1B998B', linewidth=1.5, label='Typha domingensis', alpha=0.85)
    
    # Plotar espectro do Ouricuri (com offset vertical para melhor visualização)
    offset = -15  # Deslocamento vertical
    ax.plot(palm_df['wavenumber'], palm_df['transmittance'] + offset, 
            color='#C44536', linewidth=1.5, label='Syagrus coronata', alpha=0.85)
    
    # Anotações principais - Typha (parte superior)
    typha_annotations = [
        (3300, None, '3300\nO-H'),
        (2920, None, '2920\nC-H'),
        (1735, None, '1735\nC=O'),
        (1600, None, '1600\nAromático'),
        (1035, None, '1035\nC-O'),
    ]
    
    # Anotações principais - Ouricuri (parte inferior)
    ouricuri_annotations = [
        (3340, None, '3340\nO-H'),
        (2852, None, '2852\nC-H'),
        (1732, None, '1732\nC=O↓'),
        (1590, None, '1590\nSyringyl'),
        (1234, None, '1234\nLignina'),
        (896, None, '896\nβ-glyc'),
    ]
    
    # Adicionar anotações para Typha
    for wave, _, label in typha_annotations:
        # Encontrar transmitância aproximada
        idx = (taboa_df['wavenumber'] - wave).abs().idxmin()
        trans = taboa_df.loc[idx, 'transmittance']
        ax.annotate(label, 
                   xy=(wave, trans),
                   xytext=(wave, trans + 8),
                   fontsize=8,
                   ha='center',
                   color='#1B998B',
                   weight='bold',
                   arrowprops=dict(arrowstyle='->', lw=0.8, color='#1B998B'))
    
    # Adicionar anotações para Ouricuri
    for wave, _, label in ouricuri_annotations:
        # Encontrar transmitância aproximada no palm data
        idx = (palm_df['wavenumber'] - wave).abs().idxmin()
        trans = palm_df.loc[idx, 'transmittance'] + offset
        ax.annotate(label, 
                   xy=(wave, trans),
                   xytext=(wave, trans - 8),
                   fontsize=8,
                   ha='center',
                   color='#C44536',
                   weight='bold',
                   arrowprops=dict(arrowstyle='->', lw=0.8, color='#C44536'))
    
    # Destacar diferenças principais com áreas sombreadas
    # Região de hemicelulose (1730 cm⁻¹)
    ax.axvspan(1700, 1760, alpha=0.1, color='orange', label='Região C=O (hemicelulose)')
    
    # Região de lignina siringílica (1590 cm⁻¹)
    ax.axvspan(1570, 1610, alpha=0.1, color='purple', label='Região syringyl (Ouricuri)')
    
    # Configurações dos eixos
    ax.set_xlabel('Número de onda (cm$^{-1}$)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Transmitância (%)', fontsize=13, fontweight='bold')
    
    # Inverter eixo x (4000 -> 400)
    ax.set_xlim(4000, 400)
    ax.invert_xaxis()
    
    # Ajustar limites do eixo y para acomodar ambos os espectros
    ax.set_ylim(40, 90)
    
    # Grade
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Legenda com melhor posicionamento
    ax.legend(loc='upper right', fontsize=10, framealpha=0.95, 
              edgecolor='black', fancybox=True, shadow=True)
    
    # Layout
    plt.tight_layout()
    
    # Salvar figura
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Figura comparativa salva em: {output_path}")
    
    # Salvar também versão para manuscrito (sem offset)
    output_path_manuscript = output_path.parent / 'figura_ftir_comparativa_manuscrito.png'
    
    # Criar segunda figura sem offset (espectros sobrepostos diretos)
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    
    ax2.plot(taboa_df['wavenumber'], taboa_df['transmittance'], 
            color='#1B998B', linewidth=1.8, label='Typha domingensis', alpha=0.9)
    ax2.plot(palm_df['wavenumber'], palm_df['transmittance'], 
            color='#C44536', linewidth=1.8, label='Syagrus coronata', alpha=0.9, linestyle='--')
    
    ax2.set_xlabel('Número de onda (cm$^{-1}$)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Transmitância (%)', fontsize=13, fontweight='bold')
    
    ax2.set_xlim(4000, 400)
    ax2.invert_xaxis()
    ax2.set_ylim(60, 95)
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax2.legend(loc='lower left', fontsize=11, framealpha=0.95)
    
    plt.tight_layout()
    plt.savefig(output_path_manuscript, dpi=300, bbox_inches='tight')
    print(f"✓ Figura manuscrito salva em: {output_path_manuscript}")
    
    # Mostrar
    plt.show()
    
    return fig, fig2

def main():
    """Função principal"""
    
    # Caminhos
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / '5-DADOS'
    output_dir = base_dir / '3-IMAGENS'
    
    taboa_file = data_dir / 'FTIR_Taboa.csv'
    palm_file = data_dir / 'FTIR_Ouricuri_Palm.csv'
    output_file = output_dir / 'figura_ftir_comparativa.png'
    
    # Verificar arquivos
    if not taboa_file.exists():
        print(f"ERRO: {taboa_file} não encontrado!")
        return
    if not palm_file.exists():
        print(f"ERRO: {palm_file} não encontrado!")
        return
    
    # Carregar dados
    print("Carregando dados de FTIR...")
    taboa_data = load_taboa_data(taboa_file)
    palm_data = load_palm_data(palm_file)
    
    print(f"✓ Typha: {len(taboa_data)} pontos espectrais")
    print(f"✓ Ouricuri: {len(palm_data)} pontos espectrais")
    
    # Criar figuras
    print("\nGerando figuras comparativas...")
    fig1, fig2 = create_comparative_figure(taboa_data, palm_data, output_file)
    
    print("\n" + "="*60)
    print("RESUMO - Bandas FTIR características")
    print("="*60)
    print("\nTypha domingensis:")
    print("  • 3300 cm⁻¹ - O-H stretching (hidroxilas)")
    print("  • 2920 cm⁻¹ - C-H stretching (alifáticos)")
    print("  • 1735 cm⁻¹ - C=O stretching (hemicelulose - ALTA)")
    print("  • 1600 cm⁻¹ - Aromáticos (lignina)")
    print("  • 1035 cm⁻¹ - C-O stretching (celulose)")
    
    print("\nSyagrus coronata (Ouricuri):")
    print("  • 3340 cm⁻¹ - O-H stretching (hidroxilas)")
    print("  • 2852 cm⁻¹ - C-H stretching (alifáticos)")
    print("  • 1732 cm⁻¹ - C=O stretching (hemicelulose - REDUZIDA)")
    print("  • 1590 cm⁻¹ - Lignina siringílica (CARACTERÍSTICA)")
    print("  • 1234 cm⁻¹ - C-O-C anel siringil (lignina)")
    print("  • 896 cm⁻¹ - β-glicosídica (celulose)")
    
    print("\n" + "="*60)
    print("✓ Processamento concluído!")
    print("✓ Figuras prontas para uso no manuscrito")
    print("="*60)

if __name__ == "__main__":
    main()
