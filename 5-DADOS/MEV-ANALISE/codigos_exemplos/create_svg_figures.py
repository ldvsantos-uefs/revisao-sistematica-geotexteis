#!/usr/bin/env python3
"""
Gerador de Figuras Comparativas em SVG
Cria versões editáveis das análises comparativas de fibras
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle
from skimage import filters, measure, morphology, segmentation, feature
from skimage.measure import regionprops
from skimage.morphology import skeletonize
from skimage.feature import graycomatrix, graycoprops
import os
import json
from datetime import datetime
from scipy import ndimage
import warnings
warnings.filterwarnings('ignore')

def load_and_process_images():
    """Carrega e processa as duas imagens"""
    # Fibra sem tratamento
    image_sem = cv2.imread("/home/ubuntu/fibra_sem_tratamento.tif", cv2.IMREAD_GRAYSCALE)
    image_sem_norm = image_sem.astype(np.float32) / 255.0
    
    # Fibra com tratamento
    image_com = cv2.imread("/home/ubuntu/taboa_analysis.tiff", cv2.IMREAD_GRAYSCALE)
    image_com_norm = image_com.astype(np.float32) / 255.0
    
    return image_sem, image_sem_norm, image_com, image_com_norm

def analyze_orientation(image_normalized):
    """Analisa orientação das fibras"""
    blurred = filters.gaussian(image_normalized, sigma=1.0)
    grad_x = filters.sobel_h(blurred)
    grad_y = filters.sobel_v(blurred)
    angles = np.arctan2(grad_y, grad_x)
    magnitudes = np.sqrt(grad_x**2 + grad_y**2)
    return angles, magnitudes

def detect_pores(image, image_normalized):
    """Detecta poros"""
    blurred = filters.gaussian(image_normalized, sigma=2.0)
    threshold = filters.threshold_otsu(blurred)
    pores = blurred < (threshold * 0.7)
    pores_cleaned = morphology.remove_small_objects(pores, min_size=20)
    pores_cleaned = morphology.remove_small_holes(pores_cleaned, area_threshold=10)
    return pores_cleaned

def create_skeleton(image_normalized):
    """Cria esqueleto das fibrilas"""
    blurred = filters.gaussian(image_normalized, sigma=1.0)
    kernel_h = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32)
    horizontal_lines = cv2.filter2D(blurred, -1, kernel_h)
    kernel_v = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32)
    vertical_lines = cv2.filter2D(blurred, -1, kernel_v)
    linear_features = np.maximum(horizontal_lines, vertical_lines)
    linear_threshold = filters.threshold_otsu(linear_features)
    linear_mask = linear_features > linear_threshold
    skeleton = skeletonize(linear_mask)
    return skeleton

def detect_junctions(image_normalized):
    """Detecta junções"""
    corners = feature.corner_harris(image_normalized, method='eps', sigma=2)
    corner_coords = feature.corner_peaks(corners, min_distance=10, threshold_abs=0.01*corners.max())
    return corner_coords

def create_individual_svg_figures():
    """Cria figuras individuais em SVG"""
    
    # Criar diretório
    output_dir = "/home/ubuntu/figuras_svg_comparativas"
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar imagens
    image_sem, image_sem_norm, image_com, image_com_norm = load_and_process_images()
    
    # Processar análises
    angles_sem, magnitudes_sem = analyze_orientation(image_sem_norm)
    angles_com, magnitudes_com = analyze_orientation(image_com_norm)
    
    pores_sem = detect_pores(image_sem, image_sem_norm)
    pores_com = detect_pores(image_com, image_com_norm)
    
    skeleton_sem = create_skeleton(image_sem_norm)
    skeleton_com = create_skeleton(image_com_norm)
    
    corner_coords_sem = detect_junctions(image_sem_norm)
    corner_coords_com = detect_junctions(image_com_norm)
    
    # Configurar estilo para SVG
    plt.style.use('default')
    
    # 1. Comparação de Imagens Originais
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Comparação: Fibras de Taboa Sem vs. Com Tratamento', fontsize=16, fontweight='bold')
    
    ax1.imshow(image_sem, cmap='gray')
    ax1.set_title('Fibra SEM Tratamento\n(T3-1.2Kx)', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    ax2.imshow(image_com, cmap='gray')
    ax2.set_title('Fibra COM Tratamento\n(1.05Kx)', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/01_comparacao_imagens_originais.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/01_comparacao_imagens_originais.svg", bbox_inches='tight')
    plt.close()
    
    # 2. Comparação de Mapas de Orientação
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Comparação: Mapas de Orientação das Fibras', fontsize=16, fontweight='bold')
    
    orientation_sem = np.degrees(angles_sem) % 180
    orientation_com = np.degrees(angles_com) % 180
    
    im1 = ax1.imshow(orientation_sem, cmap='hsv', vmin=0, vmax=180)
    ax1.set_title('SEM Tratamento\n(Índice: 0.290)', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    im2 = ax2.imshow(orientation_com, cmap='hsv', vmin=0, vmax=180)
    ax2.set_title('COM Tratamento\n(Índice: 0.463)', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    # Colorbar compartilhada
    cbar = fig.colorbar(im1, ax=[ax1, ax2], shrink=0.8, aspect=30)
    cbar.set_label('Ângulo (graus)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/02_comparacao_orientacao.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/02_comparacao_orientacao.svg", bbox_inches='tight')
    plt.close()
    
    # 3. Comparação de Detecção de Poros
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Comparação: Detecção de Poros', fontsize=16, fontweight='bold')
    
    ax1.imshow(image_sem, cmap='gray', alpha=0.7)
    ax1.imshow(pores_sem, cmap='Reds', alpha=0.6)
    ax1.set_title('SEM Tratamento\n(140 poros, 29.83%)', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    ax2.imshow(image_com, cmap='gray', alpha=0.7)
    ax2.imshow(pores_com, cmap='Reds', alpha=0.6)
    ax2.set_title('COM Tratamento\n(81 poros, 32.10%)', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/03_comparacao_poros.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/03_comparacao_poros.svg", bbox_inches='tight')
    plt.close()
    
    # 4. Comparação de Esqueletos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Comparação: Esqueleto das Fibrilas', fontsize=16, fontweight='bold')
    
    ax1.imshow(image_sem, cmap='gray', alpha=0.8)
    ax1.imshow(skeleton_sem, cmap='Reds', alpha=0.8)
    ax1.set_title('SEM Tratamento\n(26.534 pixels)', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    ax2.imshow(image_com, cmap='gray', alpha=0.8)
    ax2.imshow(skeleton_com, cmap='Reds', alpha=0.8)
    ax2.set_title('COM Tratamento\n(32.458 pixels)', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/04_comparacao_esqueletos.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/04_comparacao_esqueletos.svg", bbox_inches='tight')
    plt.close()
    
    # 5. Comparação de Junções
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Comparação: Junções e Ramificações', fontsize=16, fontweight='bold')
    
    ax1.imshow(image_sem, cmap='gray')
    if len(corner_coords_sem) > 0:
        ax1.plot(corner_coords_sem[:, 1], corner_coords_sem[:, 0], 'ro', markersize=2, alpha=0.8)
    ax1.set_title(f'SEM Tratamento\n({len(corner_coords_sem)} junções)', fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    ax2.imshow(image_com, cmap='gray')
    if len(corner_coords_com) > 0:
        ax2.plot(corner_coords_com[:, 1], corner_coords_com[:, 0], 'ro', markersize=2, alpha=0.8)
    ax2.set_title(f'COM Tratamento\n({len(corner_coords_com)} junções)', fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/05_comparacao_juncoes.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/05_comparacao_juncoes.svg", bbox_inches='tight')
    plt.close()
    
    # 6. Gráficos Quantitativos Comparativos
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Análise Quantitativa Comparativa', fontsize=16, fontweight='bold')
    
    # Porosidade
    categories = ['SEM Tratamento', 'COM Tratamento']
    porosities = [29.83, 32.10]
    bars1 = ax1.bar(categories, porosities, color=['lightcoral', 'lightblue'], alpha=0.7, edgecolor='black')
    ax1.set_title('Porosidade (%)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Porosidade (%)', fontsize=12)
    for i, v in enumerate(porosities):
        ax1.text(i, v + 0.5, f'{v:.1f}%', ha='center', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Número de poros
    num_pores = [140, 81]
    bars2 = ax2.bar(categories, num_pores, color=['lightcoral', 'lightblue'], alpha=0.7, edgecolor='black')
    ax2.set_title('Número de Poros', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Número de Poros', fontsize=12)
    for i, v in enumerate(num_pores):
        ax2.text(i, v + 2, f'{v}', ha='center', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Rugosidade
    roughness = [0.0353, 0.0523]
    bars3 = ax3.bar(categories, roughness, color=['lightcoral', 'lightblue'], alpha=0.7, edgecolor='black')
    ax3.set_title('Rugosidade Superficial', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Rugosidade', fontsize=12)
    for i, v in enumerate(roughness):
        ax3.text(i, v + 0.001, f'{v:.4f}', ha='center', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Número de junções
    junctions = [666, 831]
    bars4 = ax4.bar(categories, junctions, color=['lightcoral', 'lightblue'], alpha=0.7, edgecolor='black')
    ax4.set_title('Número de Junções', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Junções', fontsize=12)
    for i, v in enumerate(junctions):
        ax4.text(i, v + 10, f'{v}', ha='center', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/06_graficos_quantitativos.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/06_graficos_quantitativos.svg", bbox_inches='tight')
    plt.close()
    
    # 7. Tabela Resumo
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.suptitle('Tabela Comparativa: Parâmetros Morfológicos', fontsize=16, fontweight='bold')
    
    # Dados da tabela
    data = [
        ['Porosidade (%)', '29.83', '32.10', '+7.6%'],
        ['Número de Poros', '140', '81', '-42.1%'],
        ['Área Média dos Poros (pixels)', '1.935', '3.360', '+73.6%'],
        ['Rugosidade Superficial', '0.0353', '0.0523', '+48.2%'],
        ['Número de Junções', '666', '831', '+24.8%'],
        ['Índice de Orientação', '0.290', '0.463', '+59.7%'],
        ['Densidade Fibrilar', '0.0292', '0.0383', '+31.1%'],
        ['Comprimento Esqueletal (pixels)', '26.534', '32.458', '+22.3%']
    ]
    
    headers = ['Parâmetro', 'SEM Tratamento', 'COM Tratamento', 'Variação']
    
    # Criar tabela
    table = ax.table(cellText=data, colLabels=headers, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2)
    
    # Estilizar tabela
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(data) + 1):
        for j in range(len(headers)):
            if j == 3:  # Coluna de variação
                if '+' in data[i-1][j]:
                    table[(i, j)].set_facecolor('#E8F5E8')
                else:
                    table[(i, j)].set_facecolor('#FFE8E8')
            else:
                table[(i, j)].set_facecolor('#F5F5F5')
    
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/07_tabela_comparativa.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/07_tabela_comparativa.svg", bbox_inches='tight')
    plt.close()
    
    print(f"✓ 7 figuras comparativas criadas em PNG e SVG")
    print(f"📁 Diretório: {output_dir}")
    
    return output_dir

def create_zip_file(output_dir):
    """Cria arquivo ZIP com todas as figuras"""
    import zipfile
    
    zip_path = "/home/ubuntu/figuras_svg_comparativas.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    
    print(f"📦 Arquivo ZIP criado: {zip_path}")
    return zip_path

def main():
    print("Criando Figuras Comparativas em SVG")
    print("=" * 50)
    
    output_dir = create_individual_svg_figures()
    zip_path = create_zip_file(output_dir)
    
    # Listar arquivos criados
    files = sorted(os.listdir(output_dir))
    print(f"\n📋 Arquivos criados:")
    for file in files:
        print(f"  • {file}")

if __name__ == "__main__":
    main()
