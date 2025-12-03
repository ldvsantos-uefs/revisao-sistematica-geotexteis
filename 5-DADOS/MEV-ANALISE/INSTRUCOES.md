# Análise Morfométrica Comparativa MEV
## Taboa (Typha domingensis) vs Ouricuri (Syagrus coronata)

## Estrutura de Diretórios

```
5-DADOS/MEV-ANALISE/
├── imagens-taboa/          # Imagens MEV de fibras de taboa
├── imagens-ouricuri/       # Imagens MEV de fibras de ouricuri
├── resultados/             # Saída das análises (JSON, PNG)
├── README_MEV.md           # Documentação original do código
└── INSTRUCOES.md          # Este arquivo
```

## Scripts Disponíveis

### 1. `analise_mev_fibras.py` (Código Original Completo)
- Código completo do pipeline original
- Classes `FiberAnalyzer` e `ComparativeFiberAnalyzer`
- Múltiplos métodos de rugosidade
- Documentação detalhada no `README_MEV.md`

### 2. `analise_mev_comparativa_artigo.py` (Script Adaptado)
- Versão simplificada e focada para o artigo
- Análise comparativa direta Taboa vs Ouricuri
- Gera visualizações e comparações quantitativas
- Salva resultados em JSON e PNG

## Como Usar

### Passo 1: Preparar Imagens

Copiar imagens MEV (.tif) para os diretórios apropriados:

```powershell
# Copiar imagens da Taboa
Copy-Item "caminho/origem/*.tif" ".\5-DADOS\MEV-ANALISE\imagens-taboa\"

# Copiar imagens do Ouricuri
Copy-Item "caminho/origem/*.tif" ".\5-DADOS\MEV-ANALISE\imagens-ouricuri\"
```

### Passo 2: Instalar Dependências

```bash
pip install opencv-python scikit-image matplotlib numpy scipy
```

### Passo 3: Executar Análise

```python
# Navegar para o diretório do código
cd 4-CODIGOS

# Executar análise comparativa
python analise_mev_comparativa_artigo.py
```

## Parâmetros Analisados

### 1. Porosidade Superficial
- **Porosidade total (%)**: Proporção de área de poros
- **Número de poros**: Contagem de regiões porosas
- **Área média dos poros**: Tamanho médio em pixels²
- **Circularidade**: Métrica de forma dos poros (0-1)

### 2. Orientação Fibrilar
- **Índice de orientação (0-1)**: Grau de alinhamento das fibras
  - 0 = orientação aleatória
  - 1 = orientação perfeitamente alinhada
- **Ângulo médio**: Direção predominante em graus
- **Desvio padrão angular**: Dispersão da orientação

### 3. Estrutura Fibrilar
- **Densidade fibrilar**: Proporção de área ocupada por fibras
- **Comprimento esqueletal**: Soma dos comprimentos das fibras
- **Número de junções**: Pontos de ramificação/cruzamento

### 4. Textura Superficial (Rugosidade)
- **Rugosidade por desvio padrão**: Variação local de intensidade
- **Rugosidade por gradiente**: Magnitude das mudanças de intensidade

## Resultados Esperados

### Arquivos JSON
- `analise_Typha_domingensis_[nome].json` - Dados quantitativos da taboa
- `analise_Syagrus_coronata_[nome].json` - Dados quantitativos do ouricuri
- `comparacao_taboa_ouricuri_[timestamp].json` - Comparação completa

### Imagens PNG
- `analise_Typha_domingensis_[nome].png` - Visualização multi-painel da taboa
- `analise_Syagrus_coronata_[nome].png` - Visualização multi-painel do ouricuri
- `comparacao_grafica_[timestamp].png` - Gráficos comparativos

### Visualizações Incluem:
1. Imagem original
2. Mapa de porosidade
3. Mapa de orientação (colorido por ângulo)
4. Esqueleto fibrilar
5. Mapa de rugosidade
6. Resumo textual dos parâmetros

## Integração com o Artigo

### Tabela 2 (Morfometria Quantitativa)
Os resultados podem ser usados para atualizar/expandir a **Tabela 2** do manuscrito:

```markdown
| **Parâmetro** | **Fibras Não Tratadas** | **NaOH 6%** | **Resina Monocamada** | **Variação (%)** |
|---|---|---|---|---|
| **Morfologia Superficial** | | | | |
| Porosidade total (%) | [valor MEV] | [valor MEV] | [valor MEV] | [cálculo] |
```

### Figura MEV Comparativa
Gerar figura para o manuscrito mostrando:
- **Painel A**: MEV Taboa (escala)
- **Painel B**: MEV Ouricuri (escala)
- **Painel C**: Mapas de orientação
- **Painel D**: Análise esqueletal

### Texto para Seção 3.1
Os dados quantitativos podem ser citados:

> "A análise morfométrica quantitativa revelou que fibras de *Typha* apresentam 
> porosidade de X,X ± Y,Y %, com índice de orientação de 0,ZZZ, enquanto 
> *Syagrus* exibe porosidade de A,A ± B,B % e índice de orientação de 0,CCC, 
> refletindo diferenças na arquitetura microestrutural..."

## Localização das Imagens Originais

### Taboa (Bio SAP)
```
C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\20 - ARTIGOS\
  1 - ARTIGOS PENDENTES\2 - MEUS ARTIGOS\3 - Bio SAP\2 - DADOS\
  3 - PDI MEV\FIBRAS\
    ├── MEV_Antes do tratamento\TABOA\
    └── MEV_Pós-tratamento\TABOA\
```

### Ouricuri (Artigo Comparações MEV)
```
C:\Users\vidal\OneDrive\Documentos\1 - ACADEMICO\20 - ARTIGOS\
  2 - ARTIGOS PUBLICADOS\ARTIGO COMPARAÇÕES MEV (PUBLICADO)\4 - MEVs\
```

**Nota**: Buscar especificamente por imagens de:
- Fibras sem resina
- Fibras com duas camadas de resina

## Troubleshooting

### Erro: "Não foi possível carregar imagem"
- Verificar se os arquivos são .tif ou .TIF
- Confirmar que não são arquivos corrompidos
- Testar com `cv2.imread()` manualmente

### Erro: Importação de módulos
```bash
pip install --upgrade opencv-python scikit-image matplotlib numpy scipy
```

### Imagens muito grandes
- Redimensionar se necessário:
```python
img_resized = cv2.resize(img, (2048, 2048))
```

## Contato

Para dúvidas sobre o código ou análise:
- Verificar `README_MEV.md` (documentação original)
- Revisar código inline em `analise_mev_fibras.py`
- Consultar exemplos no artigo Bio SAP

---

**Última atualização**: Dezembro 2025  
**Versão**: 1.0 (adaptada para artigo de revisão)
