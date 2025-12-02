"""
Busca por artigos sobre geotêxteis biodegradáveis e biodiversidade do solo
"""

import requests
import json

# Configuração
API_KEY = "465a2fe04ff2d247552d79c320c3c7c6"
BASE_URL = "https://api.elsevier.com/content/search/sciencedirect"

# Query para geotêxteis biodegradáveis e biodiversidade
query = "biodegradable geotextiles soil biodiversity Collembola AMF"

headers = {
    'X-ELS-APIKey': API_KEY,
    'Accept': 'application/json'
}

params = {
    'query': query,
    'count': 25  # Mais resultados
}

print("="*80)
print(f"BUSCA NO SCIENCEDIRECT")
print("="*80)
print(f"\nQuery: {query}")
print(f"Fazendo requisição...\n")

try:
    response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    # Informações gerais
    print(f"✓ Requisição bem-sucedida!")
    print(f"✓ Total de resultados encontrados: {data.get('resultsFound', 0)}")
    
    # Mostrar artigos
    results = data.get('results', [])
    print(f"\nExibindo {len(results)} artigos encontrados:\n")
    
    for i, article in enumerate(results, 1):
        print(f"{i}. {article.get('title', 'N/A')}")
        
        authors = article.get('authors', [])
        if authors:
            author_names = ', '.join([a.get('name', 'N/A') for a in authors[:3]])
            print(f"   Autores: {author_names}")
        
        journal = article.get('sourceTitle', 'N/A')
        print(f"   Journal: {journal}")
        
        year = article.get('publicationDate', 'N/A')[:4] if article.get('publicationDate') else 'N/A'
        print(f"   Ano: {year}")
        
        doi = article.get('doi', 'N/A')
        print(f"   DOI: {doi}")
        
        # Para BibTeX, preciso de mais info
        print(f"   Link: https://doi.org/{doi}" if doi != 'N/A' else "   Link: N/A")
        print()
        
except Exception as e:
    print(f"Erro: {e}")