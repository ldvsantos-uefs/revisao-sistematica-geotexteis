"""
Seleção Inteligente de Imagens MEV para Artigo de Revisão
=========================================================

Seleciona automaticamente as melhores imagens MEV de Taboa e Ouricuri para
comparação no artigo, garantindo:
- Mesma magnificação entre comparações
- Períodos específicos: 30 dias e 180 dias
- Tratamentos: Sem tratamento vs Duas camadas de resina
- Total: 8 imagens (4 Taboa + 4 Ouricuri)

Autor: Diego Vidal
Data: Dezembro 2025
"""

import re
from pathlib import Path
import shutil
from collections import defaultdict

class MEVImageSelector:
    """Seletor inteligente de imagens MEV"""
    
    def __init__(self, base_dir="./5-DADOS/MEV-ANALISE"):
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / "imagens-selecionadas"
        self.output_dir.mkdir(exist_ok=True)
        
        # Padrões de magnificação
        self.magnification_patterns = [
            r'\.(\d+\.?\d*)Kx',  # Ex: .1.2Kx, .2Kx
            r'\.(\d+)x',          # Ex: .300x, .500x
            r'-(\d+\.?\d*)Kx',   # Ex: -1.2Kx
            r'-(\d+)x'            # Ex: -300x
        ]
        
        # Mapeamento de períodos (dias)
        self.period_keywords = {
            '30': ['30d', '30dias', 't30', '1mes', '1month'],
            '180': ['180d', '180dias', 't180', '6mes', '6month', '6meses']
        }
        
    def extract_magnification(self, filename):
        """
        Extrai magnificação do nome do arquivo
        Returns: (mag_value, mag_unit) ex: (1.2, 'K') ou (300, '')
        """
        for pattern in self.magnification_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                mag = match.group(1)
                if 'K' in pattern or 'Kx' in filename:
                    return (float(mag), 'K')
                else:
                    return (int(mag), '')
        return (None, None)
    
    def normalize_magnification(self, mag_value, mag_unit):
        """
        Normaliza magnificação para comparação
        Converte tudo para equivalente em x
        """
        if mag_unit == 'K':
            return mag_value * 1000  # 1.2K = 1200x
        else:
            return mag_value
    
    def detect_period(self, path_str):
        """
        Detecta período (30d ou 180d) no caminho ou nome do arquivo
        """
        path_lower = path_str.lower()
        
        for period, keywords in self.period_keywords.items():
            for keyword in keywords:
                if keyword in path_lower:
                    return int(period)
        
        # Se não encontrar, tentar inferir do nome do diretório
        if '30' in path_lower:
            return 30
        elif '180' in path_lower:
            return 180
        
        return None
    
    def classify_treatment(self, path_str):
        """
        Classifica tratamento baseado no caminho
        """
        path_lower = path_str.lower()
        
        if 'sem_trat' in path_lower or 'sem-trat' in path_lower or 'semtrat' in path_lower:
            return 'sem_tratamento'
        elif 'duas_camadas' in path_lower or 'duas-camadas' in path_lower or 'duascamadas' in path_lower:
            return 'duas_camadas'
        elif 'bicamada' in path_lower or '2camadas' in path_lower:
            return 'duas_camadas'
        
        return 'indefinido'
    
    def scan_images(self, fiber_type):
        """
        Escaneia todas as imagens de uma fibra e organiza por características
        """
        fiber_dir = self.base_dir / f"imagens-{fiber_type.lower()}"
        
        if not fiber_dir.exists():
            print(f"AVISO: Diretório não encontrado: {fiber_dir}")
            return {}
        
        images = {}
        
        # Buscar todos os PNG (imagens processadas)
        for img_path in fiber_dir.rglob("*.png"):
            # Extrair informações do caminho e nome
            period = self.detect_period(img_path.name)
            treatment = self.classify_treatment(str(img_path.parent))
            
            if period is None:
                continue
            
            # PNG não tem magnificação no nome, usar "comum" como chave
            mag_normalized = 0  # Placeholder - todas PNG são tratadas iguais
            
            key = (treatment, period, mag_normalized)
            
            if key not in images:
                images[key] = []
            
            images[key].append({
                'path': img_path,
                'filename': img_path.name,
                'mag_value': None,
                'mag_unit': '',
                'mag_normalized': mag_normalized,
                'period': period,
                'treatment': treatment
            })
        
        return images
    
    def find_best_magnification(self, taboa_images, ouricuri_images):
        """
        Para imagens PNG processadas, todas têm mesma "magnificação" (0)
        Retorna 0 se ambas as fibras têm imagens disponíveis
        """
        if taboa_images and ouricuri_images:
            return 0  # Todas PNG são tratadas igualmente
        return None
    
    def select_images_for_article(self):
        """
        Seleciona as 8 imagens principais para o artigo
        """
        print("="*70)
        print(" SELEÇÃO DE IMAGENS MEV PARA O ARTIGO")
        print("="*70)
        
        # Escanear imagens
        print("\n1. Escaneando imagens...")
        taboa_images = self.scan_images("taboa")
        ouricuri_images = self.scan_images("ouricuri")
        
        print(f"   Taboa: {sum(len(v) for v in taboa_images.values())} imagens encontradas")
        print(f"   Ouricuri: {sum(len(v) for v in ouricuri_images.values())} imagens encontradas")
        
        # Encontrar melhor magnificação
        print("\n2. Determinando magnificação ideal...")
        best_mag = self.find_best_magnification(taboa_images, ouricuri_images)
        
        if best_mag is None:
            print("\nERRO: Não foi possível encontrar magnificação comum!")
            return None
        
        print(f"   Magnificação selecionada: PNG (imagens processadas)")
        
        # Critérios de seleção
        criteria = [
            ('sem_tratamento', 30),
            ('sem_tratamento', 180),
            ('duas_camadas', 30),
            ('duas_camadas', 180)
        ]
        
        selected = {
            'taboa': [],
            'ouricuri': [],
            'magnificacao': best_mag
        }
        
        print("\n3. Selecionando imagens...")
        
        # Selecionar para cada fibra
        for fiber_type, images_dict in [('taboa', taboa_images), ('ouricuri', ouricuri_images)]:
            print(f"\n   {fiber_type.upper()}:")
            
            for treatment, period in criteria:
                key = (treatment, period, best_mag)
                
                if key in images_dict and images_dict[key]:
                    # Pegar primeira imagem disponível
                    img_info = images_dict[key][0]
                    selected[fiber_type].append(img_info)
                    
                    treatment_label = "Sem Trat." if treatment == 'sem_tratamento' else "Dupla Camada"
                    print(f"     ✓ {treatment_label} - {period}d: {img_info['filename']}")
                else:
                    print(f"     ✗ {treatment} - {period}d: NÃO ENCONTRADA")
        
        # Copiar imagens selecionadas
        print("\n4. Copiando imagens selecionadas...")
        self.copy_selected_images(selected)
        
        # Gerar relatório
        self.generate_selection_report(selected)
        
        return selected
    
    def copy_selected_images(self, selected):
        """
        Copia imagens selecionadas para diretório organizado
        """
        for fiber_type in ['taboa', 'ouricuri']:
            fiber_output = self.output_dir / fiber_type
            fiber_output.mkdir(exist_ok=True)
            
            for idx, img_info in enumerate(selected[fiber_type], 1):
                # Nome padronizado
                treatment = 'ST' if img_info['treatment'] == 'sem_tratamento' else 'DC'
                new_name = f"{fiber_type}_{treatment}_{img_info['period']}d.png"
                
                dest_path = fiber_output / new_name
                shutil.copy2(img_info['path'], dest_path)
                print(f"     Copiado: {new_name}")
    
    def generate_selection_report(self, selected):
        """
        Gera relatório markdown da seleção
        """
        report_path = self.output_dir / "RELATORIO_SELECAO.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Relatório de Seleção de Imagens MEV\n\n")
            f.write(f"**Data**: {Path(__file__).stat().st_mtime}\n\n")
            f.write(f"**Formato**: PNG (imagens processadas)\n\n")
            
            f.write("## Imagens Selecionadas\n\n")
            
            for fiber_type in ['taboa', 'ouricuri']:
                f.write(f"### {fiber_type.upper()} (*{'Typha domingensis' if fiber_type=='taboa' else 'Syagrus coronata'}*)\n\n")
                f.write("| Tratamento | Período | Arquivo Original |\n")
                f.write("|------------|---------|------------------|\n")
                
                for img_info in selected[fiber_type]:
                    treatment = "Sem Tratamento" if img_info['treatment'] == 'sem_tratamento' else "Duas Camadas"
                    f.write(f"| {treatment} | {img_info['period']} dias | `{img_info['filename']}` |\n")
                
                f.write("\n")
            
            f.write("## Estrutura de Saída\n\n")
            f.write("```\n")
            f.write("imagens-selecionadas/\n")
            f.write("├── taboa/\n")
            f.write("│   ├── taboa_ST_30d.png     (Sem Tratamento, 30 dias)\n")
            f.write("│   ├── taboa_ST_180d.png    (Sem Tratamento, 180 dias)\n")
            f.write("│   ├── taboa_DC_30d.png     (Dupla Camada, 30 dias)\n")
            f.write("│   └── taboa_DC_180d.png    (Dupla Camada, 180 dias)\n")
            f.write("├── ouricuri/\n")
            f.write("│   ├── ouricuri_ST_30d.png\n")
            f.write("│   ├── ouricuri_ST_180d.png\n")
            f.write("│   ├── ouricuri_DC_30d.png\n")
            f.write("│   └── ouricuri_DC_180d.png\n")
            f.write("└── RELATORIO_SELECAO.md\n")
            f.write("```\n\n")
            
            f.write("## Próximos Passos\n\n")
            f.write("1. Executar `analise_mev_fraturas_danos.py` nas imagens selecionadas\n")
            f.write("2. Gerar figura comparativa para o manuscrito\n")
            f.write("3. Atualizar Tabela 2 com dados morfométricos\n")
        
        print(f"\nRelatório salvo: {report_path}")


def main():
    """Execução principal"""
    selector = MEVImageSelector()
    selected = selector.select_images_for_article()
    
    if selected:
        print("\n" + "="*70)
        print(" SELEÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print(f"\nImagens salvas em: {selector.output_dir}")
        print("\nPróximo passo: Executar análise de fraturas e danos")
    else:
        print("\n" + "="*70)
        print(" ERRO NA SELEÇÃO")
        print("="*70)
        print("\nVerifique:")
        print("1. Se as imagens estão nos diretórios corretos")
        print("2. Se os nomes dos arquivos contêm informações de magnificação")
        print("3. Se há imagens com magnificações compatíveis entre Taboa e Ouricuri")


if __name__ == "__main__":
    main()
