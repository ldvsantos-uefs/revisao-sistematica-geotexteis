"""
Teste rápido da API ScienceDirect
"""

import requests
import json

# Configuração
API_KEY = "465a2fe04ff2d247552d79c320c3c7c6"
BASE_URL = "https://api.elsevier.com/content/search/sciencedirect"

# Fazer busca simples
query = "geotextiles AND biodegradation"

headers = {
    'X-ELS-APIKey': API_KEY,
    'Accept': 'application/json'
}

params = {
    'query': query,
    'count': 10  # Apenas 10 resultados para teste
}

print("="*80)
print(f"TESTE DE BUSCA NO SCIENCEDIRECT")
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
    
    # Mostrar primeiros 5 artigos
    results = data.get('results', [])
    print(f"\nExibindo {min(5, len(results))} primeiros artigos:\n")
    
    for i, article in enumerate(results[:5], 1):
        print(f"{i}. {article.get('title', 'N/A')}")
        
        authors = article.get('authors', [])
        if authors:
            author_names = ', '.join([a.get('name', 'N/A') for a in authors[:3]])
            if len(authors) > 3:
                author_names += ' et al.'
            print(f"   Autores: {author_names}")
        
        print(f"   Journal: {article.get('publicationName', 'N/A')}")
        print(f"   Data: {article.get('coverDate', 'N/A')}")
        print(f"   DOI: {article.get('doi', 'N/A')}")
        print(f"   Acesso aberto: {'Sim' if article.get('openaccess') else 'Não'}")
        print()
    
    print("="*80)
    print("✓ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80)
    
except requests.exceptions.RequestException as e:
    print(f"✗ ERRO na requisição: {e}")
    print("\nPossíveis causas:")
    print("  1. Problema de conexão com a internet")
    print("  2. API key inválida ou expirada")
    print("  3. Limite de requisições excedido")
    print("  4. Problema com o servidor da Elsevier")
    
except Exception as e:
    print(f"✗ ERRO inesperado: {e}")
