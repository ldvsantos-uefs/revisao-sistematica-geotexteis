"""
Script para gerar dados simulados de FTIR de Syagrus coronata (Ouricuri)
baseados nas características espectrais conhecidas e na comparação com Typha domingensis.

Características principais do Ouricuri (do manuscrito):
- Banda em 1590 cm⁻¹ (lignina siringílica - mais proeminente)
- Redução da intensidade em 1730 cm⁻¹ (hemicelulose)
- Bandas típicas de lignocelulose em ~3300 cm⁻¹ (O-H), ~2920-2850 cm⁻¹ (C-H)
- Menor teor de hemicelulose comparado à Taboa
"""

import numpy as np
import pandas as pd

# Ler dados de Taboa como referência
taboa_data = pd.read_csv(
    r'c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\5-DADOS\FTIR_Taboa.csv',
    sep=';',
    skiprows=1,
    names=['wavenumber', 'transmittance'],
    decimal=','
)

# Converter para float
taboa_data['wavenumber'] = taboa_data['wavenumber'].astype(float)
taboa_data['transmittance'] = taboa_data['transmittance'].astype(float)

# Criar baseline para Ouricuri (similar à Taboa, mas com ajustes)
ouricuri_data = taboa_data.copy()

# Função para adicionar picos gaussianos
def gaussian_peak(x, center, amplitude, width):
    return amplitude * np.exp(-((x - center) ** 2) / (2 * width ** 2))

# Ajustar características espectrais do Ouricuri
wavenumber = ouricuri_data['wavenumber'].values
transmittance = ouricuri_data['transmittance'].values

# 1. REDUZIR intensidade do pico em 1730 cm⁻¹ (hemicelulose)
# Encontrar região próxima a 1730
mask_1730 = (wavenumber >= 1700) & (wavenumber <= 1760)
# Aumentar transmitância (= reduzir absorção) nessa região
transmittance[mask_1730] += 3.0

# 2. AUMENTAR intensidade do pico em 1590 cm⁻¹ (lignina siringílica)
# Reduzir transmitância (= aumentar absorção) em 1590
peak_1590 = gaussian_peak(wavenumber, 1590, -5.0, 15)
transmittance += peak_1590

# 3. Ajustar região de lignina aromática (1600-1500 cm⁻¹)
# Aumentar absorção geral nessa região
mask_aromatic = (wavenumber >= 1500) & (wavenumber <= 1600)
transmittance[mask_aromatic] -= 2.0

# 4. Manter bandas de O-H (~3300) e C-H (~2920-2850) similares
# (já presentes no baseline de Taboa)

# 5. Adicionar pequena variação de ruído para tornar mais realista
noise = np.random.normal(0, 0.15, len(transmittance))
transmittance += noise

# Garantir que transmitância esteja em faixa razoável (0-100%)
transmittance = np.clip(transmittance, 0, 100)

# Criar DataFrame final
ouricuri_final = pd.DataFrame({
    'wavenumber': wavenumber,
    'transmittance': transmittance
})

# Salvar arquivo CSV no formato compatível
output_path = r'c:\Users\vidal\OneDrive\Documentos\13 - CLONEGIT\revisao-sistematica\5-DADOS\FTIR_Ouricuri.csv'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('Criado como novo conjunto de dados;Syagrus coronata (Ouricuri) - Dados simulados baseados em características espectrais conhecidas\n')
    f.write('cm-1;%T\n')
    for i, row in ouricuri_final.iterrows():
        f.write(f'{row["wavenumber"]:.2f};{row["transmittance"]:.2f}\n')

print(f"✓ Arquivo FTIR_Ouricuri.csv criado com sucesso!")
print(f"✓ Total de pontos: {len(ouricuri_final)}")
print(f"\nCaracterísticas implementadas:")
print(f"  • Banda proeminente em ~1590 cm⁻¹ (lignina siringílica)")
print(f"  • Redução em ~1730 cm⁻¹ (menor hemicelulose)")
print(f"  • Região aromática 1500-1600 cm⁻¹ intensificada")
print(f"  • Bandas O-H e C-H preservadas")
