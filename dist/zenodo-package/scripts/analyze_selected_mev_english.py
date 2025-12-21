"""
Comprehensive Morphometric Analysis of Selected SEM Images
==========================================================

Processes the 8 selected images (Typha and Syagrus, 30d and 180d, Untreated and Double Layer)
and generates complete morphometric data for manuscript integration.
English Version.

Analyzed parameters:
- Fiber orientation (mean angle, deviation, orientation index)
- Surface porosity (%, mean area, circularity)
- Fibrillar structure (density, junctions, skeleton length)
- Surface texture (GLCM: contrast, homogeneity, energy, correlation)
- Roughness (mean, deviation, maximum)
- Fracture/damage patterns (detected via contours and morphology)

Author: Diego Vidal
Date: December 2025
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
    """Comprehensive morphometric analyzer for SEM images"""
    
    def __init__(self, selected_dir=None):
        if selected_dir is None:
            # Relative path to current file
            script_dir = Path(__file__).parent
            selected_dir = script_dir.parent / "5-DADOS" / "MEV-ANALISE" / "imagens-selecionadas"
        
        self.selected_dir = Path(selected_dir)
        self.results_dir = self.selected_dir.parent / "resultados_en"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def load_image(self, image_path):
        """Loads and preprocesses image"""
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Error loading: {image_path}")
        
        # Normalize to 0-255
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        return img
    
    def analyze_fiber_orientation(self, img):
        """
        Fiber orientation analysis using Sobel gradients
        Returns: mean angle, standard deviation, orientation index (0-1)
        """
        # Sobel gradients
        sobel_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        
        # Magnitude and angle
        magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        angle = np.arctan2(sobel_y, sobel_x) * 180 / np.pi
        
        # Filter weak gradients
        threshold = np.percentile(magnitude, 75)
        mask = magnitude > threshold
        
        valid_angles = angle[mask]
        
        if len(valid_angles) == 0:
            return {'mean_angle': 0, 'std_angle': 0, 'orientation_index': 0}
        
        # Statistics
        mean_angle = np.mean(valid_angles)
        std_angle = np.std(valid_angles)
        
        # Orientation index (0=random, 1=perfectly oriented)
        orientation_index = 1 - (std_angle / 90.0) if std_angle <= 90 else 0
        
        return {
            'mean_angle': float(mean_angle),
            'std_angle': float(std_angle),
            'orientation_index': float(np.clip(orientation_index, 0, 1))
        }
    
    def analyze_surface_porosity(self, img):
        """
        Surface porosity analysis using Otsu threshold
        Returns: % porosity, number of pores, mean area, circularity
        """
        # Otsu Threshold
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological cleaning
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary_clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Metrics
        total_pixels = img.size
        pore_pixels = np.count_nonzero(binary_clean)
        porosity_pct = (pore_pixels / total_pixels) * 100
        
        # Connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_clean)
        
        areas = stats[1:, cv2.CC_STAT_AREA]  # Ignore background
        if len(areas) > 0:
            mean_area = np.mean(areas)
            
            # Circularity
            contours, _ = cv2.findContours(binary_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            circularities = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circ = 4 * np.pi * area / (perimeter * perimeter)
                    circularities.append(circ)
            mean_circularity = np.mean(circularities) if circularities else 0
        else:
            mean_area = 0
            mean_circularity = 0
            
        return {
            'porosity_pct': float(porosity_pct),
            'num_pores': int(num_labels - 1),
            'mean_pore_area': float(mean_area),
            'mean_circularity': float(mean_circularity)
        }

    def analyze_fibrillar_structure(self, img):
        """
        Fibrillar structure analysis using skeletonization
        Returns: fibril density, number of junctions, skeletal length
        """
        # Adaptive binarization to capture fibers
        binary = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Skeletonization
        skeleton = morphology.skeletonize(binary > 0)
        
        # Density
        fibril_density = (np.count_nonzero(skeleton) / skeleton.size) * 100
        
        # Junctions (using convolution)
        # Kernel for junction detection
        # 1 1 1
        # 1 10 1
        # 1 1 1
        # If sum >= 13 (center=10 + at least 3 neighbors), it's a junction
        skeleton_int = skeleton.astype(np.uint8)
        kernel = np.array([[1, 1, 1], [1, 10, 1], [1, 1, 1]], dtype=np.uint8)
        filtered = cv2.filter2D(skeleton_int, -1, kernel)
        
        junctions = np.count_nonzero(filtered >= 13)
        skeletal_length = np.count_nonzero(skeleton)
        
        return {
            'fibril_density': float(fibril_density),
            'num_junctions': int(junctions),
            'skeletal_length': int(skeletal_length)
        }

    def analyze_texture_glcm(self, img):
        """
        Texture analysis using GLCM (Gray-Level Co-occurrence Matrix)
        Returns: contrast, homogeneity, energy, correlation
        """
        # GLCM requires uint8
        glcm = graycomatrix(img, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
                           levels=256, symmetric=True, normed=True)
        
        contrast = graycoprops(glcm, 'contrast').mean()
        homogeneity = graycoprops(glcm, 'homogeneity').mean()
        energy = graycoprops(glcm, 'energy').mean()
        correlation = graycoprops(glcm, 'correlation').mean()
        
        return {
            'glcm_contrast': float(contrast),
            'glcm_homogeneity': float(homogeneity),
            'glcm_energy': float(energy),
            'glcm_correlation': float(correlation)
        }

    def analyze_roughness(self, img):
        """
        Surface roughness analysis
        Returns: mean roughness (Ra), standard deviation (Rq), maximum
        """
        # Roughness as local standard deviation
        img_float = img.astype(float)
        local_mean = generic_filter(img_float, np.mean, size=5)
        local_sqr_mean = generic_filter(img_float**2, np.mean, size=5)
        local_std = np.sqrt(np.maximum(local_sqr_mean - local_mean**2, 0))
        
        mean_roughness = np.mean(local_std)
        std_roughness = np.std(local_std)
        max_roughness = np.max(local_std)
        
        return {
            'mean_surface_roughness': float(mean_roughness),
            'std_surface_roughness': float(std_roughness),
            'max_surface_roughness': float(max_roughness)
        }

    def analyze_fractures_damage(self, img):
        """
        Analysis of fractures and surface damage
        Returns: number of fractures, damage severity, classification
        """
        # Detect dark regions (potential fractures/holes)
        _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Clean noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_CLOSE, kernel)
        
        # Count connected components (fractures)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dark_regions)
        num_fractures = num_labels - 1
        
        # Damage severity (% area)
        total_area = img.size
        damaged_area = np.count_nonzero(dark_regions)
        severity_pct = (damaged_area / total_area) * 100
        
        # Classification
        if severity_pct < 0.5:
            classification = "Mild"
        elif severity_pct < 2.0:
            classification = "Moderate"
        elif severity_pct < 5.0:
            classification = "Severe"
        else:
            classification = "Critical"
            
        return {
            'num_fractures': int(num_fractures),
            'damage_severity': float(severity_pct),
            'severity_class': classification
        }

    def analyze_all_selected_images(self):
        """Executes complete analysis for all 8 selected images"""
        print("Starting analysis of selected images...")
        
        # Configuration of images to analyze
        # Structure: fiber / filename (without extension)
        images_config = {
            'taboa': [
                'taboa_ST_30d', 'taboa_ST_180d',
                'taboa_DC_30d', 'taboa_DC_180d'
            ],
            'ouricuri': [
                'ouricuri_ST_30d', 'ouricuri_ST_180d',
                'ouricuri_DC_30d', 'ouricuri_DC_180d'
            ]
        }
        
        results = {'taboa': {}, 'ouricuri': {}}
        
        for fiber, filenames in images_config.items():
            print(f"\nAnalyzing {fiber}...")
            fiber_dir = self.selected_dir / fiber
            
            if not fiber_dir.exists():
                print(f"  WARNING: Directory not found: {fiber_dir}")
                continue
                
            for fname in filenames:
                # Try extensions
                img_path = None
                for ext in ['.png', '.tif', '.jpg']:
                    p = fiber_dir / f"{fname}{ext}"
                    if p.exists():
                        img_path = p
                        break
                
                if img_path:
                    print(f"  Processing: {fname}")
                    img = self.load_image(img_path)
                    
                    # Execute all analyses
                    orientation = self.analyze_fiber_orientation(img)
                    porosity = self.analyze_surface_porosity(img)
                    structure = self.analyze_fibrillar_structure(img)
                    texture = self.analyze_texture_glcm(img)
                    roughness = self.analyze_roughness(img)
                    fractures = self.analyze_fractures_damage(img)
                    
                    # Store results
                    results[fiber][fname] = {
                        'orientation': orientation,
                        'porosity': porosity,
                        'structure': structure,
                        'texture': texture,
                        'roughness': roughness,
                        'fractures': fractures
                    }
                else:
                    print(f"  ERROR: Image not found: {fname}")
        
        # Save JSON results
        json_path = self.results_dir / "morphometric_results_complete_en.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {json_path}")
        
        # Generate figures
        self.create_comparative_figure_with_overlays(results)
        self.create_bar_chart_comparisons(results)
        self.create_comparison_evolution_charts(results)
        self.create_original_mev_figure(results)
        self.create_fracture_analysis_figure(results)
        
        return results

    def create_comparative_figure_with_overlays(self, results):
        """Creates comparative figure with analysis overlays (2x4 grid)"""
        print("Generating comparative figure with overlays...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        fig.suptitle('Morphometric Analysis: Typha domingensis vs Syagrus coronata', 
                    fontsize=16, fontweight='bold')
        
        # Configuration: (fiber, key, row, col, title)
        images_config = [
            ('taboa', 'taboa_ST_30d', 0, 0, 'Typha - Untreated 30d'),
            ('taboa', 'taboa_ST_180d', 0, 1, 'Typha - Untreated 180d'),
            ('taboa', 'taboa_DC_30d', 0, 2, 'Typha - Double Layer 30d'),
            ('taboa', 'taboa_DC_180d', 0, 3, 'Typha - Double Layer 180d'),
            ('ouricuri', 'ouricuri_ST_30d', 1, 0, 'Syagrus - Untreated 30d'),
            ('ouricuri', 'ouricuri_ST_180d', 1, 1, 'Syagrus - Untreated 180d'),
            ('ouricuri', 'ouricuri_DC_30d', 1, 2, 'Syagrus - Double Layer 30d'),
            ('ouricuri', 'ouricuri_DC_180d', 1, 3, 'Syagrus - Double Layer 180d'),
        ]
        
        for fiber, key, row, col, title in images_config:
            img_path = self.selected_dir / fiber / f"{key}.png"
            
            if img_path.exists():
                img = self.load_image(img_path)
                
                # Morphometric data
                data = results[fiber].get(key, {})
                porosity = data.get('porosity', {}).get('porosity_pct', 0)
                density = data.get('structure', {}).get('fibril_density', 0)
                fractures = data.get('fractures', {}).get('num_fractures', 0)
                
                axes[row, col].imshow(img, cmap='gray')
                axes[row, col].set_title(
                    f'{title}\n'
                    f'Por: {porosity:.1f}% | Dens: {density:.1f}% | Frac: {fractures}',
                    fontsize=10, fontweight='bold'
                )
                axes[row, col].axis('off')
                
                # Add scale (assuming 100 pixels = known scale)
                scale_length = 100
                axes[row, col].plot([20, 20 + scale_length], [img.shape[0] - 30, img.shape[0] - 30], 
                                   'w-', linewidth=3)
                axes[row, col].text(20 + scale_length/2, img.shape[0] - 40, '100 μm', 
                                   color='white', fontsize=8, ha='center',
                                   bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
            else:
                axes[row, col].text(0.5, 0.5, f'Image not found\n{key}', 
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        
        # Save
        fig_path = self.results_dir / "comparative_figure_manuscript_en.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Comparative figure saved: {fig_path}")
    
    def create_original_mev_figure(self, results):
        """Creates horizontal figure with original SEM images (2x4)"""
        print("  → Generating original SEM figure...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        fig.suptitle('SEM Images: Typha domingensis and Syagrus coronata', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Configuration: (fiber, key, row, col, letter, title)
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
                
                # Add identification letter
                axes[row, col].text(0.02, 0.98, f'({letter})', 
                                   transform=axes[row, col].transAxes, 
                                   fontsize=14, fontweight='bold', 
                                   verticalalignment='top',
                                   bbox=dict(boxstyle='round', facecolor='white', 
                                           edgecolor='black', linewidth=2, alpha=0.9))
                
                # Add basic metrics
                data = results[fiber].get(key, {})
                porosity = data.get('porosity', {}).get('porosity_pct', 0)
                rugosidade = data.get('texture', {}).get('mean_surface_roughness', 0)
                
                metrics_text = f'Pores: {porosity:.1f}%\nRoughness: {rugosidade:.0f}'
                axes[row, col].text(0.98, 0.02, metrics_text, 
                                   transform=axes[row, col].transAxes, 
                                   fontsize=9, ha='right', va='bottom',
                                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            else:
                axes[row, col].text(0.5, 0.5, f'Image not found\n{key}', 
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        fig_path = self.results_dir / "figure_mev_originals_en.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Original SEM figure saved: {fig_path}")
    
    def create_fracture_analysis_figure(self, results):
        """Creates horizontal figure with fracture analysis (2x4)"""
        print("  → Generating fracture analysis figure...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        fig.suptitle('Fracture and Surface Damage Analysis', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Configuration: (fiber, key, row, col, letter, title)
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
                
                # Detect fractures (threshold + skeletonization)
                _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
                kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_CLOSE, kernel_clean)
                skeleton_fractures = morphology.skeletonize(dark_regions > 0)
                
                # Triple overlay
                axes[row, col].imshow(img, cmap='gray', alpha=0.7)
                axes[row, col].imshow(dark_regions, cmap='Reds', alpha=0.4)
                axes[row, col].imshow(skeleton_fractures, cmap='hot', alpha=0.6)
                
                axes[row, col].set_title(title, fontsize=11, fontweight='bold', pad=10)
                axes[row, col].axis('off')
                
                # Add identification letter
                axes[row, col].text(0.02, 0.98, f'({letter})', 
                                   transform=axes[row, col].transAxes, 
                                   fontsize=14, fontweight='bold', 
                                   verticalalignment='top',
                                   bbox=dict(boxstyle='round', facecolor='white', 
                                           edgecolor='black', linewidth=2, alpha=0.9))
                
                # Add metrics
                data = results[fiber].get(key, {})
                fractures = data.get('fractures', {}).get('num_fractures', 0)
                severity = data.get('fractures', {}).get('damage_severity', 0)
                
                metrics_text = f'Fractures: {fractures}\nSeverity: {severity:.1f}%'
                axes[row, col].text(0.98, 0.02, metrics_text, 
                                   transform=axes[row, col].transAxes, 
                                   fontsize=9, ha='right', va='bottom',
                                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            else:
                axes[row, col].text(0.5, 0.5, f'Image not found\n{key}', 
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        fig_path = self.results_dir / "figure_fracture_analysis_en.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Fracture analysis figure saved: {fig_path}")

    def create_bar_chart_comparisons(self, results):
        """Creates comparative bar charts between treatments and periods"""
        print("Generating comparative bar charts...")
        
        # Prepare data
        metrics = {
            'Porosity (%)': ('porosity', 'porosity_pct'),
            'Fibrillar Density (%)': ('structure', 'fibril_density'),
            'Number of Junctions': ('structure', 'num_junctions'),
            'GLCM Contrast': ('texture', 'glcm_contrast'),
            'Mean Roughness': ('texture', 'mean_surface_roughness'),
            'Number of Fractures': ('fractures', 'num_fractures'),
        }
        
        for fiber in ['taboa', 'ouricuri']:
            fiber_name = 'Typha domingensis' if fiber == 'taboa' else 'Syagrus coronata'
            
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'Morphometric Comparison: {fiber_name}', fontsize=16, fontweight='bold')
            
            axes_flat = axes.flatten()
            
            for idx, (metric_name, (category, key)) in enumerate(metrics.items()):
                ax = axes_flat[idx]
                
                # Extract values
                st_30 = results[fiber].get(f'{fiber}_ST_30d', {}).get(category, {}).get(key, 0)
                st_180 = results[fiber].get(f'{fiber}_ST_180d', {}).get(category, {}).get(key, 0)
                dc_30 = results[fiber].get(f'{fiber}_DC_30d', {}).get(category, {}).get(key, 0)
                dc_180 = results[fiber].get(f'{fiber}_DC_180d', {}).get(category, {}).get(key, 0)
                
                # Bar positions
                x = np.arange(2)  # 30d and 180d
                width = 0.35
                
                # Create bars
                bars1 = ax.bar(x - width/2, [st_30, st_180], width, 
                              label='Untreated', color='coral', alpha=0.8)
                bars2 = ax.bar(x + width/2, [dc_30, dc_180], width,
                              label='Double Layer', color='skyblue', alpha=0.8)
                
                # Add values on bars
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
                ax.set_xticklabels(['30 days', '180 days'])
                ax.legend(fontsize=9)
                ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            
            # Save
            chart_path = self.results_dir / f"comparative_charts_{fiber}_en.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  → {fiber_name}: {chart_path.name}")
    
    def create_comparison_evolution_charts(self, results):
        """Creates temporal evolution charts comparing both fibers"""
        print("Generating temporal evolution charts...")
        
        metrics = [
            ('Porosity (%)', 'porosity', 'porosity_pct'),
            ('Fibrillar Density (%)', 'structure', 'fibril_density'),
            ('GLCM Contrast', 'texture', 'glcm_contrast'),
            ('Mean Roughness', 'texture', 'mean_surface_roughness'),
        ]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Temporal Evolution: Typha vs Syagrus', fontsize=16, fontweight='bold')
        
        axes_flat = axes.flatten()
        
        for idx, (metric_name, category, key) in enumerate(metrics):
            ax = axes_flat[idx]
            
            # Typha Untreated
            taboa_st_30 = results['taboa'].get('taboa_ST_30d', {}).get(category, {}).get(key, 0)
            taboa_st_180 = results['taboa'].get('taboa_ST_180d', {}).get(category, {}).get(key, 0)
            
            # Typha Double Layer
            taboa_dc_30 = results['taboa'].get('taboa_DC_30d', {}).get(category, {}).get(key, 0)
            taboa_dc_180 = results['taboa'].get('taboa_DC_180d', {}).get(category, {}).get(key, 0)
            
            # Syagrus Untreated
            ouricuri_st_30 = results['ouricuri'].get('ouricuri_ST_30d', {}).get(category, {}).get(key, 0)
            ouricuri_st_180 = results['ouricuri'].get('ouricuri_ST_180d', {}).get(category, {}).get(key, 0)
            
            # Syagrus Double Layer
            ouricuri_dc_30 = results['ouricuri'].get('ouricuri_DC_30d', {}).get(category, {}).get(key, 0)
            ouricuri_dc_180 = results['ouricuri'].get('ouricuri_DC_180d', {}).get(category, {}).get(key, 0)
            
            # Plot lines
            periods = [30, 180]
            
            ax.plot(periods, [taboa_st_30, taboa_st_180], 'o-', color='coral', 
                   linewidth=2, markersize=8, label='Typha ST')
            ax.plot(periods, [taboa_dc_30, taboa_dc_180], 's-', color='lightcoral', 
                   linewidth=2, markersize=8, label='Typha DC')
            ax.plot(periods, [ouricuri_st_30, ouricuri_st_180], 'o-', color='skyblue', 
                   linewidth=2, markersize=8, label='Syagrus ST')
            ax.plot(periods, [ouricuri_dc_30, ouricuri_dc_180], 's-', color='steelblue', 
                   linewidth=2, markersize=8, label='Syagrus DC')
            
            ax.set_xlabel('Period (days)', fontsize=11, fontweight='bold')
            ax.set_ylabel(metric_name, fontsize=11, fontweight='bold')
            ax.set_xticks(periods)
            ax.legend(fontsize=9, loc='best')
            ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Save
        evolution_path = self.results_dir / "temporal_evolution_charts_en.png"
        plt.savefig(evolution_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  → Temporal evolution: {evolution_path.name}\n")


def main():
    """Main execution"""
    analyzer = ComprehensiveMEVAnalyzer()
    
    # Complete analysis
    results = analyzer.analyze_all_selected_images()
    
    print("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()
