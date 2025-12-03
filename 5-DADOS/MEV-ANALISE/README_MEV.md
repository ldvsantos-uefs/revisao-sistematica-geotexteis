# Documentação dos Códigos de Análise MEV

## Visão Geral

Este conjunto de códigos Python implementa análise morfológica quantitativa completa para imagens de Microscopia Eletrônica de Varredura (MEV) de fibras de *Typha domingensis*. Os códigos foram desenvolvidos para caracterizar fibras naturais com e sem tratamento químico.

## Estrutura dos Arquivos

### 1. `codigos_analise_mev_completo.py` (PRINCIPAL)
**Arquivo principal** contendo todas as classes e funções organizadas:

- **Classe `FiberAnalyzer`**: Análise individual de fibras
- **Classe `ComparativeFiberAnalyzer`**: Análise comparativa entre amostras
- **Funções de rugosidade**: Múltiplos métodos de cálculo
- **Exemplo de uso**: Demonstração completa

### 2. `analise_comparativa_fibras.py`
Código específico para análise comparativa entre fibras tratadas e não tratadas.

### 3. `create_rugosidade_visualizations.py`
Geração de visualizações avançadas de rugosidade superficial com múltiplos métodos.

### 4. `create_svg_figures.py`
Criação de figuras em formato SVG editável para publicações científicas.

### 5. `taboa_fiber_analysis.py`
Código original para análise individual de fibras de taboa.

## Dependências Necessárias

```bash
pip install opencv-python
pip install scikit-image
pip install matplotlib
pip install numpy
pip install scipy
```

## Principais Funcionalidades

### Análise de Orientação Fibrilar
- Cálculo de gradientes com operadores de Sobel
- Determinação de ângulos de orientação
- Índice de orientação (0-1)
- Classificação de direção predominante

### Análise de Características Superficiais
- Detecção automática de poros
- Cálculo de porosidade total
- Análise morfométrica de poros (área, circularidade, razão de aspecto)
- Limpeza morfológica para remoção de artefatos

### Análise de Estrutura Fibrilar
- Esqueletização morfológica (algoritmo Zhang-Suen)
- Densidade fibrilar
- Detecção de junções e ramificações
- Comprimento esqueletal total

### Análise de Textura Superficial
- Matriz de Co-ocorrência de Níveis de Cinza (GLCM)
- Descritores de textura (contraste, homogeneidade, energia, correlação)
- Múltiplos métodos de rugosidade:
  - Desvio padrão local
  - Magnitude do gradiente
  - Operador Laplaciano
  - Filtro de range

## Como Usar

### Análise Individual
```python
from codigos_analise_mev_completo import FiberAnalyzer

# Criar analisador
analyzer = FiberAnalyzer()

# Carregar imagem
image, image_norm = analyzer.load_and_process_image("sua_imagem.tif")

# Executar análises
orientation_results, angles, magnitudes = analyzer.analyze_fiber_orientation(image_norm)
surface_results, pores, regions = analyzer.analyze_surface_features(image, image_norm)
structure_results, skeleton, features, corners = analyzer.analyze_fiber_structure(image_norm)
texture_results, roughness = analyzer.analyze_surface_texture(image_norm)
```

### Análise Comparativa
```python
from codigos_analise_mev_completo import ComparativeFiberAnalyzer

# Criar analisador comparativo
comp_analyzer = ComparativeFiberAnalyzer()

# Executar análise comparativa
results = comp_analyzer.run_comparative_analysis(
    image_path_sem="fibra_sem_tratamento.tif",
    image_path_com="fibra_com_tratamento.tif",
    output_dir="resultados"
)
```

### Análise de Rugosidade
```python
from codigos_analise_mev_completo import calculate_enhanced_roughness

# Diferentes métodos de rugosidade
rugosidade_std = calculate_enhanced_roughness(image_norm, 'local_std')
rugosidade_grad = calculate_enhanced_roughness(image_norm, 'gradient_magnitude')
rugosidade_lap = calculate_enhanced_roughness(image_norm, 'laplacian')
rugosidade_range = calculate_enhanced_roughness(image_norm, 'range_filter')
```

## Parâmetros Principais

### Orientação Fibrilar
- **Sigma gaussiano**: 1.0 pixel
- **Limiar de magnitude**: 75º percentil
- **Índice de orientação**: IO = 1 - (σ_θ/90°)

### Detecção de Poros
- **Sigma gaussiano**: 2.0 pixels
- **Fator de limiar**: 0.7 × limiar de Otsu
- **Área mínima**: 20 pixels
- **Área de preenchimento**: 10 pixels

### Esqueletização
- **Algoritmo**: Zhang-Suen
- **Filtros direcionais**: kernels 3×3 otimizados
- **Sigma para junções**: 2.0 pixels

### GLCM
- **Distâncias**: [1, 2, 3, 5] pixels
- **Ângulos**: [0°, 45°, 90°, 135°]
- **Níveis de cinza**: 256
- **Normalização**: simétrica

## Resultados Gerados

### Dados Quantitativos
- Arquivo JSON com todos os parâmetros calculados
- Comparações percentuais entre amostras
- Timestamps para rastreabilidade

### Visualizações
- Mapas de orientação codificados por cores
- Detecção de poros sobrepostos
- Esqueletos fibrilares
- Mapas de rugosidade com múltiplos métodos
- Gráficos comparativos
- Figuras em PNG (alta resolução) e SVG (editável)

## Validação e Controle de Qualidade

- Parâmetros padronizados para reprodutibilidade
- Controle de versão das bibliotecas
- Validação com imagens de referência
- Documentação completa de métodos

## Aplicações

- Caracterização de fibras naturais
- Análise de efeitos de tratamentos químicos
- Estudos de materiais compósitos
- Pesquisa em biomateriais
- Análise de superfícies em geral

## Suporte e Modificações

Os códigos são modulares e podem ser facilmente adaptados para:
- Outros tipos de fibras naturais
- Diferentes condições de tratamento
- Novos parâmetros morfológicos
- Outras técnicas de microscopia

Para modificações, consulte a documentação inline nos códigos e os exemplos de uso fornecidos.
