# Revisão Sistemática: Geotêxteis Lignocelulósicos

## 📋 Sobre o Projeto

Este repositório contém uma revisão sistemática sobre **Arquitetura Química e Modelagem de Confiabilidade de Geotêxteis Lignocelulósicos para Estabilização Biogeoquímica em Solos Tropicais**.

### 🎯 Objetivos
- Analisar a arquitetura química de polímeros naturais (celulose, hemicelulose, lignina)
- Desenvolver modelos de confiabilidade baseados na distribuição Weibull
- Avaliar estratégias de modificação de superfície para otimizar durabilidade
- Quantificar benefícios biogeoquímicos em solos tropicais

### 🌿 Espécies Estudadas
- **Typha domingensis** (taboa) - Rica em celulose (48%), L/C = 0,46
- **Syagrus coronata** (palmeira-ouricuri) - Rica em lignina (32%), L/C = 0,67

## 📁 Estrutura do Repositório

```
├── 0-OLD/                          # Versões anteriores do manuscrito
├── 1-REFERENCIAS/                  # Dados experimentais e artigos
│   ├── JUNCO/                      # Dados de precipitação
│   ├── OURICURI/                   # Experimentos com Syagrus coronata
│   ├── TABOA/                      # Experimentos com Typha domingensis
│   └── _EXTRAIDOS/                 # Dados consolidados em CSV
├── 2-MANUSCRITO/                   # Manuscrito principal
│   ├── Review_Article_Draft.md     # Texto principal com citações
│   ├── referencias.bib             # 13 referências consolidadas
│   ├── library.bib                 # Biblioteca completa (30+ entradas)
│   ├── Manuscrito_com_Referencias.docx # Documento Word final
│   └── DOCUMENTACAO_SESSAO.md      # Documentação completa da sessão
├── 3-IMAGENS/                      # Figuras e diagramas
├── 4-CODIGOS/                      # Scripts de análise
│   ├── analyze_data.py            # Análise estatística
│   ├── sav_extract.py             # Extração de dados SPSS
│   ├── consolidar_csvs.py         # Consolidação de dados
│   └── gerar-docx.py              # Geração de documentos
└── resultados_sciencedirect/       # Resultados de busca bibliográfica
```

## 🔬 Metodologias

### Ensaios Mecânicos
- **Tração:** EMIC DL (100mm gauge, 20mm/min)
- **Resistência à perfuração:** ASTM D4833
- **Análise estatística:** ANOVA-RM, Cohen's D, Eta squared

### Tratamentos Aplicados
- **Mercerização alcalina:** NaOH 3-9% (ótimo: 6%)
- **Revestimentos acrílicos:** Camada única vs. dupla
- **Duração funcional:** 120-180 dias (FSL P₁₀ Weibull)

### Modelagem
- **Distribuição Weibull:** β (forma), η (escala)
- **Regressão GLM:** Tempo de falha acelerado
- **Pandoc:** Processamento de citações (formato APA)

## 📊 Resultados Principais

### Propriedades Mecânicas
- **Geotêxteis naturais:** 3-9 N·mm⁻² (vs. sintéticos: 50-200 kN·m⁻²)
- **Vida útil funcional:** 120-180 dias
- **Coeficiente de variação:** Redução de 40% com tratamento

### Benefícios Biogeoquímicos
- **Sequestro de carbono:** 0,8-1,2 Mg C·ha⁻¹
- **Agregação do solo:** AEA +16,2%, DMP +42,5%
- **Colonização fúngica:** AMF: 100→600 esporos·g⁻¹
- **VPL serviços ecossistêmicos:** US$ 3.200-4.800·ha⁻¹

## 🛠️ Como Usar

### Regenerar Documento Word
```bash
cd 2-MANUSCRITO
pandoc Review_Article_Draft.md -o Manuscrito_com_Referencias.docx \
  --bibliography=referencias.bib \
  --csl=apa.csl \
  --reference-doc=modelo_formatacao.docx
```

### Executar Análises
```bash
cd 4-CODIGOS
python analyze_data.py
python sav_extract.py
```

### Instalar Dependências
```bash
pip install pandas numpy scipy matplotlib seaborn pandoc
```

## 📚 Referências

O manuscrito cita 13 referências-chave organizadas em:
- **Geotecnia:** Wu1979, Veylon2015, Vannoppen2017
- **Estudos próprios:** Holanda2021, Fontes2021
- **Ecologia:** Ibanez2014, Konvalinkova2015, Mosbah2018, Jha2014
- **Bioquímica:** Larrainzar2017, Girardin2019, Mori2020, Abd-Alla2016

## 👥 Autores

- **Catuxe Varjão de Santana Oliveira**
- **Paulo Roberto Gagliardi**
- **Luiz Diego Vidal Santos**
- **Gustavo da Silva Quirino**
- **Ana Karla de Souza Abud**
- **Cristiane Toniolo Dias**

## 📄 Licença

Este trabalho é parte de uma tese/dissertação acadêmica.


**Última atualização:** Dezembro 2025
**Repositório GitHub:** https://github.com/ldvsantos-uefs/revisao-sistematica-geotexteis