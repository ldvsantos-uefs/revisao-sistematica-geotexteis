"""
Illustrator Automation Script for Figure 1 Translation
======================================================
Translates text inside 'fig_01.ai' from Portuguese to English using COM Automation.

REQUIREMENTS:
1. Adobe Illustrator installed on this machine.
2. Python package `pywin32` installed (pip install pywin32).

Author: Diego Vidal
Date: December 2025
"""

import os
import sys
from pathlib import Path
import time

# Try to import win32com
try:
    import win32com.client
except ImportError:
    print("ERROR: 'pywin32' library not found.")
    print("Please run: pip install pywin32")
    sys.exit(1)

def translate_figure_1():
    # Paths
    base_dir = Path(__file__).parent.parent
    ai_file = base_dir / "3-IMAGENS" / "fig_01.ai"
    output_dir = base_dir / "5-DADOS" / "MEV-ANALISE" / "resultados_en"
    output_png = output_dir / "fig_01_english.png"
    
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ai_file.exists():
        print(f"Error: Source file not found: {ai_file}")
        return

    print(f"Connecting to Adobe Illustrator...")
    try:
        # Connect to Illustrator Application
        # 'Illustrator.Application' is the COM ProgID. Version might vary (e.g., .24), but generic usually works.
        app = win32com.client.Dispatch("Illustrator.Application")
        
        # Open the file
        print(f"Opening: {ai_file.name}...")
        doc = app.Open(str(ai_file))
        
        # Translation Dictionary (Portuguese -> English)
        # ORDER MATTERS: Longer phrases first to prevent partial replacements
        translations = {
            # Specific Labels (Long phrases)
            "Syagrus (Alta Razão L/C)": "Syagrus (High L/C Ratio)",
            "Typha (Baixa Razão L/C)": "Typha (Low L/C Ratio)",
            "S2 (Média, mais espessa)": "S2 (Middle, thickest)",
            "Parede Primária (P)": "Primary Wall (P)",
            "Lamela Média (LM)": "Middle Lamella (ML)",
            "Lamela média": "Middle Lamella",
            "(a) Nível molecular": "(a) Molecular Level",
            "(b) Nível Fibrilar": "(b) Fibrillar Level",
            "(c) Nível Celular": "(c) Cellular Level",
            "(d) Nível do Tecido & Razão L/C": "(d) Tissue Level & L/C Ratio",
            "dificulta a": "hinders",
            "descontrução da biomassa": "biomass deconstruction",
            "Recalcitrância": "Recalcitrance",
            "Alta Razão L/C": "High L/C Ratio",
            "Baixa Razão L/C": "Low L/C Ratio",
            "Ponte de Hidrogênio": "Hydrogen Bond",
            "Pontes de Hidrogênio": "Hydrogen Bonds",
            "Cadeia de Celulose": "Cellulose Chain",
            "Complexo Enzimático": "Enzymatic Complex",
            
            # General Terms
            "Parede Celular": "Cell Wall",
            "Parede celular": "Cell wall",
            "Microfibrila": "Microfibril",
            "Microfibrilas": "Microfibrils",
            "Celulose": "Cellulose",
            "Lignina": "Lignin",
            "Hemicelulose": "Hemicellulose",
            "Cadeias": "Chains",
            "Tecido": "Tissue",
            "Fibra": "Fiber",
            "Fibras": "Fibers",
            "Lúmen": "Lumen",
            "Primária": "Primary",
            "Secundária": "Secondary",
            "Macrofibrila": "Macrofibril",
            "Cristalina": "Crystalline",
            "Amorfa": "Amorphous",
            "Estrutura": "Structure",
            "Nível": "Level",
            "Esquemático": "Schematic",
            "Região": "Region",
            "Micela": "Micelle",
            "Molécula": "Molecule",
            "Glicose": "Glucose",
            "Ligação": "Bond",
            "Célula": "Cell",
            "Vegetal": "Plant",
            "Transversal": "Cross-section",
            "Longitudinal": "Longitudinal",
            "Feixe": "Bundle",
            "Vascular": "Vascular",
            "Xilema": "Xylem",
            "Floema": "Phloem",
            "Esclerênquima": "Sclerenchyma",
            "Parênquima": "Parenchyma",
            "Intercelular": "Intercellular",
            "Espaço": "Space",
            "Camada": "Layer",
            "Externa": "Outer",
            "Interna": "Inner",
            "Média": "Middle",
            "Complexo": "Complex",
            "Enzimático": "Enzymatic",
            "Ataque": "Attack",
            "Degradação": "Degradation",
            "Tempo": "Time",
            "Dias": "Days",
            "Resistência": "Strength",
            "Tração": "Tensile",
            "Deformação": "Strain",
            "Tensão": "Stress"
        }
        
        print("Translating text frames...")
        count = 0
        
        # Iterate through all text frames in the document
        # Using doc.TextFrames usually gets all frames, even in groups.
        # If not, we might need to recurse, but let's try Stories first which is content-centric.
        
        # Debug: Print all found text
        print("\n--- TEXT CONTENT FOUND ---")
        for i, text_frame in enumerate(doc.TextFrames):
            content = text_frame.Contents
            print(f"[{i}] '{content}'")
            
            # Translation Logic
            new_text = content
            for pt, en in translations.items():
                # Case insensitive check, but replace with dictionary case
                if pt.lower() in new_text.lower():
                    # Simple replace might fail case, let's try to be smart or just direct replace
                    # For now, direct replace using the key as the source of truth for case
                    # This assumes the key in dict matches the case in file roughly or we don't care
                    
                    # Better: Case insensitive replace
                    import re
                    pattern = re.compile(re.escape(pt), re.IGNORECASE)
                    new_text = pattern.sub(en, new_text)
            
            if new_text != content:
                text_frame.Contents = new_text
                print(f"  >>> TRANSLATED: '{new_text}'")
                count += 1
        print("--------------------------\n")
        
        print(f"Translation finished. {count} text frames updated.")
        
        print(f"Translation finished. {count} text frames updated.")
        
        # Export to PNG
        print(f"Exporting to: {output_png.name}...")
        
        # Configure Export Options
        export_options = win32com.client.Dispatch("Illustrator.ExportOptionsPNG24")
        export_options.AntiAliasing = True
        export_options.Transparency = True
        export_options.ArtBoardClipping = True
        export_options.HorizontalScale = 300.0 # 300% scale for high res (approx 300 DPI if base is 72)
        export_options.VerticalScale = 300.0
        
        # Export type 5 is PNG24
        # SaveAs is for AI/EPS/PDF. Export is for images.
        doc.Export(str(output_png), 5, export_options)
        
        # Close without saving changes to the original AI file
        # 2 = aiDoNotSaveChanges
        doc.Close(2)
        
        print("Success! Figure 1 translated and exported.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: Could not automate Illustrator.")
        print(f"Details: {e}")
        print("\nPossible causes:")
        print("1. Adobe Illustrator is not installed or not running.")
        print("2. A dialog box is open in Illustrator blocking the script.")
        print("3. Permissions issue.")

if __name__ == "__main__":
    translate_figure_1()
