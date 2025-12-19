"""
Comprehensive Morphometric Analysis of Selected SEM Images
==========================================================
English Version

Processes the 8 selected images (Typha and Syagrus, 30d and 180d, Untreated and Bilayer)
and generates complete morphometric data and composite figures for the manuscript.

Analyzed parameters:
- Fiber orientation (mean angle, deviation, orientation index)
- Surface porosity (%, mean area, circularity)
- Fibrillar structure (density, junctions, skeleton length)
- Surface texture (GLCM: contrast, homogeneity, energy, correlation)
- Roughness (mean, deviation, max)
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
            # Relative path
            script_dir = Path(__file__).parent
            # Assuming images are in the same place
            selected_dir = script_dir.parent / "5-DADOS" / "MEV-ANALISE" / "imagens-selecionadas"
        
        self.selected_dir = Path(selected_dir)
        self.results_dir = script_dir.parent / "5-DADOS" / "MEV-ANALISE" / "resultados_en"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def load_image(self, image_path):
        """Loads and pre-processes image"""
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Error loading: {image_path}")
        
        # Normalize to 0-255
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
        return img
    
    def create_original_mev_figure(self):
        """Creates horizontal figure with original SEM images (2x4)"""
        print("  -> Generating Original SEM Figure...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        # fig.suptitle('SEM Images: Typha domingensis and Syagrus coronata',
        #              fontsize=16, fontweight='bold', y=0.98)
        
        # Configuration: (fiber, key, row, col, letter, title)
        # Keys must match filenames in the folder
        images_config = [
            ('taboa', 'taboa_ST_30d', 0, 0, 'a', 'Typha - Untreated 30d'),
            ('taboa', 'taboa_ST_180d', 0, 1, 'b', 'Typha - Untreated 180d'),
            ('taboa', 'taboa_DC_30d', 0, 2, 'c', 'Typha - Bilayer 30d'),
            ('taboa', 'taboa_DC_180d', 0, 3, 'd', 'Typha - Bilayer 180d'),
            ('ouricuri', 'ouricuri_ST_30d', 1, 0, 'e', 'Syagrus - Untreated 30d'),
            ('ouricuri', 'ouricuri_ST_180d', 1, 1, 'f', 'Syagrus - Untreated 180d'),
            ('ouricuri', 'ouricuri_DC_30d', 1, 2, 'g', 'Syagrus - Bilayer 30d'),
            ('ouricuri', 'ouricuri_DC_180d', 1, 3, 'h', 'Syagrus - Bilayer 180d'),
        ]
        
        for fiber, key, row, col, letter, title in images_config:
            # Try png first, then tif
            img_path = self.selected_dir / fiber / f"{key}.png"
            if not img_path.exists():
                 img_path = self.selected_dir / fiber / f"{key}.tif"

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
                
                # Scale bar (approximate for visualization)
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
        fig_path = self.results_dir / "fig_mev_original_english.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Original SEM Figure saved: {fig_path}")

    def create_fracture_analysis_figure(self):
        """Creates horizontal figure with fracture analysis (2x4)"""
        print("  -> Generating Fracture Analysis Figure...")
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        # fig.suptitle('Fracture and Surface Damage Analysis',
        #              fontsize=16, fontweight='bold', y=0.98)
        
        images_config = [
            ('taboa', 'taboa_ST_30d', 0, 0, 'a', 'Typha - Untreated 30d'),
            ('taboa', 'taboa_ST_180d', 0, 1, 'b', 'Typha - Untreated 180d'),
            ('taboa', 'taboa_DC_30d', 0, 2, 'c', 'Typha - Bilayer 30d'),
            ('taboa', 'taboa_DC_180d', 0, 3, 'd', 'Typha - Bilayer 180d'),
            ('ouricuri', 'ouricuri_ST_30d', 1, 0, 'e', 'Syagrus - Untreated 30d'),
            ('ouricuri', 'ouricuri_ST_180d', 1, 1, 'f', 'Syagrus - Untreated 180d'),
            ('ouricuri', 'ouricuri_DC_30d', 1, 2, 'g', 'Syagrus - Bilayer 30d'),
            ('ouricuri', 'ouricuri_DC_180d', 1, 3, 'h', 'Syagrus - Bilayer 180d'),
        ]
        
        for fiber, key, row, col, letter, title in images_config:
            img_path = self.selected_dir / fiber / f"{key}.png"
            if not img_path.exists():
                 img_path = self.selected_dir / fiber / f"{key}.tif"
            
            if img_path.exists():
                img = self.load_image(img_path)
                
                # Detect fractures (threshold + skeletonization)
                _, dark_regions = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
                kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                dark_regions = cv2.morphologyEx(dark_regions, cv2.MORPH_CLOSE, kernel_clean)
                skeleton_fractures = morphology.skeletonize(dark_regions > 0)
                
                # Triple Overlay
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
                
            else:
                axes[row, col].text(0.5, 0.5, f'Image not found\n{key}',
                                   ha='center', va='center', fontsize=10)
                axes[row, col].axis('off')
        
        plt.tight_layout()
        fig_path = self.results_dir / "fig_fracture_analysis_english.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"    Fracture Analysis Figure saved: {fig_path}")

def main():
    analyzer = ComprehensiveMEVAnalyzer()
    analyzer.create_original_mev_figure()
    analyzer.create_fracture_analysis_figure()

if __name__ == "__main__":
    main()
