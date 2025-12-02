# Guia de Uso: Script de Busca ScienceDirect

## 📋 Descrição

Script Python para facilitar buscas de artigos científicos no ScienceDirect usando a API Elsevier. Permite buscar, filtrar e exportar resultados em CSV e BibTeX.

## 🔧 Instalação

### 1. Instalar dependências

```powershell
pip install pandas requests
```

### 2. Configurar API Key

Sua chave API já está configurada no script:
```python
API_KEY = "465a2fe04ff2d247552d79c320c3c7c6"
```

## 🚀 Uso Básico

### Executar busca padrão

```powershell
python sciencedirect_search.py
```

Isso executará as buscas de exemplo e salvará os resultados em `resultados_sciencedirect/`

## 📖 Exemplos de Uso Personalizado

### Exemplo 1: Busca simples

```python
from sciencedirect_search import ScienceDirectSearch

searcher = ScienceDirectSearch("465a2fe04ff2d247552d79c320c3c7c6")

# Buscar artigos sobre geotêxteis
results = searcher.search_articles("geotextiles")

# Salvar em CSV
searcher.save_to_csv(results['results'], "meus_resultados.csv")
```

### Exemplo 2: Busca com filtros

```python
# Buscar artigos de 2020 em diante, apenas acesso aberto
results = searcher.search_all_pages(
    query="soil erosion AND geotextiles",
    max_results=100,
    date_from="2020-01-01",
    open_access=True,
    pub_type="Research articles"
)

searcher.save_to_csv(results, "artigos_recentes.csv")
searcher.save_to_bibtex(results, "referencias.bib")
```

### Exemplo 3: Busca avançada com operadores booleanos

```python
# Busca complexa com operadores AND, OR
query = "(lignocellulosic OR natural fibers) AND (biodegradation OR decomposition) AND geotextiles"

results = searcher.search_all_pages(
    query=query,
    max_results=200,
    date_from="2015-01-01",
    date_to="2025-12-31"
)

searcher.print_summary(results)
```

## 🔍 Parâmetros de Busca

### query (obrigatório)
Termo de busca. Suporta operadores booleanos:
- `AND`: geotextiles AND biodegradation
- `OR`: (natural OR synthetic) geotextiles
- `NOT`: geotextiles NOT synthetic
- `"citação exata"`: "soil bioengineering"

### Filtros Opcionais

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `start` | int | Índice inicial (paginação) | `start=0` |
| `count` | int | Resultados por página (max 100) | `count=50` |
| `date_from` | str | Data inicial | `date_from="2020-01-01"` |
| `date_to` | str | Data final | `date_to="2025-12-31"` |
| `pub_type` | str | Tipo de publicação | `pub_type="Research articles"` |
| `open_access` | bool | Apenas acesso aberto | `open_access=True` |

### Tipos de Publicação Disponíveis

- `"Research articles"`
- `"Review articles"`
- `"Case Reports"`
- `"Conference abstracts"`
- `"Book chapters"`

## 📊 Formatos de Saída

### CSV
Contém as seguintes colunas:
- title
- authors
- journal
- date
- doi
- url
- abstract
- open_access
- volume, issue, pages

### BibTeX
Formato padrão para gerenciadores de referências (Zotero, Mendeley, etc.)

## 💡 Exemplos de Queries para Sua Pesquisa

```python
# 1. Geotêxteis lignocelulósicos
query1 = "lignocellulosic AND geotextiles AND (degradation OR biodegradation)"

# 2. Fibras naturais em engenharia de solos
query2 = "(natural fibers OR plant fibers) AND (soil reinforcement OR slope stabilization)"

# 3. Modelagem de Weibull em materiais biodegradáveis
query3 = "Weibull AND (biodegradable materials OR natural fibers)"

# 4. Serviços ecossistêmicos de bioengenharia
query4 = "(soil bioengineering OR ecological engineering) AND (carbon sequestration OR ecosystem services)"

# 5. Typha ou Syagrus (suas espécies estudadas)
query5 = "(Typha domingensis OR Syagrus coronata) AND (geotextiles OR fibers)"
```

## ⚠️ Limitações da API

- **Rate Limit**: Máximo de requisições por segundo (o script já inclui pausas)
- **Resultados por requisição**: Máximo 100 artigos por chamada
- **Acesso**: Alguns artigos requerem assinatura institucional
- **Quota**: Verifique seu plano na Elsevier Developer Portal

## 🛠️ Solução de Problemas

### Erro: "API Key inválida"
```python
# Verifique se sua chave está correta
searcher = ScienceDirectSearch("SUA_CHAVE_AQUI")
```

### Erro: "Module not found"
```powershell
# Instalar dependências
pip install --upgrade pandas requests
```

### Poucos resultados
```python
# Tente queries mais amplas
query = "geotextiles"  # ao invés de "lignocellulosic geotextiles biodegradation"

# Ou remova filtros restritivos
results = searcher.search_all_pages(
    query=query,
    max_results=500  # Aumentar limite
)
```

## 📈 Análise de Resultados

O script gera automaticamente:
- ✅ Total de artigos encontrados
- ✅ Distribuição por acesso (aberto vs restrito)
- ✅ Top 5 journals com mais publicações
- ✅ Distribuição temporal (últimos 10 anos)

## 🔗 Recursos Adicionais

- [Elsevier Developer Portal](https://dev.elsevier.com/)
- [ScienceDirect API Documentation](https://dev.elsevier.com/documentation/ScienceDirectSearchAPI.wadl)
- [Operadores de Busca Avançada](https://dev.elsevier.com/tips/ScienceDirectSearchTips.htm)

## 📝 Notas

- Os resultados são salvos com timestamp para evitar sobrescrever buscas anteriores
- O script respeita limites de requisições da API com pausas automáticas
- Arquivos CSV usam UTF-8 com BOM para compatibilidade com Excel

## 🤝 Suporte

Para problemas com a API, consulte:
- Elsevier API Support: https://service.elsevier.com/app/contact/supporthub/

---

**Autor**: Diego Vidal  
**Data**: 2025-12-02  
**Versão**: 1.0
