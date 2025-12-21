"""
Análise Morfométrica MEV - Versão Recursiva
Taboa (Typha domingensis) vs Ouricuri (Syagrus coronata)
Com suporte a imagens em subdiretórios (DUAS_CAMADAS, SEM_TRAT)

Autor: Diego Vidal
Data: Dezembro 2025
"""

import cv2
import numpy as np
from skimage import filters, morphology, measure, feature
from skimage.morphology import skeletonize
from scipy import ndimage
import matplotlib.pyplot as plt
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ComparativeFiberAnalyzer:
    """
    Análise comparativa de fibras de Taboa e Ouricuri com busca recursiva
    """
    
    def __init__(self, output_dir="./5-DADOS/MEV-ANALISE/resultados-analise"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.all_results = {"taboa": {}, "ouricuri": {}}
        
    def load_image(self, image_path):
        """Carregar imagem MEV"""
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Não foi possível carregar: {image_path}")
        
        # Normalizar para 0-1
        img_norm = img.astype(float) / 255.0
        return img, img_norm
    
    def analyze_surface_porosity(self, image_norm, sigma=2.0, threshold_factor=0.7):
        """Análise de porosidade superficial"""
        smoothed = filters.gaussian(image_norm, sigma=sigma)
        
        threshold = filters.threshold_otsu(smoothed)
        binary = smoothed > threshold
        
        labeled = measure.label(binary)
        regions = measure.regionprops(labeled)
        
        # Calcular porosidade
        total_pixels = binary.size
        pore_pixels = np.sum(binary)
        porosity_pct = (pore_pixels / total_pixels) * 100
        
        # Análise de poros
        num_pores = len(regions)
        
        if num_pores > 0:
            pore_areas = [region.area for region in regions]
            mean_pore_area = np.mean(pore_areas)
            
            # Circularidade (1 = círculo perfeito)
            circularities = [4 * np.pi * region.area / (region.perimeter ** 2) if region.perimeter > 0 else 0 for region in regions]
            mean_circularity = np.mean(circularities)
            
            # Aspect ratio
            aspect_ratios = []
            for region in regions:
                if region.minor_axis_length > 0:
                    ar = region.major_axis_length / region.minor_axis_length
                    aspect_ratios.append(ar)
            mean_aspect_ratio = np.mean(aspect_ratios) if aspect_ratios else 0
        else:
            mean_pore_area = 0
            mean_circularity = 0
            mean_aspect_ratio = 0
        
        results = {
            'porosity_pct': round(porosity_pct, 2),
            'num_pores': num_pores,
            'mean_pore_area': round(mean_pore_area, 2),
            'pore_circularity': round(mean_circularity, 3),
            'aspect_ratio': round(mean_aspect_ratio, 3)
        }
        
        return results, binary, labeled, regions
    
    def analyze_surface_roughness(self, image_norm, window_size=31):
        """Análise de rugosidade superficial com mútricas"""
        # Método 1: Rugosidade por altura local
        kernel = np.ones((window_size, window_size)) / (window_size ** 2)
        local_mean = ndimage.convolve(image_norm, kernel, mode='reflect')
        local_var = ndimage.convolve(image_norm**2, kernel, mode='reflect') - local_mean**2
        roughness_height = np.sqrt(np.maximum(local_var, 0))
        
        # Método 2: Rugosidade por gradiente (velocidade de mudança)
        grad_x = ndimage.sobel(image_norm, axis=1)
        grad_y = ndimage.sobel(image_norm, axis=0)
        roughness_gradient = np.sqrt(grad_x**2 + grad_y**2)
        
        # Calcular estatísticas
        mean_roughness = np.mean(roughness_gradient) * 1000  # Converter para micrometros equivalentes
        std_roughness = np.std(roughness_gradient) * 1000
        max_roughness = np.max(roughness_gradient) * 1000
        
        results = {
            'mean_surface_roughness': round(mean_roughness, 2),
            'std_surface_roughness': round(std_roughness, 2),
            'max_surface_roughness': round(max_roughness, 2)
        }
        
        return results, roughness_gradient
    
    def analyze_orientation(self, image_norm):
        """Análise de orientação fibrilar"""
        # Calcular gradientes
        sobel_h = ndimage.sobel(image_norm, axis=1)
        sobel_v = ndimage.sobel(image_norm, axis=0)
        
        # Magnitude e orientação
        magnitude = np.sqrt(sobel_h**2 + sobel_v**2)
        orientation = np.arctan2(sobel_v, sobel_h)
        
        # Filtrar por magnitude
        threshold = np.percentile(magnitude, 75)
        mask = magnitude > threshold
        
        if np.sum(mask) > 0:
            angles_deg = np.degrees(orientation[mask])
            angles_deg = (angles_deg + 180) % 180
            
            std_angle = np.std(angles_deg)
            orientation_index = 1 - (std_angle / 90.0)
            
            results = {
                'mean_angle': round(np.mean(angles_deg), 2),
                'std_angle': round(std_angle, 2),
                'orientation_index': round(orientation_index, 3)
            }
        else:
            results = {
                'mean_angle': 0,
                'std_angle': 0,
                'orientation_index': 0
            }
        
        return results, magnitude, orientation
    
    def analyze_fiber_structure(self, image_norm, sigma=2.0):
        """Análise de estrutura fibrilar"""
        smoothed = filters.gaussian(image_norm, sigma=sigma)
        threshold = filters.threshold_otsu(smoothed)
        binary = smoothed > threshold
        
        skeleton = skeletonize(binary)
        fibril_density = np.sum(skeleton) / skeleton.size * 100
        skeletal_length = np.sum(skeleton)
        
        # Detecção de junções
        skeleton_float = skeleton.astype(float)
        corners = feature.corner_harris(skeleton_float, sigma=2.0)
        corner_threshold = np.percentile(corners[corners > 0], 95) if np.any(corners > 0) else 0
        junctions = corners > corner_threshold
        num_junctions = np.sum(junctions)
        
        results = {
            'fibril_density': round(fibril_density, 2),
            'num_junctions': int(num_junctions),
            'skeleton_length': int(skeletal_length)
        }
        
        return results, skeleton, junctions
    
    def analyze_fractures(self, image_norm):
        """Análise de fraturas e danos"""
        # Detecção de bordas para identificar fraturas
        edges = filters.sobel(image_norm)
        threshold = filters.threshold_otsu(edges)
        fracture_mask = edges > threshold
        
        # Morfologia
        fracture_mask = morphology.binary_dilation(fracture_mask, iterations=2)
        fracture_mask = morphology.binary_erosion(fracture_mask, iterations=1)
        
        labeled_fractures = measure.label(fracture_mask)
        fracture_regions = measure.regionprops(labeled_fractures)
        
        num_fractures = len(fracture_regions)
        
        if num_fractures > 0:
            total_fracture_area = sum([region.area for region in fracture_regions])
            fracture_length = np.sum(fracture_mask)
            damage_severity = (total_fracture_area / image_norm.size) * 100
            
            # Classificar severidade
            if damage_severity > 120:
                severity_class = "Crítico"
            elif damage_severity > 100:
                severity_class = "Severo"
            elif damage_severity > 80:
                severity_class = "Moderado"
            else:
                severity_class = "Leve"
            
            # Aspect ratio médio de fraturas
            avg_aspect_ratio = np.mean([
                region.major_axis_length / (region.minor_axis_length + 1e-6) 
                for region in fracture_regions
            ])
        else:
            total_fracture_area = 0
            fracture_length = 0
            damage_severity = 0
            severity_class = "Nenhum"
            avg_aspect_ratio = 0
        
        results = {
            'num_fractures': num_fractures,
            'total_fracture_area': round(total_fracture_area, 1),
            'fracture_length': int(fracture_length),
            'damage_severity': round(damage_severity, 2),
            'severity_class': severity_class,
            'avg_aspect_ratio': round(avg_aspect_ratio, 3)
        }
        
        return results, fracture_mask
    
    def analyze_glcm_texture(self, image_norm):
        """Análise de textura usando GLCM (Gray-Level Co-occurrence Matrix)"""
        # Quantizar imagem para 256 níveis
        image_quantized = (image_norm * 255).astype(np.uint8)
        
        # Distância e ângulo para GLCM
        distances = [1, 2]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        from skimage.feature import greycomatrix, greycoprops
        
        glcm = greycomatrix(image_quantized, distances, angles, levels=256, symmetric=True, normed=True)
        
        # Calcular propriedades
        contrast = np.mean([greycoprops(glcm[:, :, i, j], 'contrast') for i in range(len(distances)) for j in range(len(angles))])
        dissimilarity = np.mean([greycoprops(glcm[:, :, i, j], 'dissimilarity') for i in range(len(distances)) for j in range(len(angles))])
        homogeneity = np.mean([greycoprops(glcm[:, :, i, j], 'homogeneity') for i in range(len(distances)) for j in range(len(angles))])
        energy = np.mean([greycoprops(glcm[:, :, i, j], 'energy') for i in range(len(distances)) for j in range(len(angles))])
        correlation = np.mean([greycoprops(glcm[:, :, i, j], 'correlation') for i in range(len(distances)) for j in range(len(angles))])
        
        results = {
            'glcm_contrast': round(contrast, 2),
            'glcm_dissimilarity': round(dissimilarity, 3),
            'glcm_homogeneity': round(homogeneity, 3),
            'glcm_energy': round(energy, 3),
            'glcm_correlation': round(correlation, 3)
        }
        
        return results
    
    def analyze_single_image(self, image_path, fiber_type="Unknown", sample_name=""):
        """Análise completa de uma imagem"""
        print(f"  → Analisando: {Path(image_path).name}")
        
        try:
            img, img_norm = self.load_image(image_path)
            
            # Executar todas as análises
            porosity_results, binary, labeled, regions = self.analyze_surface_porosity(img_norm)
            roughness_results, roughness_gradient = self.analyze_surface_roughness(img_norm)
            orientation_results, mag, orient = self.analyze_orientation(img_norm)
            structure_results, skeleton, junctions = self.analyze_fiber_structure(img_norm)
            fracture_results, fracture_mask = self.analyze_fractures(img_norm)
            texture_results = self.analyze_glcm_texture(img_norm)
            
            # Consolidar resultados
            all_results = {
                'filename': Path(image_path).name,
                'fiber': fiber_type,
                'sample': sample_name,
                'image_size': list(img.shape),
                'orientation': orientation_results,
                'porosity': porosity_results,
                'structure': structure_results,
                'texture': {**roughness_results, **texture_results},
                'fractures': fracture_results
            }
            
            # Salvar figura de análise
            self.save_analysis_figure(img_norm, binary, skeleton, fracture_mask, roughness_gradient, 
                                     fiber_type, Path(image_path).stem, all_results)
            
            return all_results
            
        except Exception as e:
            print(f"    ✗ Erro ao analisar {image_path}: {str(e)}")
            return None
    
    def save_analysis_figure(self, img_norm, binary, skeleton, fractures, roughness, 
                            fiber_type, filename, results):
        """Salvar figura de análise"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        axes[0, 0].imshow(img_norm, cmap='gray')
        axes[0, 0].set_title('Imagem Original')
        axes[0, 0].axis('off')
        
        axes[0, 1].imshow(binary, cmap='gray')
        axes[0, 1].set_title('Porosidade\n' + f"({results['porosity']['porosity_pct']:.1f}% vazia)")
        axes[0, 1].axis('off')
        
        axes[0, 2].imshow(skeleton, cmap='gray')
        axes[0, 2].set_title('Estrutura Fibrilar\n' + f"({results['structure']['fibril_density']:.1f}% fibrilar)")
        axes[0, 2].axis('off')
        
        axes[1, 0].imshow(roughness, cmap='hot')
        axes[1, 0].set_title('Rugosidade\n' + f"(Ra: {results['texture']['mean_surface_roughness']:.1f} µm)")
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(fractures, cmap='gray')
        axes[1, 1].set_title('Fraturas\n' + f"({results['fractures']['num_fractures']} fraturas)")
        axes[1, 1].axis('off')
        
        axes[1, 2].axis('off')
        axes[1, 2].text(0.1, 0.9, f"Amostra: {filename}\nFibra: {fiber_type}\nSeveridade: {results['fractures']['severity_class']}", 
                        fontsize=11, verticalalignment='top', family='monospace')
        
        output_path = self.output_dir / f"{fiber_type.replace(' ', '_')}_{filename}_analise.png"
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"    ✓ Figura salva: {output_path.name}")
    
    def find_images_recursive(self, base_dir, fiber_type):
        """Encontrar imagens recursivamente"""
        base_path = Path(base_dir)
        images = []
        
        if base_path.exists():
            # Procurar TIF recursivamente
            tif_files = list(base_path.rglob("*.tif"))
            
            for tif_file in sorted(tif_files):
                # Classificar por subdiretório se existir
                relative_path = tif_file.relative_to(base_path)
                subdir = str(relative_path.parent).upper()
                
                images.append({
                    'path': tif_file,
                    'name': tif_file.stem,
                    'category': subdir if subdir != '.' else 'ROOT'
                })
        
        return images
    
    def process_all_images(self):
        """Processar todas as imagens encontradas"""
        base_dir = Path("./5-DADOS/MEV-ANALISE")
        
        # Procurar imagens
        taboa_images = self.find_images_recursive(base_dir / "imagens-taboa", "Typha domingensis")
        ouricuri_images = self.find_images_recursive(base_dir / "imagens-ouricuri", "Syagrus coronata")
        
        print(f"\n{'='*70}")
        print(f" Encontradas {len(taboa_images)} imagens de TABOA (Typha domingensis)")
        print(f" Encontradas {len(ouricuri_images)} imagens de OURICURI (Syagrus coronata)")
        print(f"{'='*70}")
        
        # Processar Taboa
        if taboa_images:
            print(f"\nAnalisando TABOA:")
            for img_info in taboa_images:
                result = self.analyze_single_image(img_info['path'], "Typha domingensis", img_info['name'])
                if result:
                    key = f"taboa_{img_info['name']}"
                    self.all_results['taboa'][key] = result
        
        # Processar Ouricuri
        if ouricuri_images:
            print(f"\nAnalisando OURICURI:")
            for img_info in ouricuri_images:
                result = self.analyze_single_image(img_info['path'], "Syagrus coronata", img_info['name'])
                if result:
                    key = f"ouricuri_{img_info['name']}"
                    self.all_results['ouricuri'][key] = result
        
        # Salvar resultados em JSON
        self.save_results()
    
    def save_results(self):
        """Salvar resultados em JSON"""
        output_json = self.output_dir / "analise_morfometrica_completa.json"
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(self.all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Resultados salvos em: {output_json}")


def main():
    print("\n" + "="*70)
    print(" ANÁLISE MORFOMÉTRICA MEV - VERSÃO RECURSIVA")
    print(" Taboa (Typha domingensis) vs Ouricuri (Syagrus coronata)")
    print("="*70)
    
    analyzer = ComparativeFiberAnalyzer()
    analyzer.process_all_images()
    
    print("\n" + "="*70)
    print(" ✓ Análise concluída com sucesso!")
    print(f" Resultados salvos em: {analyzer.output_dir}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
