"""
Análise Morfométrica Completa das Imagens MEV Selecionadas
==========================================================

Processa as 8 imagens selecionadas (Taboa e Ouricuri, 30d e 180d, ST e DC)
e gera dados morfométricos completos para integração no manuscrito.

Parâmetros analisados:
- Orientação de fibras (ângulo médio, desvio, índice de orientação)
- Porosidade superficial (%, área média, circularidade)
- Estrutura fibrilar (densidade, junções, comprimento esqueleto)
- Textura superficial (GLCM: contraste, homogeneidade, energia, correlação)
- Rugosidade (média, desvio, máxima)
- Padrões de fratura/dano (detectados via contornos e morfologia)

Autor: Diego Vidal
Data: Dezembro 2025
"""

import cv2
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
from skimage import morphology, feature, filters
from skimage.measure import regionprops, label
try:
    from skimage.feature import graycomatrix, graycoprops
except ImportError:
    from skimage.feature import greycomatrix as graycomatrix
    from skimage.feature import greycoprops as graycoprops
from scipy.ndimage import generic_filter
import warnings
warnings.filterwarnings('ignore')


class ComprehensiveMEVAnalyzer:
    """Analisador morfométrico completo para imagens MEV"""
    
    def __init__(self, selected_dir=None):
        if selected_dir is None:
            # Caminho relativo ao arquivo atual
            script_dir = Path(__file__).parent
            selected_dir = script_dir.parent / "5-DADOS" / "MEV-ANALISE" / "imagens-selecionadas"
        
        self.selected_dir = Path(selected_dir)
        self.results_dir = self.selected_dir.parent / "resultados-analise"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def load_image(self, image_path):
        """Carrega e pré-processa imagem"""
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Erro ao carregar: {image_path}")
        
        # Normalizar para 0-255
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        return img
    
    def analyze_fiber_orientation(self, img):
        """
        Análise de orientação de fibras usando gradientes Sobel
        Retorna: ângulo médio, desvio padrão, índice de orientação (0-1)
        """
        # Gradientes Sobel
        sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        
        # Magnitude e ângulo
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        angle = np.arctan2(sobel_y, sobel_x) * 180 / np.pi
        
        # Filtrar gradientes fracos
        threshold = np.percentile(magnitude, 75)
        mask = magnitude > threshold
        
        valid_angles = angle[mask]
        
        if len(valid_angles) == 0:
            return {'mean_angle': 0, 'std_angle': 0, 'orientation_index': 0}
        
        # Estatísticas
        mean_angle = np.mean(valid_angles)
        std_angle = np.std(valid_angles)
        
        # Índice de orientação (0=randômico, 1=perfeitamente orientado)
        orientation_index = 1 - (std_angle / 90.0) if std_angle <= 90 else 0
        
        return {
            'mean_angle': float(mean_angle),
            'std_angle': float(std_angle),
            'orientation_index': float(np.clip(orientation_index, 0, 1))
        }
    
    def analyze_surface_porosity(self, img):
        """
        Análise de porosidade superficial usando threshold Otsu
        Retorna: % porosidade, número de poros, área média, circularidade
        """
        # Threshold Otsu
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Limpar ruído
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Identificar poros
        labeled = label(binary)
        regions = regionprops(labeled)
        
        # Filtrar regiões pequenas (ruído)
        min_area = 50
        valid_regions = [r for r in regions if r.area >= min_area]
        
        if len(valid_regions) == 0:
            return {
                'porosity_pct': 0,
                'num_pores': 0,
                'mean_pore_area': 0,
                'pore_circularity': 0,
                'aspect_ratio': 0
            }
        
        # Calcular métricas
        total_pore_area = sum(r.area for r in valid_regions)
        porosity_pct = (total_pore_area / img.size) * 100
        
        mean_pore_area = np.mean([r.area for r in valid_regions])
        
        # Circularidade: 4π*area/perimeter² (1=círculo perfeito)
        circularities = []
        aspect_ratios = []
        for r in valid_regions:
            if r.perimeter > 0:
                circ = (4 * np.pi * r.area) / (r.perimeter ** 2)
                circularities.append(circ)
            if r.minor_axis_length > 0:
                ar = r.major_axis_length / r.minor_axis_length
                aspect_ratios.append(ar)
        
        mean_circularity = np.mean(circularities) if circularities else 0
        mean_aspect_ratio = np.mean(aspect_ratios) if aspect_ratios else 0
        
        return {
            'porosity_pct': float(porosity_pct),
            'num_pores': len(valid_regions),
            'mean_pore_area': float(mean_pore_area),
            'pore_circularity': float(mean_circularity),
            'aspect_ratio': float(mean_aspect_ratio)
        }
    
    def analyze_fibrillar_structure(self, img):
        """
        Análise de estrutura fibrilar via skeletonização
        Retorna: densidade de fibrilas, número de junções, comprimento total
        """
        # Threshold adaptativo
        binary = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Skeletonize
        skeleton = morphology.skeletonize(binary > 0)
        
        # Densidade fibrilar
        fibril_density = np.sum(skeleton) / skeleton.size * 100
        
        # Detectar junções (pontos com 3+ vizinhos)
        kernel = np.ones((3, 3), dtype=np.uint8)
        neighbors = cv2.filter2D(skeleton.astype(np.uint8), -1, kernel) * skeleton
        junctions = np.sum(neighbors >= 3)
        
        # Comprimento total do esqueleto
        skeleton_length = np.sum(skeleton)
        
        return {
            'fibril_density': float(fibril_density),
            'num_junctions': int(junctions),
            'skeleton_length': int(skeleton_length)
        }
    
    def analyze_surface_texture(self, img):
        """
        Análise de textura superficial usando GLCM
        Retorna: contraste, dissimilaridade, homogeneidade, energia, correlação
        """
        # Reduzir níveis de cinza para performance (256 -> 64)
        img_reduced = (img / 4).astype(np.uint8)
        
        # Realçar rugosidade: combinar gradiente e laplaciano para maior sensibilidade
        grad_x = cv2.Sobel(img.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(img.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        lap = cv2.Laplacian(img.astype(np.float32), cv2.CV_32F, ksize=3)
        enhanced_roughness = np.abs(grad_mag) + 0.5 * np.abs(lap)
        
        # GLCM em 4 direções
        distances = [1]
        angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
        
        glcm = graycomatrix(
            img_reduced, distances, angles, 
            levels=64, symmetric=True, normed=True
        )
        
        # Propriedades GLCM (média das 4 direções)
        contrast = float(np.mean(graycoprops(glcm, 'contrast')))
        dissimilarity = float(np.mean(graycoprops(glcm, 'dissimilarity')))
        homogeneity = float(np.mean(graycoprops(glcm, 'homogeneity')))
        energy = float(np.mean(graycoprops(glcm, 'energy')))
        correlation = float(np.mean(graycoprops(glcm, 'correlation')))
        
        # Rugosidade local (variância em janelas 7x7) + componente de alta frequência
        local_var = generic_filter(img.astype(float), np.var, size=7)
        local_var = local_var + 0.3 * enhanced_roughness
        
        return {
            'glcm_contrast': contrast,
            'glcm_dissimilarity': dissimilarity,
            'glcm_homogeneity': homogeneity,
            'glcm_energy': energy,
            'glcm_correlation': correlation,
            'mean_surface_roughness': float(np.mean(local_var)),
            'std_surface_roughness': float(np.std(local_var)),
            'max_surface_roughness': float(np.max(local_var))
        }
    
    def detect_fracture_patterns(self, img):
        """
        Detecção de padrões de fratura/dano via análise de contornos e regiões escuras
        Retorna: número de fraturas, área total danificada, severidade
        """
        # MÉTODO 1: Detectar linhas pretas grossas (fraturas abertas)
        # Threshold para identificar regiões muito escuras (< 50 = preto/cinza escuro)
        _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Limpar ruído pequeno
        kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_OPEN, kernel_clean)
        
        # Encontrar contornos de regiões escuras
        contours_dark, _ = cv2.findContours(
            dark_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # MÉTODO 2: Detectar bordas Canny (fraturas finas/bordas)
        edges = cv2.Canny(img, 30, 90)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=3)
        
        contours_edges, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Analisar fraturas de ambos os métodos
        fractures = []
        all_contours = list(contours_dark) + list(contours_edges)
        
        for cnt in all_contours:
            area = cv2.contourArea(cnt)
            if area < 25:  # Limiar mínimo reduzido
                continue
            
            rect = cv2.minAreaRect(cnt)
            width, height = rect[1]
            if width == 0 or height == 0:
                continue
            
            aspect_ratio = max(width, height) / min(width, height)
            perimeter = cv2.arcLength(cnt, True)
            
            # Classificar como fratura se:
            # 1. Alongado (aspect_ratio > 2) OU
            # 2. Grande e escuro (área > 100 independente da forma)
            is_fracture = (aspect_ratio > 2) or (area > 100)
            
            if is_fracture:
                # Calcular severidade baseada em área e forma
                severity_score = area * (1 + 0.1 * aspect_ratio)
                
                fractures.append({
                    'area': area,
                    'aspect_ratio': aspect_ratio,
                    'perimeter': perimeter,
                    'severity_score': severity_score
                })
        
        # MÉTODO 3: Skeletonização de regiões escuras para medir comprimento de fraturas
        skeleton_fractures = morphology.skeletonize(dark_regions > 0)
        fracture_length = np.sum(skeleton_fractures)
        
        # Calcular métricas finais
        if not fractures:
            return {
                'num_fractures': 0,
                'total_fracture_area': 0,
                'fracture_length': 0,
                'damage_severity': 0,
                'severity_class': 'Nenhum'
            }
        
        total_fracture_area = sum(f['area'] for f in fractures)
        total_severity_score = sum(f['severity_score'] for f in fractures)
        
        # Severidade considerando área + comprimento
        damage_severity = (total_fracture_area / img.size) * 100
        length_factor = (fracture_length / img.size) * 100
        combined_severity = damage_severity + (0.5 * length_factor)
        
        # Classificar severidade
        if combined_severity < 0.5:
            severity_class = 'Leve'
        elif combined_severity < 2.0:
            severity_class = 'Moderado'
        elif combined_severity < 5.0:
            severity_class = 'Severo'
        else:
            severity_class = 'Crítico'
        
        return {
            'num_fractures': len(fractures),
            'total_fracture_area': float(total_fracture_area),
            'fracture_length': int(fracture_length),
            'damage_severity': float(combined_severity),
            'severity_class': severity_class,
            'avg_aspect_ratio': float(np.mean([f['aspect_ratio'] for f in fractures]))
        }
    
    def analyze_single_image(self, image_path):
        """Análise completa de uma única imagem"""
        print(f"  Analisando: {image_path.name}...")
        
        img = self.load_image(image_path)
        
        results = {
            'filename': image_path.name,
            'fiber': image_path.parent.name,
            'image_size': img.shape,
            'orientation': self.analyze_fiber_orientation(img),
            'porosity': self.analyze_surface_porosity(img),
            'structure': self.analyze_fibrillar_structure(img),
            'texture': self.analyze_surface_texture(img),
            'fractures': self.detect_fracture_patterns(img)
        }
        
        # Gerar visualização individual
        self.create_individual_visualization(img, results, image_path)
        
        return results
    
    def create_individual_visualization(self, img, results, image_path):
        """Cria visualização de análise individual"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        stem = image_path.stem
        fiber = results['fiber']
        
        fig.suptitle(f'Análise MEV: {stem}', fontsize=14, fontweight='bold')
        
        # 1. Imagem original
        axes[0, 0].imshow(img, cmap='gray')
        axes[0, 0].set_title('Imagem Original', fontsize=11, fontweight='bold')
        axes[0, 0].axis('off')
        
        # 2. Detecção de poros
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        pores = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        axes[0, 1].imshow(img, cmap='gray', alpha=0.7)
        axes[0, 1].imshow(pores, cmap='Reds', alpha=0.5)
        axes[0, 1].set_title(f'Porosidade: {results["porosity"]["porosity_pct"]:.1f}%\n'
                            f'{results["porosity"]["num_pores"]} poros', 
                            fontsize=11)
        axes[0, 1].axis('off')
        
        # 3. Estrutura fibrilar (skeleton)
        binary_struct = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        skeleton = morphology.skeletonize(binary_struct > 0)
        
        axes[0, 2].imshow(img, cmap='gray', alpha=0.6)
        axes[0, 2].imshow(skeleton, cmap='hot', alpha=0.7)
        axes[0, 2].set_title(f'Densidade Fibrilar: {results["structure"]["fibril_density"]:.1f}%\n'
                            f'{results["structure"]["num_junctions"]} junções',
                            fontsize=11)
        axes[0, 2].axis('off')
        
        # 4. Rugosidade superficial
        local_var = generic_filter(img.astype(float), np.var, size=7)
        
        im = axes[1, 0].imshow(local_var, cmap='jet')
        axes[1, 0].set_title(f'Rugosidade Superficial\nMédia: {results["texture"]["mean_surface_roughness"]:.1f}',
                            fontsize=11)
        axes[1, 0].axis('off')
        plt.colorbar(im, ax=axes[1, 0], fraction=0.046)
        
        # 5. Detecção de fraturas (regiões escuras + bordas + skeleton)
        # Detectar regiões escuras
        _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
        kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_OPEN, kernel_clean)
        
        # Skeleton das fraturas
        skeleton_fractures = morphology.skeletonize(dark_regions > 0)
        
        # Combinar visualização
        axes[1, 1].imshow(img, cmap='gray', alpha=0.7)
        axes[1, 1].imshow(dark_regions, cmap='Reds', alpha=0.4)
        axes[1, 1].imshow(skeleton_fractures, cmap='hot', alpha=0.6)
        axes[1, 1].set_title(f'Fraturas: {results["fractures"]["num_fractures"]}\n'
                            f'Severidade: {results["fractures"]["damage_severity"]:.2f}% ({results["fractures"].get("severity_class", "N/A")})',
                            fontsize=11)
        axes[1, 1].axis('off')
        
        # 6. Resumo quantitativo
        axes[1, 2].axis('off')
        summary_text = (
            f"RESUMO MORFOMÉTRICO\n"
            f"{'='*30}\n\n"
            f"Orientação:\n"
            f"  Índice: {results['orientation']['orientation_index']:.3f}\n\n"
            f"Porosidade:\n"
            f"  Total: {results['porosity']['porosity_pct']:.1f}%\n"
            f"  Nº poros: {results['porosity']['num_pores']}\n"
            f"  Circularidade: {results['porosity']['pore_circularity']:.3f}\n\n"
            f"Estrutura:\n"
            f"  Densidade: {results['structure']['fibril_density']:.1f}%\n"
            f"  Junções: {results['structure']['num_junctions']}\n\n"
            f"Textura (GLCM):\n"
            f"  Contraste: {results['texture']['glcm_contrast']:.1f}\n"
            f"  Homogeneidade: {results['texture']['glcm_homogeneity']:.3f}\n\n"
            f"Dano:\n"
            f"  Fraturas: {results['fractures']['num_fractures']}\n"
            f"  Comprimento: {results['fractures'].get('fracture_length', 0)} px\n"
            f"  Severidade: {results['fractures']['damage_severity']:.2f}%\n"
            f"  Classe: {results['fractures'].get('severity_class', 'N/A')}"
        )
        
        axes[1, 2].text(0.1, 0.95, summary_text, 
                       transform=axes[1, 2].transAxes,
                       fontsize=9, verticalalignment='top',
                       fontfamily='monospace',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        
        # Salvar
        viz_path = self.results_dir / f"{stem}_analise.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"    → Visualização salva: {viz_path.name}")
    
    def analyze_all_selected_images(self):
        """Analisa todas as 8 imagens selecionadas"""
        print("="*70)
        print(" ANÁLISE MORFOMÉTRICA COMPLETA - IMAGENS SELECIONADAS")
        print("="*70)
        
        all_results = {}
        
        for fiber in ['taboa', 'ouricuri']:
            print(f"\n{fiber.upper()}:")
            fiber_dir = self.selected_dir / fiber
            
            if not fiber_dir.exists():
                print(f"  AVISO: Diretório não encontrado: {fiber_dir}")
                continue
            
            fiber_results = {}
            
            for img_path in sorted(fiber_dir.glob("*.png")):
                result = self.analyze_single_image(img_path)
                key = img_path.stem  # ex: taboa_ST_30d
                fiber_results[key] = result
            
            all_results[fiber] = fiber_results
        
        # Salvar resultados
        output_file = self.results_dir / "analise_morfometrica_completa.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f" RESULTADOS SALVOS: {output_file}")
        print(f"{'='*70}")
        
        return all_results
    
    def generate_comparison_table(self, results):
        """Gera tabela comparativa para o manuscrito"""
        print("\n" + "="*70)
        print(" TABELA COMPARATIVA PARA MANUSCRITO")
        print("="*70)
        
        table_file = self.results_dir / "tabela_comparativa_manuscrito.md"
        
        with open(table_file, 'w', encoding='utf-8') as f:
            f.write("# Dados Morfométricos para Tabela 2 do Manuscrito\n\n")
            
            for fiber in ['taboa', 'ouricuri']:
                fiber_name = "Typha domingensis" if fiber == 'taboa' else "Syagrus coronata"
                f.write(f"## {fiber_name}\n\n")
                
                # Tabela principal
                f.write("| Parâmetro | ST 30d | ST 180d | DC 30d | DC 180d |\n")
                f.write("|-----------|--------|---------|--------|----------|\n")
                
                # Extrair dados
                data = results[fiber]
                
                # Orientação
                st_30 = data.get(f'{fiber}_ST_30d', {})
                st_180 = data.get(f'{fiber}_ST_180d', {})
                dc_30 = data.get(f'{fiber}_DC_30d', {})
                dc_180 = data.get(f'{fiber}_DC_180d', {})
                
                # Construir linhas
                def get_value(d, key_path, fmt=".2f"):
                    keys = key_path.split('.')
                    val = d
                    for k in keys:
                        val = val.get(k, {}) if isinstance(val, dict) else {}
                    return format(val, fmt) if isinstance(val, (int, float)) else "N/A"
                
                f.write(f"| Índice Orientação | {get_value(st_30, 'orientation.orientation_index')} | ")
                f.write(f"{get_value(st_180, 'orientation.orientation_index')} | ")
                f.write(f"{get_value(dc_30, 'orientation.orientation_index')} | ")
                f.write(f"{get_value(dc_180, 'orientation.orientation_index')} |\n")
                
                f.write(f"| Porosidade (%) | {get_value(st_30, 'porosity.porosity_pct')} | ")
                f.write(f"{get_value(st_180, 'porosity.porosity_pct')} | ")
                f.write(f"{get_value(dc_30, 'porosity.porosity_pct')} | ")
                f.write(f"{get_value(dc_180, 'porosity.porosity_pct')} |\n")
                
                f.write(f"| Densidade Fibrilar (%) | {get_value(st_30, 'structure.fibril_density')} | ")
                f.write(f"{get_value(st_180, 'structure.fibril_density')} | ")
                f.write(f"{get_value(dc_30, 'structure.fibril_density')} | ")
                f.write(f"{get_value(dc_180, 'structure.fibril_density')} |\n")
                
                f.write(f"| GLCM Contraste | {get_value(st_30, 'texture.glcm_contrast')} | ")
                f.write(f"{get_value(st_180, 'texture.glcm_contrast')} | ")
                f.write(f"{get_value(dc_30, 'texture.glcm_contrast')} | ")
                f.write(f"{get_value(dc_180, 'texture.glcm_contrast')} |\n")
                
                f.write(f"| Rugosidade Média | {get_value(st_30, 'texture.mean_surface_roughness')} | ")
                f.write(f"{get_value(st_180, 'texture.mean_surface_roughness')} | ")
                f.write(f"{get_value(dc_30, 'texture.mean_surface_roughness')} | ")
                f.write(f"{get_value(dc_180, 'texture.mean_surface_roughness')} |\n")
                
                f.write(f"| N° Fraturas | {get_value(st_30, 'fractures.num_fractures', 'd')} | ")
                f.write(f"{get_value(st_180, 'fractures.num_fractures', 'd')} | ")
                f.write(f"{get_value(dc_30, 'fractures.num_fractures', 'd')} | ")
                f.write(f"{get_value(dc_180, 'fractures.num_fractures', 'd')} |\n")
                
                f.write(f"| Severidade Dano (%) | {get_value(st_30, 'fractures.damage_severity')} | ")
                f.write(f"{get_value(st_180, 'fractures.damage_severity')} | ")
                f.write(f"{get_value(dc_30, 'fractures.damage_severity')} | ")
                f.write(f"{get_value(dc_180, 'fractures.damage_severity')} |\n")
                
                f.write("\n")
            
            f.write("\n## Legenda\n\n")
            f.write("- **ST**: Sem Tratamento\n")
            f.write("- **DC**: Dupla Camada de resina\n")
            f.write("- **30d / 180d**: Período de exposição em dias\n")
        
        print(f"Tabela salva: {table_file}\n")
    
    def create_comparative_figure(self, results):
        """Cria figura comparativa 4x2 para o manuscrito"""
        print("\n" + "="*70)
        print(" GERANDO FIGURA COMPARATIVA PARA MANUSCRITO")
        print("="*70)
        
        fig, axes = plt.subplots(4, 2, figsize=(12, 16))
        fig.suptitle('Análise Comparativa MEV: Typha domingensis vs Syagrus coronata\n'
                     'Sem Tratamento (ST) vs Dupla Camada (DC)', 
                     fontsize=14, fontweight='bold')
        
        # Carregar e exibir imagens
        positions = [
            (0, 0, 'taboa', 'taboa_ST_30d', 'Taboa ST 30d'),
            (0, 1, 'taboa', 'taboa_DC_30d', 'Taboa DC 30d'),
            (1, 0, 'taboa', 'taboa_ST_180d', 'Taboa ST 180d'),
            (1, 1, 'taboa', 'taboa_DC_180d', 'Taboa DC 180d'),
            (2, 0, 'ouricuri', 'ouricuri_ST_30d', 'Ouricuri ST 30d'),
            (2, 1, 'ouricuri', 'ouricuri_DC_30d', 'Ouricuri DC 30d'),
            (3, 0, 'ouricuri', 'ouricuri_ST_180d', 'Ouricuri ST 180d'),
            (3, 1, 'ouricuri', 'ouricuri_DC_180d', 'Ouricuri DC 180d'),
        ]
        
        for row, col, fiber, key, title in positions:
            img_path = self.selected_dir / fiber / f"{key}.png"
            
            if img_path.exists():
                img = self.load_image(img_path)
                
                # Dados morfométricos
                data = results[fiber].get(key, {})
                porosity = data.get('porosity', {}).get('porosity_pct', 0)
                density = data.get('structure', {}).get('fibril_density', 0)
                fractures = data.get('fractures', {}).get('num_fractures', 0)
                
                axes[row, col].imshow(img, cmap='gray')
                axes[row, col].set_title(
                    f'{title}\n'
                    f'Por: {porosity:.1f}% | Dens: {density:.1f}% | Frat: {fractures}',
                    fontsize=10, fontweight='bold'
                )
                axes[row, col].axis('off')
                
                # Adicionar escala (assumindo 100 pixels = escala conhecida)
                scale_length = 100
                axes[row, col].plot([20, 20 + scale_length], [img.shape[0] - 30, img.shape[0] - 30],
                                   'w-', linewidth=3)
                axes[row, col].text(20 + scale_length/2, img.shape[0] - 40, '100 μm',
                                   color='white', fontsize=8, ha='center',
                                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
            else:
                axes[row, col].text(0.5, 0.5, f'Imagem não encontrada\n{key}',
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        
        # Salvar
        fig_path = self.results_dir / "figura_comparativa_manuscrito.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Figura comparativa salva: {fig_path}")
        
        # Criar figuras horizontais aprimoradas
        self.create_original_mev_figure(results)
        self.create_fracture_analysis_figure(results)
        
        # Criar também versão com overlay de análises
        self.create_comparative_figure_with_overlays(results)
    
    def create_original_mev_figure(self, results):
        """Cria figura horizontal com imagens MEV originais (2×4)"""
        print("  → Gerando figura MEV originais...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        fig.suptitle('Imagens MEV: Typha domingensis e Syagrus coronata',
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Configuração: (fibra, chave, row, col, letra, título)
        images_config = [
            ('taboa', 'taboa_ST_30d', 0, 0, 'a', 'Typha - ST 30d'),
            ('taboa', 'taboa_ST_180d', 0, 1, 'b', 'Typha - ST 180d'),
            ('taboa', 'taboa_DC_30d', 0, 2, 'c', 'Typha - DC 30d'),
            ('taboa', 'taboa_DC_180d', 0, 3, 'd', 'Typha - DC 180d'),
            ('ouricuri', 'ouricuri_ST_30d', 1, 0, 'e', 'Syagrus - ST 30d'),
            ('ouricuri', 'ouricuri_ST_180d', 1, 1, 'f', 'Syagrus - ST 180d'),
            ('ouricuri', 'ouricuri_DC_30d', 1, 2, 'g', 'Syagrus - DC 30d'),
            ('ouricuri', 'ouricuri_DC_180d', 1, 3, 'h', 'Syagrus - DC 180d'),
        ]
        
        for fiber, key, row, col, letter, title in images_config:
            img_path = self.selected_dir / fiber / f"{key}.png"
            
            if img_path.exists():
                img = self.load_image(img_path)
                axes[row, col].imshow(img, cmap='gray')
                axes[row, col].set_title(title, fontsize=11, fontweight='bold', pad=10)
                axes[row, col].axis('off')
                
                # Adicionar letra de identificação
                axes[row, col].text(0.02, 0.98, f'({letter})',
                                   transform=axes[row, col].transAxes,
                                   fontsize=14, fontweight='bold',
                                   verticalalignment='top',
                                   bbox=dict(boxstyle='round', facecolor='white', 
                                           edgecolor='black', linewidth=2, alpha=0.9))
                
                # Adicionar métricas básicas
                data = results[fiber].get(key, {})
                porosity = data.get('porosity', {}).get('porosity_pct', 0)
                rugosidade = data.get('texture', {}).get('mean_surface_roughness', 0)
                
                metrics_text = f'Poros: {porosity:.1f}%\nRugosidade: {rugosidade:.0f}'
                axes[row, col].text(0.98, 0.02, metrics_text,
                                   transform=axes[row, col].transAxes,
                                   fontsize=9, ha='right', va='bottom',
                                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            else:
                axes[row, col].text(0.5, 0.5, f'Imagem não encontrada\n{key}',
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        fig_path = self.results_dir / "figura_mev_originais.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Figura MEV originais salva: {fig_path}")
    
    def create_fracture_analysis_figure(self, results):
        """Cria figura horizontal com análise de fraturas (2×4)"""
        print("  → Gerando figura análise de fraturas...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        fig.suptitle('Análise de Fraturas e Danos Superficiais',
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Configuração: (fibra, chave, row, col, letra, título)
        images_config = [
            ('taboa', 'taboa_ST_30d', 0, 0, 'a', 'Typha - ST 30d'),
            ('taboa', 'taboa_ST_180d', 0, 1, 'b', 'Typha - ST 180d'),
            ('taboa', 'taboa_DC_30d', 0, 2, 'c', 'Typha - DC 30d'),
            ('taboa', 'taboa_DC_180d', 0, 3, 'd', 'Typha - DC 180d'),
            ('ouricuri', 'ouricuri_ST_30d', 1, 0, 'e', 'Syagrus - ST 30d'),
            ('ouricuri', 'ouricuri_ST_180d', 1, 1, 'f', 'Syagrus - ST 180d'),
            ('ouricuri', 'ouricuri_DC_30d', 1, 2, 'g', 'Syagrus - DC 30d'),
            ('ouricuri', 'ouricuri_DC_180d', 1, 3, 'h', 'Syagrus - DC 180d'),
        ]
        
        for fiber, key, row, col, letter, title in images_config:
            img_path = self.selected_dir / fiber / f"{key}.png"
            
            if img_path.exists():
                img = self.load_image(img_path)
                
                # Detectar fraturas (threshold + skeletonização)
                _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
                kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_CLOSE, kernel_clean)
                skeleton_fractures = morphology.skeletonize(dark_regions > 0)
                
                # Overlay triplo
                axes[row, col].imshow(img, cmap='gray', alpha=0.7)
                axes[row, col].imshow(dark_regions, cmap='Reds', alpha=0.4)
                axes[row, col].imshow(skeleton_fractures, cmap='hot', alpha=0.6)
                
                axes[row, col].set_title(title, fontsize=11, fontweight='bold', pad=10)
                axes[row, col].axis('off')
                
                # Adicionar letra de identificação
                axes[row, col].text(0.02, 0.98, f'({letter})',
                                   transform=axes[row, col].transAxes,
                                   fontsize=14, fontweight='bold',
                                   verticalalignment='top',
                                   bbox=dict(boxstyle='round', facecolor='white', 
                                           edgecolor='black', linewidth=2, alpha=0.9))
                
                # Adicionar métricas de fraturas
                data = results[fiber].get(key, {})
                fractures = data.get('fractures', {}).get('num_fractures', 0)
                severity = data.get('fractures', {}).get('damage_severity', 0)
                severity_class = data.get('fractures', {}).get('severity_class', 'N/A')
                frac_length = data.get('fractures', {}).get('fracture_length', 0)
                
                metrics_text = f'Fraturas: {fractures}\nComprimento: {frac_length} px\nSeveridade: {severity:.1f}%\nClasse: {severity_class}'
                axes[row, col].text(0.98, 0.02, metrics_text,
                                   transform=axes[row, col].transAxes,
                                   fontsize=9, ha='right', va='bottom',
                                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.85))
            else:
                axes[row, col].text(0.5, 0.5, f'Imagem não encontrada\n{key}',
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        fig_path = self.results_dir / "figura_analise_fraturas.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Figura análise de fraturas salva: {fig_path}")
    
    def create_comparative_figure_with_overlays(self, results):
        """Cria figura comparativa com overlays de análise"""
        print("Gerando figura com overlays de análise...")
        
        fig, axes = plt.subplots(4, 4, figsize=(20, 16))
        fig.suptitle('Análise Morfométrica Detalhada: Original | Poros | Skeleton | Fraturas',
                     fontsize=14, fontweight='bold')
        
        fibers_config = [
            ('taboa', 'taboa_ST_30d', 0, 'Taboa ST 30d'),
            ('taboa', 'taboa_DC_180d', 1, 'Taboa DC 180d'),
            ('ouricuri', 'ouricuri_ST_30d', 2, 'Ouricuri ST 30d'),
            ('ouricuri', 'ouricuri_DC_180d', 3, 'Ouricuri DC 180d'),
        ]
        
        for fiber, key, row, title in fibers_config:
            img_path = self.selected_dir / fiber / f"{key}.png"
            
            if not img_path.exists():
                continue
            
            img = self.load_image(img_path)
            
            # 1. Original
            axes[row, 0].imshow(img, cmap='gray')
            axes[row, 0].set_title(f'{title}\nOriginal', fontsize=10)
            axes[row, 0].axis('off')
            
            # 2. Poros
            _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            pores = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            axes[row, 1].imshow(img, cmap='gray', alpha=0.7)
            axes[row, 1].imshow(pores, cmap='Reds', alpha=0.5)
            
            data = results[fiber].get(key, {})
            porosity = data.get('porosity', {}).get('porosity_pct', 0)
            num_pores = data.get('porosity', {}).get('num_pores', 0)
            
            axes[row, 1].set_title(f'Porosidade\n{porosity:.1f}% ({num_pores} poros)', fontsize=10)
            axes[row, 1].axis('off')
            
            # 3. Skeleton
            binary_struct = cv2.adaptiveThreshold(
                img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            skeleton = morphology.skeletonize(binary_struct > 0)
            
            axes[row, 2].imshow(img, cmap='gray', alpha=0.6)
            axes[row, 2].imshow(skeleton, cmap='hot', alpha=0.7)
            
            density = data.get('structure', {}).get('fibril_density', 0)
            junctions = data.get('structure', {}).get('num_junctions', 0)
            
            axes[row, 2].set_title(f'Estrutura Fibrilar\n{density:.1f}% ({junctions} jun.)', fontsize=10)
            axes[row, 2].axis('off')
            
            # 4. Fraturas (usando método threshold + skeletonização)
            # Detectar regiões escuras (fraturas abertas)
            _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
            kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_CLOSE, kernel_clean)
            
            # Skeletonizar para representar comprimento
            skeleton_fractures = morphology.skeletonize(dark_regions > 0)
            
            axes[row, 3].imshow(img, cmap='gray', alpha=0.7)
            axes[row, 3].imshow(dark_regions, cmap='Reds', alpha=0.4)
            axes[row, 3].imshow(skeleton_fractures, cmap='hot', alpha=0.6)
            
            fractures = data.get('fractures', {}).get('num_fractures', 0)
            severity = data.get('fractures', {}).get('damage_severity', 0)
            severity_class = data.get('fractures', {}).get('severity_class', 'N/A')
            
            axes[row, 3].set_title(f'Fraturas/Danos\n{fractures} frat. ({severity:.2f}%) {severity_class}', fontsize=10)
            axes[row, 3].axis('off')
        
        plt.tight_layout()
        
        # Salvar
        fig_path = self.results_dir / "figura_analise_overlays_detalhada.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Figura com overlays detalhada salva: {fig_path}")
    
    def create_bar_chart_comparisons(self, results):
        """Cria gráficos de barras comparativos entre tratamentos e períodos"""
        print("Gerando gráficos de barras comparativos...")
        
        # Preparar dados
        metrics = {
            'Porosidade (%)': ('porosity', 'porosity_pct'),
            'Densidade Fibrilar (%)': ('structure', 'fibril_density'),
            'Número de Junções': ('structure', 'num_junctions'),
            'Contraste GLCM': ('texture', 'glcm_contrast'),
            'Rugosidade Média': ('texture', 'mean_surface_roughness'),
            'Número de Fraturas': ('fractures', 'num_fractures'),
        }
        
        for fiber in ['taboa', 'ouricuri']:
            fiber_name = 'Typha domingensis' if fiber == 'taboa' else 'Syagrus coronata'
            
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'Comparação Morfométrica: {fiber_name}', fontsize=16, fontweight='bold')
            
            axes_flat = axes.flatten()
            
            for idx, (metric_name, (category, key)) in enumerate(metrics.items()):
                ax = axes_flat[idx]
                
                # Extrair valores
                st_30 = results[fiber].get(f'{fiber}_ST_30d', {}).get(category, {}).get(key, 0)
                st_180 = results[fiber].get(f'{fiber}_ST_180d', {}).get(category, {}).get(key, 0)
                dc_30 = results[fiber].get(f'{fiber}_DC_30d', {}).get(category, {}).get(key, 0)
                dc_180 = results[fiber].get(f'{fiber}_DC_180d', {}).get(category, {}).get(key, 0)
                
                # Posições das barras
                x = np.arange(2)  # 30d e 180d
                width = 0.35
                
                # Criar barras
                bars1 = ax.bar(x - width/2, [st_30, st_180], width, 
                              label='Sem Tratamento', color='coral', alpha=0.8)
                bars2 = ax.bar(x + width/2, [dc_30, dc_180], width,
                              label='Dupla Camada', color='skyblue', alpha=0.8)
                
                # Adicionar valores nas barras
                for bars in [bars1, bars2]:
                    for bar in bars:
                        height = bar.get_height()
                        if height > 1000:
                            label = f'{int(height)}'
                        elif height > 10:
                            label = f'{height:.1f}'
                        else:
                            label = f'{height:.2f}'
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               label, ha='center', va='bottom', fontsize=9, fontweight='bold')
                
                ax.set_ylabel(metric_name, fontsize=10, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(['30 dias', '180 dias'])
                ax.legend(fontsize=9)
                ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            # Salvar
            chart_path = self.results_dir / f"graficos_comparativos_{fiber}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  → {fiber_name}: {chart_path.name}")
    
    def create_comparison_evolution_charts(self, results):
        """Cria gráficos de evolução temporal comparando as duas fibras"""
        print("Gerando gráficos de evolução temporal...")
        
        metrics = [
            ('Porosidade (%)', 'porosity', 'porosity_pct'),
            ('Densidade Fibrilar (%)', 'structure', 'fibril_density'),
            ('Contraste GLCM', 'texture', 'glcm_contrast'),
            ('Rugosidade Média', 'texture', 'mean_surface_roughness'),
        ]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Evolução Temporal: Taboa vs Ouricuri', fontsize=16, fontweight='bold')
        
        axes_flat = axes.flatten()
        
        for idx, (metric_name, category, key) in enumerate(metrics):
            ax = axes_flat[idx]
            
            # Taboa Sem Tratamento
            taboa_st_30 = results['taboa'].get('taboa_ST_30d', {}).get(category, {}).get(key, 0)
            taboa_st_180 = results['taboa'].get('taboa_ST_180d', {}).get(category, {}).get(key, 0)
            
            # Taboa Dupla Camada
            taboa_dc_30 = results['taboa'].get('taboa_DC_30d', {}).get(category, {}).get(key, 0)
            taboa_dc_180 = results['taboa'].get('taboa_DC_180d', {}).get(category, {}).get(key, 0)
            
            # Ouricuri Sem Tratamento
            ouricuri_st_30 = results['ouricuri'].get('ouricuri_ST_30d', {}).get(category, {}).get(key, 0)
            ouricuri_st_180 = results['ouricuri'].get('ouricuri_ST_180d', {}).get(category, {}).get(key, 0)
            
            # Ouricuri Dupla Camada
            ouricuri_dc_30 = results['ouricuri'].get('ouricuri_DC_30d', {}).get(category, {}).get(key, 0)
            ouricuri_dc_180 = results['ouricuri'].get('ouricuri_DC_180d', {}).get(category, {}).get(key, 0)
            
            # Plotar linhas
            periods = [30, 180]
            
            ax.plot(periods, [taboa_st_30, taboa_st_180], 'o-', color='coral', 
                   linewidth=2, markersize=8, label='Taboa ST')
            ax.plot(periods, [taboa_dc_30, taboa_dc_180], 's-', color='lightcoral', 
                   linewidth=2, markersize=8, label='Taboa DC')
            ax.plot(periods, [ouricuri_st_30, ouricuri_st_180], 'o-', color='skyblue', 
                   linewidth=2, markersize=8, label='Ouricuri ST')
            ax.plot(periods, [ouricuri_dc_30, ouricuri_dc_180], 's-', color='steelblue', 
                   linewidth=2, markersize=8, label='Ouricuri DC')
            
            ax.set_xlabel('Período (dias)', fontsize=11, fontweight='bold')
            ax.set_ylabel(metric_name, fontsize=11, fontweight='bold')
            ax.set_xticks(periods)
            ax.legend(fontsize=9, loc='best')
            ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Salvar
        evolution_path = self.results_dir / "graficos_evolucao_temporal.png"
        plt.savefig(evolution_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  → Evolução temporal: {evolution_path.name}\n")


def main():
    """Execução principal"""
    analyzer = ComprehensiveMEVAnalyzer()
    
    # Análise completa
    results = analyzer.analyze_all_selected_images()
    
    # Gerar tabela comparativa
    analyzer.generate_comparison_table(results)
    
    # Gerar figuras comparativas
    analyzer.create_comparative_figure(results)
    
    # Gerar gráficos de barras comparativos
    analyzer.create_bar_chart_comparisons(results)
    
    # Gerar gráficos de evolução temporal
    analyzer.create_comparison_evolution_charts(results)
    
    print("\n" + "="*70)
    print(" ANÁLISE CONCLUÍDA!")
    print("="*70)
    print("\nArquivos gerados:")
    print("1. analise_morfometrica_completa.json - Dados brutos completos")
    print("2. tabela_comparativa_manuscrito.md - Tabela formatada para o artigo")
    print("3. [nome]_analise.png (8 arquivos) - Análises individuais detalhadas")
    print("4. figura_comparativa_manuscrito.png - Painel 4×2 comparativo")
    print("5. figura_mev_originais.png - Imagens MEV originais 2×4 horizontal (a-h)")
    print("6. figura_analise_fraturas.png - Análise de fraturas 2×4 horizontal (a-h)")
    print("7. figura_analise_overlays_detalhada.png - Análises com overlays (4 amostras)")
    print("8. graficos_comparativos_taboa.png - Gráficos de barras Taboa")
    print("9. graficos_comparativos_ouricuri.png - Gráficos de barras Ouricuri")
    print("10. graficos_evolucao_temporal.png - Evolução temporal comparativa")
    print("\nPróximos passos:")
    print("- Integrar dados na Tabela 2 do manuscrito")
    print("- Inserir figuras comparativas no artigo (Figura X: MEV originais, Figura Y: Fraturas)")
    print("- Adicionar legenda detalhada para as marcações (a) a (h)")


if __name__ == "__main__":
    main()
    print("8. graficos_evolucao_temporal.png - Evolução temporal comparativa")
    print("\nPróximos passos:")
    print("- Integrar dados na Tabela 2 do manuscrito")
    print("- Inserir figuras comparativas no artigo")
    print("- Adicionar legenda e escala nas figuras")


if __name__ == "__main__":
    main()
