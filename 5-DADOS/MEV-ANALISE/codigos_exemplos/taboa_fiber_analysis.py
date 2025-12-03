#!/usr/bin/env python3
"""
Análise Especializada de Fibras Naturais de Taboa - MEV
Focado em padrões estruturais, orientação de fibras, porosidade e características superficiais
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
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

class TaboaFiberAnalyzer:
    """Analisador especializado para fibras naturais de taboa"""
    
    def __init__(self):
        self.results = {}
        
    def load_image(self, image_path):
        """Carrega e pré-processa imagem MEV da fibra"""
        # Carrega imagem (suporta TIFF)
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Normaliza valores para 0-1
        image_normalized = image.astype(np.float32) / 255.0
        
        return image, image_normalized
    
    def analyze_fiber_orientation(self, image_normalized):
        """Analisa orientação predominante das fibras"""
        results = {}
        
        # Aplicar filtro para realçar estruturas lineares
        blurred = filters.gaussian(image_normalized, sigma=1.0)
        
        # Detecção de bordas direcionais usando filtros Sobel
        grad_x = filters.sobel_h(blurred)
        grad_y = filters.sobel_v(blurred)
        
        # Calcular ângulos dos gradientes
        angles = np.arctan2(grad_y, grad_x)
        magnitudes = np.sqrt(grad_x**2 + grad_y**2)
        
        # Filtrar apenas gradientes significativos
        threshold = np.percentile(magnitudes, 75)
        significant_angles = angles[magnitudes > threshold]
        
        # Converter para graus e normalizar para 0-180°
        angles_deg = np.degrees(significant_angles) % 180
        
        # Análise estatística da orientação
        mean_angle = float(np.mean(angles_deg))
        std_angle = float(np.std(angles_deg))
        
        # Calcular índice de orientação (0 = aleatório, 1 = altamente orientado)
        orientation_index = 1.0 - (std_angle / 90.0) if std_angle <= 90 else 0.0
        
        results['mean_fiber_angle'] = mean_angle
        results['angle_std_deviation'] = std_angle
        results['orientation_index'] = float(orientation_index)
        results['predominant_direction'] = self._classify_direction(mean_angle)
        
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
        """Analisa características da superfície da fibra"""
        results = {}
        
        # Detecção de poros e cavidades
        blurred = filters.gaussian(image_normalized, sigma=2.0)
        
        # Threshold para identificar regiões escuras (poros)
        threshold = filters.threshold_otsu(blurred)
        pores = blurred < (threshold * 0.7)  # Regiões mais escuras que o threshold
        
        # Limpeza morfológica
        pores_cleaned = morphology.remove_small_objects(pores, min_size=20)
        pores_cleaned = morphology.remove_small_holes(pores_cleaned, area_threshold=10)
        
        # Análise dos poros
        labeled_pores = measure.label(pores_cleaned)
        pore_regions = measure.regionprops(labeled_pores)
        
        pore_areas = [region.area for region in pore_regions]
        pore_circularities = []
        pore_aspect_ratios = []
        
        for region in pore_regions:
            if region.area > 10:
                # Circularidade
                circularity = 4 * np.pi * region.area / (region.perimeter ** 2)
                pore_circularities.append(circularity)
                
                # Razão de aspecto
                minr, minc, maxr, maxc = region.bbox
                aspect_ratio = (maxr - minr) / (maxc - minc) if (maxc - minc) > 0 else 1
                pore_aspect_ratios.append(aspect_ratio)
        
        # Cálculo da porosidade (% da área ocupada por poros)
        total_area = image_normalized.shape[0] * image_normalized.shape[1]
        pore_area_total = np.sum(pore_areas)
        porosity = (pore_area_total / total_area) * 100
        
        results['num_pores'] = len(pore_areas)
        results['porosity_percentage'] = float(porosity)
        results['mean_pore_area'] = float(np.mean(pore_areas)) if pore_areas else 0.0
        results['std_pore_area'] = float(np.std(pore_areas)) if pore_areas else 0.0
        results['mean_pore_circularity'] = float(np.mean(pore_circularities)) if pore_circularities else 0.0
        results['mean_pore_aspect_ratio'] = float(np.mean(pore_aspect_ratios)) if pore_aspect_ratios else 0.0
        
        return results, pores_cleaned, pore_regions
    
    def analyze_fiber_structure(self, image_normalized):
        """Analisa estrutura fibrilar e padrões de celulose"""
        results = {}
        
        # Detecção de estruturas lineares (fibrilas)
        blurred = filters.gaussian(image_normalized, sigma=1.0)
        
        # Aplicar filtros direcionais para detectar fibrilas
        # Filtro horizontal
        kernel_h = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32)
        horizontal_lines = cv2.filter2D(blurred, -1, kernel_h)
        
        # Filtro vertical  
        kernel_v = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32)
        vertical_lines = cv2.filter2D(blurred, -1, kernel_v)
        
        # Combinar detecções
        linear_features = np.maximum(horizontal_lines, vertical_lines)
        
        # Threshold para estruturas lineares
        linear_threshold = filters.threshold_otsu(linear_features)
        linear_mask = linear_features > linear_threshold
        
        # Esqueletização para encontrar o centro das fibrilas
        skeleton = skeletonize(linear_mask)
        
        # Análise da densidade de fibrilas
        fibril_density = np.sum(skeleton) / (skeleton.shape[0] * skeleton.shape[1])
        
        # Detecção de junções e ramificações
        # Usar operador de Harris para detectar pontos de interesse
        corners = feature.corner_harris(image_normalized, method='eps', sigma=2)
        corner_coords = feature.corner_peaks(corners, min_distance=10, threshold_abs=0.01*corners.max())
        
        results['fibril_density'] = float(fibril_density)
        results['num_junctions'] = len(corner_coords)
        results['linear_feature_intensity'] = float(np.mean(linear_features))
        results['skeleton_length'] = int(np.sum(skeleton))
        
        return results, skeleton, linear_features, corner_coords
    
    def analyze_surface_texture_detailed(self, image_normalized):
        """Análise detalhada da textura superficial"""
        results = {}
        
        # Converter para uint8 para GLCM
        image_uint8 = (image_normalized * 255).astype(np.uint8)
        
        # Matriz de co-ocorrência com múltiplas direções e distâncias
        distances = [1, 2, 3, 5]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        glcm = graycomatrix(image_uint8, distances, angles, 256, symmetric=True, normed=True)
        
        # Propriedades da textura
        contrast = float(graycoprops(glcm, 'contrast').mean())
        dissimilarity = float(graycoprops(glcm, 'dissimilarity').mean())
        homogeneity = float(graycoprops(glcm, 'homogeneity').mean())
        energy = float(graycoprops(glcm, 'energy').mean())
        correlation = float(graycoprops(glcm, 'correlation').mean())
        
        # Análise de rugosidade local
        # Calcular variação local usando filtro de desvio padrão
        kernel_size = 9
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size**2)
        local_mean = cv2.filter2D(image_normalized, -1, kernel)
        local_variance = cv2.filter2D((image_normalized - local_mean)**2, -1, kernel)
        local_roughness = np.sqrt(local_variance)
        
        # Estatísticas de rugosidade
        mean_roughness = float(np.mean(local_roughness))
        std_roughness = float(np.std(local_roughness))
        max_roughness = float(np.max(local_roughness))
        
        results.update({
            'texture_contrast': contrast,
            'texture_dissimilarity': dissimilarity,
            'texture_homogeneity': homogeneity,
            'texture_energy': energy,
            'texture_correlation': correlation,
            'mean_surface_roughness': mean_roughness,
            'std_surface_roughness': std_roughness,
            'max_surface_roughness': max_roughness
        })
        
        return results, local_roughness
    
    def classify_fiber_characteristics(self, orientation_results, surface_results, structure_results, texture_results):
        """Classifica características da fibra de taboa"""
        classification = {}
        
        # Classificação da orientação
        if orientation_results['orientation_index'] > 0.7:
            orientation_class = "Altamente Orientada"
        elif orientation_results['orientation_index'] > 0.4:
            orientation_class = "Moderadamente Orientada"
        else:
            orientation_class = "Orientação Aleatória"
        
        # Classificação da porosidade
        porosity = surface_results['porosity_percentage']
        if porosity > 15:
            porosity_class = "Alta Porosidade"
        elif porosity > 5:
            porosity_class = "Porosidade Moderada"
        else:
            porosity_class = "Baixa Porosidade"
        
        # Classificação da estrutura fibrilar
        if structure_results['fibril_density'] > 0.1:
            structure_class = "Estrutura Fibrilar Densa"
        elif structure_results['fibril_density'] > 0.05:
            structure_class = "Estrutura Fibrilar Moderada"
        else:
            structure_class = "Estrutura Fibrilar Esparsa"
        
        # Classificação da rugosidade
        if texture_results['mean_surface_roughness'] > 0.1:
            roughness_class = "Superfície Rugosa"
        elif texture_results['mean_surface_roughness'] > 0.05:
            roughness_class = "Superfície Moderadamente Rugosa"
        else:
            roughness_class = "Superfície Lisa"
        
        classification.update({
            'fiber_orientation': orientation_class,
            'porosity_level': porosity_class,
            'fibrillar_structure': structure_class,
            'surface_roughness': roughness_class,
            'predominant_direction': orientation_results['predominant_direction']
        })
        
        # Características específicas detectadas
        characteristics = []
        
        if orientation_results['orientation_index'] > 0.6:
            characteristics.append("Fibras bem alinhadas")
        
        if surface_results['num_pores'] > 50:
            characteristics.append("Rica em poros")
        
        if structure_results['num_junctions'] > 20:
            characteristics.append("Múltiplas ramificações")
        
        if texture_results['texture_homogeneity'] < 0.3:
            characteristics.append("Textura heterogênea")
        
        if surface_results['mean_pore_circularity'] > 0.7:
            characteristics.append("Poros predominantemente circulares")
        
        classification['specific_characteristics'] = characteristics
        
        return classification
    
    def create_comprehensive_visualization(self, image_path, image, image_normalized, 
                                         skeleton, pores, corner_coords, local_roughness, 
                                         angles, magnitudes, output_path):
        """Cria visualização completa da análise da fibra"""
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))
        fig.suptitle(f'Análise Completa da Fibra de Taboa - {os.path.basename(image_path)}', fontsize=16)
        
        # 1. Imagem original
        axes[0,0].imshow(image, cmap='gray')
        axes[0,0].set_title('Imagem Original MEV')
        axes[0,0].axis('off')
        
        # 2. Mapa de orientação das fibras
        orientation_map = np.degrees(angles) % 180
        im1 = axes[0,1].imshow(orientation_map, cmap='hsv', vmin=0, vmax=180)
        axes[0,1].set_title('Mapa de Orientação das Fibras')
        axes[0,1].axis('off')
        plt.colorbar(im1, ax=axes[0,1], label='Ângulo (graus)')
        
        # 3. Detecção de poros
        axes[0,2].imshow(image, cmap='gray', alpha=0.7)
        axes[0,2].imshow(pores, cmap='Reds', alpha=0.5)
        axes[0,2].set_title('Detecção de Poros')
        axes[0,2].axis('off')
        
        # 4. Esqueleto das fibrilas
        axes[1,0].imshow(image, cmap='gray', alpha=0.8)
        axes[1,0].imshow(skeleton, cmap='Reds', alpha=0.7)
        axes[1,0].set_title('Esqueleto das Fibrilas')
        axes[1,0].axis('off')
        
        # 5. Pontos de junção/ramificação
        axes[1,1].imshow(image, cmap='gray')
        if len(corner_coords) > 0:
            axes[1,1].plot(corner_coords[:, 1], corner_coords[:, 0], 'ro', markersize=3)
        axes[1,1].set_title(f'Junções Detectadas ({len(corner_coords)})')
        axes[1,1].axis('off')
        
        # 6. Mapa de rugosidade
        im2 = axes[1,2].imshow(local_roughness, cmap='viridis')
        axes[1,2].set_title('Mapa de Rugosidade Local')
        axes[1,2].axis('off')
        plt.colorbar(im2, ax=axes[1,2], label='Rugosidade')
        
        # 7. Histograma de intensidades
        axes[2,0].hist(image_normalized.flatten(), bins=50, alpha=0.7, color='blue')
        axes[2,0].set_title('Distribuição de Intensidades')
        axes[2,0].set_xlabel('Intensidade')
        axes[2,0].set_ylabel('Frequência')
        
        # 8. Histograma de orientações
        significant_angles = angles[magnitudes > np.percentile(magnitudes, 75)]
        angles_deg = np.degrees(significant_angles) % 180
        axes[2,1].hist(angles_deg, bins=36, alpha=0.7, color='green')
        axes[2,1].set_title('Distribuição de Orientações')
        axes[2,1].set_xlabel('Ângulo (graus)')
        axes[2,1].set_ylabel('Frequência')
        
        # 9. Perfil de rugosidade
        # Extrair perfil central horizontal
        center_row = local_roughness.shape[0] // 2
        profile = local_roughness[center_row, :]
        axes[2,2].plot(profile, 'b-', linewidth=2)
        axes[2,2].set_title('Perfil de Rugosidade (linha central)')
        axes[2,2].set_xlabel('Posição (pixels)')
        axes[2,2].set_ylabel('Rugosidade')
        axes[2,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def analyze_taboa_fiber(self, image_path, output_dir):
        """Análise completa da fibra de taboa"""
        print(f"Analisando fibra de taboa: {os.path.basename(image_path)}")
        
        # Carrega imagem
        image, image_normalized = self.load_image(image_path)
        
        # Análises específicas
        orientation_results, angles, magnitudes = self.analyze_fiber_orientation(image_normalized)
        surface_results, pores, pore_regions = self.analyze_surface_features(image, image_normalized)
        structure_results, skeleton, linear_features, corner_coords = self.analyze_fiber_structure(image_normalized)
        texture_results, local_roughness = self.analyze_surface_texture_detailed(image_normalized)
        
        # Classificação
        classification = self.classify_fiber_characteristics(orientation_results, surface_results, 
                                                           structure_results, texture_results)
        
        # Compilar resultados
        results = {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'fiber_orientation': orientation_results,
            'surface_features': surface_results,
            'fibrillar_structure': structure_results,
            'surface_texture': texture_results,
            'classification': classification,
            'scale_info': {
                'magnification': '1.05kx',
                'scale_bar': '50 μm',
                'working_distance': '19.09 mm',
                'acceleration_voltage': '10 keV'
            }
        }
        
        # Criar visualização
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        viz_path = os.path.join(output_dir, f"{base_name}_taboa_analysis.png")
        self.create_comprehensive_visualization(image_path, image, image_normalized, skeleton, 
                                              pores, corner_coords, local_roughness, angles, 
                                              magnitudes, viz_path)
        
        # Salvar resultados JSON
        json_path = os.path.join(output_dir, f"{base_name}_taboa_results.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results

def main():
    """Função principal para análise da fibra de taboa"""
    
    # Configurar diretórios
    input_file = "/home/ubuntu/taboa_analysis.tiff"
    output_dir = "/home/ubuntu/taboa_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializar analisador
    analyzer = TaboaFiberAnalyzer()
    
    print("Análise Especializada de Fibra Natural de Taboa")
    print("=" * 60)
    
    try:
        results = analyzer.analyze_taboa_fiber(input_file, output_dir)
        
        # Imprimir resumo detalhado
        print(f"✓ Análise concluída com sucesso!")
        print(f"\n📊 RESULTADOS DA ANÁLISE:")
        print(f"{'='*50}")
        
        print(f"\n🧬 ORIENTAÇÃO DAS FIBRAS:")
        print(f"  • Direção predominante: {results['classification']['predominant_direction']}")
        print(f"  • Ângulo médio: {results['fiber_orientation']['mean_fiber_angle']:.1f}°")
        print(f"  • Índice de orientação: {results['fiber_orientation']['orientation_index']:.3f}")
        print(f"  • Classificação: {results['classification']['fiber_orientation']}")
        
        print(f"\n🕳️ CARACTERÍSTICAS DA SUPERFÍCIE:")
        print(f"  • Porosidade: {results['surface_features']['porosity_percentage']:.2f}%")
        print(f"  • Número de poros: {results['surface_features']['num_pores']}")
        print(f"  • Área média dos poros: {results['surface_features']['mean_pore_area']:.1f} pixels")
        print(f"  • Classificação: {results['classification']['porosity_level']}")
        
        print(f"\n🔬 ESTRUTURA FIBRILAR:")
        print(f"  • Densidade fibrilar: {results['fibrillar_structure']['fibril_density']:.4f}")
        print(f"  • Número de junções: {results['fibrillar_structure']['num_junctions']}")
        print(f"  • Comprimento do esqueleto: {results['fibrillar_structure']['skeleton_length']} pixels")
        print(f"  • Classificação: {results['classification']['fibrillar_structure']}")
        
        print(f"\n📏 TEXTURA SUPERFICIAL:")
        print(f"  • Rugosidade média: {results['surface_texture']['mean_surface_roughness']:.4f}")
        print(f"  • Contraste: {results['surface_texture']['texture_contrast']:.1f}")
        print(f"  • Homogeneidade: {results['surface_texture']['texture_homogeneity']:.3f}")
        print(f"  • Classificação: {results['classification']['surface_roughness']}")
        
        print(f"\n🎯 CARACTERÍSTICAS ESPECÍFICAS:")
        for char in results['classification']['specific_characteristics']:
            print(f"  • {char}")
        
        print(f"\n📁 Arquivos gerados:")
        print(f"  • Visualização: {output_dir}/taboa_analysis_taboa_analysis.png")
        print(f"  • Dados JSON: {output_dir}/taboa_analysis_taboa_results.json")
        
    except Exception as e:
        print(f"✗ Erro na análise: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
