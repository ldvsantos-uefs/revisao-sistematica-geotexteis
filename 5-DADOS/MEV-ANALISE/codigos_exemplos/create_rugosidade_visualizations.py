#!/usr/bin/env python3
"""
Visualizações Melhoradas de Rugosidade Superficial
Cria representações claras e compreensíveis da rugosidade das fibras
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from skimage import filters
import os
from scipy import ndimage
import warnings
warnings.filterwarnings('ignore')

def load_images():
    """Carrega as duas imagens"""
    image_sem = cv2.imread("/home/ubuntu/fibra_sem_tratamento.tif", cv2.IMREAD_GRAYSCALE)
    image_sem_norm = image_sem.astype(np.float32) / 255.0
    
    image_com = cv2.imread("/home/ubuntu/taboa_analysis.tiff", cv2.IMREAD_GRAYSCALE)
    image_com_norm = image_com.astype(np.float32) / 255.0
    
    return image_sem, image_sem_norm, image_com, image_com_norm

def calculate_enhanced_roughness(image_normalized, method='local_std'):
    """Calcula rugosidade com diferentes métodos para melhor visualização"""
    
    if method == 'local_std':
        # Desvio padrão local
        kernel_size = 7
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size**2)
        local_mean = cv2.filter2D(image_normalized, -1, kernel)
        local_variance = cv2.filter2D((image_normalized - local_mean)**2, -1, kernel)
        roughness = np.sqrt(local_variance)
        
    elif method == 'gradient_magnitude':
        # Magnitude do gradiente
        grad_x = filters.sobel_h(image_normalized)
        grad_y = filters.sobel_v(image_normalized)
        roughness = np.sqrt(grad_x**2 + grad_y**2)
        
    elif method == 'laplacian':
        # Laplaciano (segunda derivada)
        roughness = np.abs(filters.laplace(image_normalized))
        
    elif method == 'range_filter':
        # Filtro de range (max - min local)
        kernel_size = 5
        kernel = np.ones((kernel_size, kernel_size))
        local_max = ndimage.maximum_filter(image_normalized, size=kernel_size)
        local_min = ndimage.minimum_filter(image_normalized, size=kernel_size)
        roughness = local_max - local_min
        
    return roughness

def create_custom_colormap():
    """Cria colormap personalizado para rugosidade"""
    colors = ['#000080', '#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF8000', '#FF0000', '#800000']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('rugosidade', colors, N=n_bins)
    return cmap

def create_rugosidade_visualizations():
    """Cria visualizações melhoradas de rugosidade"""
    
    # Criar diretório
    output_dir = "/home/ubuntu/rugosidade_visualizations"
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar imagens
    image_sem, image_sem_norm, image_com, image_com_norm = load_images()
    
    # Colormap personalizado
    rugosidade_cmap = create_custom_colormap()
    
    # Métodos de análise de rugosidade
    methods = {
        'local_std': 'Desvio Padrão Local',
        'gradient_magnitude': 'Magnitude do Gradiente',
        'laplacian': 'Laplaciano',
        'range_filter': 'Filtro de Range'
    }
    
    for method_key, method_name in methods.items():
        
        # Calcular rugosidade para ambas as imagens
        rugosidade_sem = calculate_enhanced_roughness(image_sem_norm, method_key)
        rugosidade_com = calculate_enhanced_roughness(image_com_norm, method_key)
        
        # Normalizar para mesma escala
        vmin = min(rugosidade_sem.min(), rugosidade_com.min())
        vmax = max(rugosidade_sem.max(), rugosidade_com.max())
        
        # Criar visualização comparativa
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Análise de Rugosidade: {method_name}', fontsize=18, fontweight='bold')
        
        # Imagens originais
        ax1.imshow(image_sem, cmap='gray')
        ax1.set_title('Fibra SEM Tratamento\n(Original)', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        ax2.imshow(image_com, cmap='gray')
        ax2.set_title('Fibra COM Tratamento\n(Original)', fontsize=14, fontweight='bold')
        ax2.axis('off')
        
        # Mapas de rugosidade
        im1 = ax3.imshow(rugosidade_sem, cmap=rugosidade_cmap, vmin=vmin, vmax=vmax)
        ax3.set_title(f'Rugosidade - SEM Tratamento\n(Média: {rugosidade_sem.mean():.4f})', fontsize=14, fontweight='bold')
        ax3.axis('off')
        
        im2 = ax4.imshow(rugosidade_com, cmap=rugosidade_cmap, vmin=vmin, vmax=vmax)
        ax4.set_title(f'Rugosidade - COM Tratamento\n(Média: {rugosidade_com.mean():.4f})', fontsize=14, fontweight='bold')
        ax4.axis('off')
        
        # Colorbar
        cbar = fig.colorbar(im1, ax=[ax3, ax4], shrink=0.8, aspect=30)
        cbar.set_label('Intensidade de Rugosidade', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/rugosidade_{method_key}.png", dpi=300, bbox_inches='tight')
        plt.savefig(f"{output_dir}/rugosidade_{method_key}.svg", bbox_inches='tight')
        plt.close()
    
    # Criar visualização 3D da rugosidade
    create_3d_roughness_visualization(image_sem_norm, image_com_norm, output_dir)
    
    # Criar perfis de rugosidade
    create_roughness_profiles(image_sem_norm, image_com_norm, output_dir)
    
    # Criar histogramas de rugosidade
    create_roughness_histograms(image_sem_norm, image_com_norm, output_dir)
    
    print(f"✓ Visualizações de rugosidade criadas")
    print(f"📁 Diretório: {output_dir}")
    
    return output_dir

def create_3d_roughness_visualization(image_sem_norm, image_com_norm, output_dir):
    """Cria visualização 3D da rugosidade"""
    from mpl_toolkits.mplot3d import Axes3D
    
    # Calcular rugosidade
    rugosidade_sem = calculate_enhanced_roughness(image_sem_norm, 'local_std')
    rugosidade_com = calculate_enhanced_roughness(image_com_norm, 'local_std')
    
    # Reduzir resolução para visualização 3D
    step = 20
    rugosidade_sem_small = rugosidade_sem[::step, ::step]
    rugosidade_com_small = rugosidade_com[::step, ::step]
    
    # Criar coordenadas
    y_sem, x_sem = np.mgrid[0:rugosidade_sem_small.shape[0], 0:rugosidade_sem_small.shape[1]]
    y_com, x_com = np.mgrid[0:rugosidade_com_small.shape[0], 0:rugosidade_com_small.shape[1]]
    
    # Visualização 3D
    fig = plt.figure(figsize=(16, 8))
    
    # SEM tratamento
    ax1 = fig.add_subplot(121, projection='3d')
    surf1 = ax1.plot_surface(x_sem, y_sem, rugosidade_sem_small, 
                            cmap='viridis', alpha=0.8, linewidth=0, antialiased=True)
    ax1.set_title('Rugosidade 3D - SEM Tratamento', fontsize=14, fontweight='bold')
    ax1.set_xlabel('X (pixels)')
    ax1.set_ylabel('Y (pixels)')
    ax1.set_zlabel('Rugosidade')
    
    # COM tratamento
    ax2 = fig.add_subplot(122, projection='3d')
    surf2 = ax2.plot_surface(x_com, y_com, rugosidade_com_small, 
                            cmap='viridis', alpha=0.8, linewidth=0, antialiased=True)
    ax2.set_title('Rugosidade 3D - COM Tratamento', fontsize=14, fontweight='bold')
    ax2.set_xlabel('X (pixels)')
    ax2.set_ylabel('Y (pixels)')
    ax2.set_zlabel('Rugosidade')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/rugosidade_3d.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/rugosidade_3d.svg", bbox_inches='tight')
    plt.close()

def create_roughness_profiles(image_sem_norm, image_com_norm, output_dir):
    """Cria perfis de rugosidade ao longo de linhas"""
    
    rugosidade_sem = calculate_enhanced_roughness(image_sem_norm, 'local_std')
    rugosidade_com = calculate_enhanced_roughness(image_com_norm, 'local_std')
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Perfis de Rugosidade', fontsize=18, fontweight='bold')
    
    # Perfil horizontal (linha central)
    center_row_sem = rugosidade_sem.shape[0] // 2
    center_row_com = rugosidade_com.shape[0] // 2
    
    profile_h_sem = rugosidade_sem[center_row_sem, :]
    profile_h_com = rugosidade_com[center_row_com, :]
    
    ax1.plot(profile_h_sem, 'b-', linewidth=2, label='SEM Tratamento')
    ax1.plot(profile_h_com, 'r-', linewidth=2, label='COM Tratamento')
    ax1.set_title('Perfil Horizontal (Linha Central)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Posição (pixels)')
    ax1.set_ylabel('Rugosidade')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Perfil vertical (coluna central)
    center_col_sem = rugosidade_sem.shape[1] // 2
    center_col_com = rugosidade_com.shape[1] // 2
    
    profile_v_sem = rugosidade_sem[:, center_col_sem]
    profile_v_com = rugosidade_com[:, center_col_com]
    
    ax2.plot(profile_v_sem, 'b-', linewidth=2, label='SEM Tratamento')
    ax2.plot(profile_v_com, 'r-', linewidth=2, label='COM Tratamento')
    ax2.set_title('Perfil Vertical (Coluna Central)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Posição (pixels)')
    ax2.set_ylabel('Rugosidade')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Mostrar onde os perfis foram extraídos
    ax3.imshow(rugosidade_sem, cmap='viridis')
    ax3.axhline(y=center_row_sem, color='red', linewidth=2, alpha=0.7)
    ax3.axvline(x=center_col_sem, color='red', linewidth=2, alpha=0.7)
    ax3.set_title('SEM Tratamento - Linhas de Perfil', fontsize=14, fontweight='bold')
    ax3.axis('off')
    
    ax4.imshow(rugosidade_com, cmap='viridis')
    ax4.axhline(y=center_row_com, color='red', linewidth=2, alpha=0.7)
    ax4.axvline(x=center_col_com, color='red', linewidth=2, alpha=0.7)
    ax4.set_title('COM Tratamento - Linhas de Perfil', fontsize=14, fontweight='bold')
    ax4.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/perfis_rugosidade.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/perfis_rugosidade.svg", bbox_inches='tight')
    plt.close()

def create_roughness_histograms(image_sem_norm, image_com_norm, output_dir):
    """Cria histogramas de distribuição de rugosidade"""
    
    rugosidade_sem = calculate_enhanced_roughness(image_sem_norm, 'local_std')
    rugosidade_com = calculate_enhanced_roughness(image_com_norm, 'local_std')
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Distribuição de Rugosidade Superficial', fontsize=18, fontweight='bold')
    
    # Histograma SEM tratamento
    ax1.hist(rugosidade_sem.flatten(), bins=50, alpha=0.7, color='lightcoral', 
             edgecolor='black', density=True, label='SEM Tratamento')
    ax1.axvline(rugosidade_sem.mean(), color='red', linestyle='--', linewidth=2, 
                label=f'Média: {rugosidade_sem.mean():.4f}')
    ax1.set_title('SEM Tratamento', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Rugosidade')
    ax1.set_ylabel('Densidade')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Histograma COM tratamento
    ax2.hist(rugosidade_com.flatten(), bins=50, alpha=0.7, color='lightblue', 
             edgecolor='black', density=True, label='COM Tratamento')
    ax2.axvline(rugosidade_com.mean(), color='blue', linestyle='--', linewidth=2, 
                label=f'Média: {rugosidade_com.mean():.4f}')
    ax2.set_title('COM Tratamento', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Rugosidade')
    ax2.set_ylabel('Densidade')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Histograma comparativo
    ax3.hist(rugosidade_sem.flatten(), bins=50, alpha=0.6, color='lightcoral', 
             edgecolor='red', density=True, label='SEM Tratamento')
    ax3.hist(rugosidade_com.flatten(), bins=50, alpha=0.6, color='lightblue', 
             edgecolor='blue', density=True, label='COM Tratamento')
    ax3.axvline(rugosidade_sem.mean(), color='red', linestyle='--', linewidth=2)
    ax3.axvline(rugosidade_com.mean(), color='blue', linestyle='--', linewidth=2)
    ax3.set_title('Comparação', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Rugosidade')
    ax3.set_ylabel('Densidade')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/histogramas_rugosidade.png", dpi=300, bbox_inches='tight')
    plt.savefig(f"{output_dir}/histogramas_rugosidade.svg", bbox_inches='tight')
    plt.close()

def main():
    print("Criando Visualizações Melhoradas de Rugosidade")
    print("=" * 60)
    
    output_dir = create_rugosidade_visualizations()
    
    # Listar arquivos criados
    files = sorted(os.listdir(output_dir))
    print(f"\n📋 Arquivos criados:")
    for file in files:
        print(f"  • {file}")

if __name__ == "__main__":
    main()
