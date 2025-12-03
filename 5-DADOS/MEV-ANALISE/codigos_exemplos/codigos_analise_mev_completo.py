#!/usr/bin/env python3
"""
CÓDIGOS COMPLETOS PARA ANÁLISE DE IMAGENS MEV
Análise Quantitativa de Fibras de Typha domingensis

Autor: Manus AI
Data: Outubro 2025
Descrição: Conjunto completo de códigos para análise morfológica quantitativa
           de fibras naturais por microscopia eletrônica de varredura

DEPENDÊNCIAS NECESSÁRIAS:
pip install opencv-python scikit-image matplotlib numpy scipy

ESTRUTURA:
1. Análise Individual de Fibras
2. Análise Comparativa
3. Visualizações de Rugosidade
4. Criação de Figuras SVG
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle
from matplotlib.colors import LinearSegmentedColormap
from skimage import filters, measure, morphology, segmentation, feature
from skimage.measure import regionprops
from skimage.morphology import skeletonize
from skimage.feature import graycomatrix, graycoprops
import os
import json
from datetime import datetime
from scipy import ndimage
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CLASSE PRINCIPAL PARA ANÁLISE DE FIBRAS
# ============================================================================

class FiberAnalyzer:
    """
    Analisador principal para fibras de taboa
    Implementa todos os métodos de análise morfológica quantitativa
    """
    
    def __init__(self):
        self.results = {}
        
    def load_and_process_image(self, image_path):
        """
        Carrega e pré-processa imagem MEV
        
        Args:
            image_path (str): Caminho para a imagem
            
        Returns:
            tuple: (imagem_original, imagem_normalizada)
        """
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Normalização para [0,1]
        image_normalized = image.astype(np.float32) / 255.0
        return image, image_normalized
    
    def analyze_fiber_orientation(self, image_normalized):
        """
        Analisa orientação das fibras usando gradientes de Sobel
        
        Args:
            image_normalized (np.array): Imagem normalizada
            
        Returns:
            tuple: (resultados_orientacao, angulos, magnitudes)
        """
        # Suavização gaussiana
        blurred = filters.gaussian(image_normalized, sigma=1.0)
        
        # Cálculo de gradientes
        grad_x = filters.sobel_h(blurred)
        grad_y = filters.sobel_v(blurred)
        
        # Ângulos e magnitudes
        angles = np.arctan2(grad_y, grad_x)
        magnitudes = np.sqrt(grad_x**2 + grad_y**2)
        
        # Análise apenas de gradientes significativos
        threshold = np.percentile(magnitudes, 75)
        significant_angles = angles[magnitudes > threshold]
        angles_deg = np.degrees(significant_angles) % 180
        
        # Cálculo de parâmetros
        mean_angle = float(np.mean(angles_deg))
        std_angle = float(np.std(angles_deg))
        orientation_index = 1.0 - (std_angle / 90.0) if std_angle <= 90 else 0.0
        
        results = {
            'mean_fiber_angle': mean_angle,
            'angle_std_deviation': std_angle,
            'orientation_index': float(orientation_index),
            'predominant_direction': self._classify_direction(mean_angle)
        }
        
        return results, angles, magnitudes
    
    def _classify_direction(self, angle):
        """Classifica direção predominante das fibras"""
        if 0 <= angle < 22.5 or 157.5 <= angle < 180:
            return "Horizontal"
        elif 22.5 <= angle < 67.5:
            return "Diagonal (NE-SW)"
        elif 67.5 <= angle < 112.5:
            return "Vertical"
        elif 112.5 <= angle < 157.5:
            return "Diagonal (NW-SE)"
        else:
            return "Indefinida"
    
    def analyze_surface_features(self, image, image_normalized):
        """
        Analisa características superficiais (poros, porosidade)
        
        Args:
            image (np.array): Imagem original
            image_normalized (np.array): Imagem normalizada
            
        Returns:
            tuple: (resultados_superficie, poros_binarios, regioes_poros)
        """
        # Suavização e limiarização
        blurred = filters.gaussian(image_normalized, sigma=2.0)
        threshold = filters.threshold_otsu(blurred)
        pores = blurred < (threshold * 0.7)  # Ajuste para detectar poros
        
        # Limpeza morfológica
        pores_cleaned = morphology.remove_small_objects(pores, min_size=20)
        pores_cleaned = morphology.remove_small_holes(pores_cleaned, area_threshold=10)
        
        # Análise de regiões
        labeled_pores = measure.label(pores_cleaned)
        pore_regions = measure.regionprops(labeled_pores)
        
        # Cálculo de parâmetros dos poros
        pore_areas = [region.area for region in pore_regions]
        pore_circularities = []
        pore_aspect_ratios = []
        
        for region in pore_regions:
            if region.area > 10:
                # Circularidade: 4πA/P²
                circularity = 4 * np.pi * region.area / (region.perimeter ** 2)
                pore_circularities.append(circularity)
                
                # Razão de aspecto
                minr, minc, maxr, maxc = region.bbox
                aspect_ratio = (maxr - minr) / (maxc - minc) if (maxc - minc) > 0 else 1
                pore_aspect_ratios.append(aspect_ratio)
        
        # Cálculo de porosidade
        total_area = image_normalized.shape[0] * image_normalized.shape[1]
        pore_area_total = np.sum(pore_areas)
        porosity = (pore_area_total / total_area) * 100
        
        results = {
            'num_pores': len(pore_areas),
            'porosity_percentage': float(porosity),
            'mean_pore_area': float(np.mean(pore_areas)) if pore_areas else 0.0,
            'std_pore_area': float(np.std(pore_areas)) if pore_areas else 0.0,
            'mean_pore_circularity': float(np.mean(pore_circularities)) if pore_circularities else 0.0,
            'mean_pore_aspect_ratio': float(np.mean(pore_aspect_ratios)) if pore_aspect_ratios else 0.0
        }
        
        return results, pores_cleaned, pore_regions
    
    def analyze_fiber_structure(self, image_normalized):
        """
        Analisa estrutura fibrilar (esqueleto, densidade, junções)
        
        Args:
            image_normalized (np.array): Imagem normalizada
            
        Returns:
            tuple: (resultados_estrutura, esqueleto, caracteristicas_lineares, coordenadas_juncoes)
        """
        # Suavização
        blurred = filters.gaussian(image_normalized, sigma=1.0)
        
        # Filtros direcionais para realce de características lineares
        kernel_h = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32)
        horizontal_lines = cv2.filter2D(blurred, -1, kernel_h)
        
        kernel_v = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32)
        vertical_lines = cv2.filter2D(blurred, -1, kernel_v)
        
        # Combinação de características lineares
        linear_features = np.maximum(horizontal_lines, vertical_lines)
        linear_threshold = filters.threshold_otsu(linear_features)
        linear_mask = linear_features > linear_threshold
        
        # Esqueletização
        skeleton = skeletonize(linear_mask)
        
        # Cálculo de densidade fibrilar
        fibril_density = np.sum(skeleton) / (skeleton.shape[0] * skeleton.shape[1])
        
        # Detecção de junções usando detector de Harris
        corners = feature.corner_harris(image_normalized, method='eps', sigma=2)
        corner_coords = feature.corner_peaks(corners, min_distance=10, 
                                           threshold_abs=0.01*corners.max())
        
        results = {
            'fibril_density': float(fibril_density),
            'num_junctions': len(corner_coords),
            'linear_feature_intensity': float(np.mean(linear_features)),
            'skeleton_length': int(np.sum(skeleton))
        }
        
        return results, skeleton, linear_features, corner_coords
    
    def analyze_surface_texture(self, image_normalized):
        """
        Analisa textura superficial usando GLCM e rugosidade
        
        Args:
            image_normalized (np.array): Imagem normalizada
            
        Returns:
            tuple: (resultados_textura, mapa_rugosidade)
        """
        # Conversão para uint8 para GLCM
        image_uint8 = (image_normalized * 255).astype(np.uint8)
        
        # Parâmetros GLCM
        distances = [1, 2, 3, 5]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        # Cálculo da matriz de co-ocorrência
        glcm = graycomatrix(image_uint8, distances, angles, 256, 
                           symmetric=True, normed=True)
        
        # Descritores de textura
        contrast = float(graycoprops(glcm, 'contrast').mean())
        dissimilarity = float(graycoprops(glcm, 'dissimilarity').mean())
        homogeneity = float(graycoprops(glcm, 'homogeneity').mean())
        energy = float(graycoprops(glcm, 'energy').mean())
        correlation = float(graycoprops(glcm, 'correlation').mean())
        
        # Análise de rugosidade local
        kernel_size = 9
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size**2)
        local_mean = cv2.filter2D(image_normalized, -1, kernel)
        local_variance = cv2.filter2D((image_normalized - local_mean)**2, -1, kernel)
        local_roughness = np.sqrt(local_variance)
        
        mean_roughness = float(np.mean(local_roughness))
        std_roughness = float(np.std(local_roughness))
        max_roughness = float(np.max(local_roughness))
        
        results = {
            'texture_contrast': contrast,
            'texture_dissimilarity': dissimilarity,
            'texture_homogeneity': homogeneity,
            'texture_energy': energy,
            'texture_correlation': correlation,
            'mean_surface_roughness': mean_roughness,
            'std_surface_roughness': std_roughness,
            'max_surface_roughness': max_roughness
        }
        
        return results, local_roughness

# ============================================================================
# ANÁLISE DE RUGOSIDADE AVANÇADA
# ============================================================================

def calculate_enhanced_roughness(image_normalized, method='local_std'):
    """
    Calcula rugosidade com diferentes métodos
    
    Args:
        image_normalized (np.array): Imagem normalizada
        method (str): Método de cálculo ('local_std', 'gradient_magnitude', 
                     'laplacian', 'range_filter')
    
    Returns:
        np.array: Mapa de rugosidade
    """
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
        local_max = ndimage.maximum_filter(image_normalized, size=kernel_size)
        local_min = ndimage.minimum_filter(image_normalized, size=kernel_size)
        roughness = local_max - local_min
        
    return roughness

def create_custom_colormap():
    """Cria colormap personalizado para rugosidade"""
    colors = ['#000080', '#0000FF', '#00FFFF', '#00FF00', 
              '#FFFF00', '#FF8000', '#FF0000', '#800000']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('rugosidade', colors, N=n_bins)
    return cmap

# ============================================================================
# ANÁLISE COMPARATIVA COMPLETA
# ============================================================================

class ComparativeFiberAnalyzer:
    """Analisador comparativo para fibras com e sem tratamento"""
    
    def __init__(self):
        self.analyzer = FiberAnalyzer()
        self.results = {}
        
    def analyze_single_fiber(self, image_path, sample_name):
        """
        Análise completa de uma fibra
        
        Args:
            image_path (str): Caminho da imagem
            sample_name (str): Nome da amostra
            
        Returns:
            tuple: (resultados, dados_processados)
        """
        print(f"Analisando: {sample_name}")
        
        # Carregar imagem
        image, image_normalized = self.analyzer.load_and_process_image(image_path)
        
        # Análises
        orientation_results, angles, magnitudes = self.analyzer.analyze_fiber_orientation(image_normalized)
        surface_results, pores, pore_regions = self.analyzer.analyze_surface_features(image, image_normalized)
        structure_results, skeleton, linear_features, corner_coords = self.analyzer.analyze_fiber_structure(image_normalized)
        texture_results, local_roughness = self.analyzer.analyze_surface_texture(image_normalized)
        
        # Compilar resultados
        results = {
            'sample_name': sample_name,
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'fiber_orientation': orientation_results,
            'surface_features': surface_results,
            'fibrillar_structure': structure_results,
            'surface_texture': texture_results
        }
        
        # Dados processados para visualização
        processed_data = {
            'image': image,
            'image_normalized': image_normalized,
            'angles': angles,
            'magnitudes': magnitudes,
            'pores': pores,
            'skeleton': skeleton,
            'corner_coords': corner_coords,
            'local_roughness': local_roughness
        }
        
        return results, processed_data
    
    def create_comparative_visualization(self, results_sem, results_com, 
                                       data_sem, data_com, output_path):
        """
        Cria visualização comparativa completa
        
        Args:
            results_sem (dict): Resultados fibra sem tratamento
            results_com (dict): Resultados fibra com tratamento
            data_sem (dict): Dados processados sem tratamento
            data_com (dict): Dados processados com tratamento
            output_path (str): Caminho de saída
        """
        fig, axes = plt.subplots(3, 4, figsize=(20, 15))
        fig.suptitle('Análise Comparativa: Fibras de Taboa Sem vs. Com Tratamento', 
                    fontsize=16, fontweight='bold')
        
        # Linha 1: Imagens originais e orientação
        axes[0,0].imshow(data_sem['image'], cmap='gray')
        axes[0,0].set_title('Fibra SEM Tratamento\n(T3-1.2Kx)', fontsize=12, fontweight='bold')
        axes[0,0].axis('off')
        
        axes[0,1].imshow(data_com['image'], cmap='gray')
        axes[0,1].set_title('Fibra COM Tratamento\n(1.05Kx)', fontsize=12, fontweight='bold')
        axes[0,1].axis('off')
        
        # Mapas de orientação
        orientation_sem = np.degrees(data_sem['angles']) % 180
        orientation_com = np.degrees(data_com['angles']) % 180
        
        im1 = axes[0,2].imshow(orientation_sem, cmap='hsv', vmin=0, vmax=180)
        axes[0,2].set_title('Orientação - SEM Tratamento', fontsize=12)
        axes[0,2].axis('off')
        
        im2 = axes[0,3].imshow(orientation_com, cmap='hsv', vmin=0, vmax=180)
        axes[0,3].set_title('Orientação - COM Tratamento', fontsize=12)
        axes[0,3].axis('off')
        
        # Linha 2: Poros e esqueletos
        axes[1,0].imshow(data_sem['image'], cmap='gray', alpha=0.7)
        axes[1,0].imshow(data_sem['pores'], cmap='Reds', alpha=0.6)
        axes[1,0].set_title(f'Poros - SEM\n({results_sem["surface_features"]["num_pores"]} poros)', 
                           fontsize=12)
        axes[1,0].axis('off')
        
        axes[1,1].imshow(data_com['image'], cmap='gray', alpha=0.7)
        axes[1,1].imshow(data_com['pores'], cmap='Reds', alpha=0.6)
        axes[1,1].set_title(f'Poros - COM\n({results_com["surface_features"]["num_pores"]} poros)', 
                           fontsize=12)
        axes[1,1].axis('off')
        
        # Esqueletos
        axes[1,2].imshow(data_sem['image'], cmap='gray', alpha=0.8)
        axes[1,2].imshow(data_sem['skeleton'], cmap='Reds', alpha=0.8)
        axes[1,2].set_title('Esqueleto - SEM', fontsize=12)
        axes[1,2].axis('off')
        
        axes[1,3].imshow(data_com['image'], cmap='gray', alpha=0.8)
        axes[1,3].imshow(data_com['skeleton'], cmap='Reds', alpha=0.8)
        axes[1,3].set_title('Esqueleto - COM', fontsize=12)
        axes[1,3].axis('off')
        
        # Linha 3: Gráficos quantitativos
        categories = ['SEM Tratamento', 'COM Tratamento']
        
        # Porosidade
        porosities = [results_sem['surface_features']['porosity_percentage'], 
                     results_com['surface_features']['porosity_percentage']]
        bars1 = axes[2,0].bar(categories, porosities, color=['lightcoral', 'lightblue'], alpha=0.7)
        axes[2,0].set_title('Porosidade (%)', fontsize=12, fontweight='bold')
        axes[2,0].set_ylabel('Porosidade (%)')
        for i, v in enumerate(porosities):
            axes[2,0].text(i, v + 0.5, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # Rugosidade
        roughness = [results_sem['surface_texture']['mean_surface_roughness'],
                    results_com['surface_texture']['mean_surface_roughness']]
        bars2 = axes[2,1].bar(categories, roughness, color=['lightcoral', 'lightblue'], alpha=0.7)
        axes[2,1].set_title('Rugosidade Superficial', fontsize=12, fontweight='bold')
        axes[2,1].set_ylabel('Rugosidade')
        for i, v in enumerate(roughness):
            axes[2,1].text(i, v + 0.001, f'{v:.3f}', ha='center', fontweight='bold')
        
        # Junções
        junctions = [results_sem['fibrillar_structure']['num_junctions'],
                    results_com['fibrillar_structure']['num_junctions']]
        bars3 = axes[2,2].bar(categories, junctions, color=['lightcoral', 'lightblue'], alpha=0.7)
        axes[2,2].set_title('Número de Junções', fontsize=12, fontweight='bold')
        axes[2,2].set_ylabel('Junções')
        for i, v in enumerate(junctions):
            axes[2,2].text(i, v + 10, f'{v}', ha='center', fontweight='bold')
        
        # Contraste
        contrast = [results_sem['surface_texture']['texture_contrast'],
                   results_com['surface_texture']['texture_contrast']]
        bars4 = axes[2,3].bar(categories, contrast, color=['lightcoral', 'lightblue'], alpha=0.7)
        axes[2,3].set_title('Contraste de Textura', fontsize=12, fontweight='bold')
        axes[2,3].set_ylabel('Contraste')
        for i, v in enumerate(contrast):
            axes[2,3].text(i, v + 10, f'{v:.0f}', ha='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def run_comparative_analysis(self, image_path_sem, image_path_com, output_dir):
        """
        Executa análise comparativa completa
        
        Args:
            image_path_sem (str): Caminho da fibra sem tratamento
            image_path_com (str): Caminho da fibra com tratamento
            output_dir (str): Diretório de saída
            
        Returns:
            dict: Resultados comparativos
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print("Análise Comparativa de Fibras de Taboa")
        print("=" * 60)
        
        # Analisar ambas as fibras
        results_sem, data_sem = self.analyze_single_fiber(
            image_path_sem, "Fibra SEM Tratamento"
        )
        
        results_com, data_com = self.analyze_single_fiber(
            image_path_com, "Fibra COM Tratamento"
        )
        
        # Criar visualização
        viz_path = os.path.join(output_dir, "analise_comparativa_fibras.png")
        self.create_comparative_visualization(results_sem, results_com, 
                                            data_sem, data_com, viz_path)
        
        # Compilar resultados
        comparative_results = {
            'timestamp': datetime.now().isoformat(),
            'fibra_sem_tratamento': results_sem,
            'fibra_com_tratamento': results_com,
            'comparacao': self.calculate_differences(results_sem, results_com)
        }
        
        # Salvar resultados
        json_path = os.path.join(output_dir, "resultados_comparativos.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(comparative_results, f, indent=2, ensure_ascii=False)
        
        return comparative_results
    
    def calculate_differences(self, results_sem, results_com):
        """Calcula diferenças percentuais entre amostras"""
        differences = {}
        
        # Porosidade
        por_sem = results_sem['surface_features']['porosity_percentage']
        por_com = results_com['surface_features']['porosity_percentage']
        differences['porosity_change'] = {
            'absolute': por_com - por_sem,
            'relative_percent': ((por_com - por_sem) / por_sem) * 100 if por_sem > 0 else 0
        }
        
        # Rugosidade
        rug_sem = results_sem['surface_texture']['mean_surface_roughness']
        rug_com = results_com['surface_texture']['mean_surface_roughness']
        differences['roughness_change'] = {
            'absolute': rug_com - rug_sem,
            'relative_percent': ((rug_com - rug_sem) / rug_sem) * 100 if rug_sem > 0 else 0
        }
        
        # Número de poros
        poros_sem = results_sem['surface_features']['num_pores']
        poros_com = results_com['surface_features']['num_pores']
        differences['pores_change'] = {
            'absolute': poros_com - poros_sem,
            'relative_percent': ((poros_com - poros_sem) / poros_sem) * 100 if poros_sem > 0 else 0
        }
        
        return differences

# ============================================================================
# EXEMPLO DE USO
# ============================================================================

def exemplo_uso_completo():
    """
    Exemplo de como usar todos os códigos
    """
    
    # 1. Análise individual de uma fibra
    analyzer = FiberAnalyzer()
    
    # Carregar imagem
    image_path = "caminho/para/sua/imagem.tif"
    image, image_norm = analyzer.load_and_process_image(image_path)
    
    # Análises individuais
    orientation_results, angles, magnitudes = analyzer.analyze_fiber_orientation(image_norm)
    surface_results, pores, pore_regions = analyzer.analyze_surface_features(image, image_norm)
    structure_results, skeleton, linear_features, corner_coords = analyzer.analyze_fiber_structure(image_norm)
    texture_results, local_roughness = analyzer.analyze_surface_texture(image_norm)
    
    print("Resultados de Orientação:", orientation_results)
    print("Resultados de Superfície:", surface_results)
    print("Resultados de Estrutura:", structure_results)
    print("Resultados de Textura:", texture_results)
    
    # 2. Análise comparativa
    comparative_analyzer = ComparativeFiberAnalyzer()
    
    results = comparative_analyzer.run_comparative_analysis(
        image_path_sem="fibra_sem_tratamento.tif",
        image_path_com="fibra_com_tratamento.tif",
        output_dir="resultados_analise"
    )
    
    # 3. Análise de rugosidade avançada
    rugosidade_local_std = calculate_enhanced_roughness(image_norm, 'local_std')
    rugosidade_gradiente = calculate_enhanced_roughness(image_norm, 'gradient_magnitude')
    rugosidade_laplaciano = calculate_enhanced_roughness(image_norm, 'laplacian')
    rugosidade_range = calculate_enhanced_roughness(image_norm, 'range_filter')
    
    print("Análise de rugosidade concluída")

if __name__ == "__main__":
    print("Códigos de Análise MEV - Fibras de Typha domingensis")
    print("=" * 60)
    print("Para usar os códigos, chame as funções apropriadas:")
    print("1. FiberAnalyzer() - para análise individual")
    print("2. ComparativeFiberAnalyzer() - para análise comparativa")
    print("3. calculate_enhanced_roughness() - para análise de rugosidade")
    print("4. Veja exemplo_uso_completo() para exemplos detalhados")
