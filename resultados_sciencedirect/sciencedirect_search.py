"""
Script para busca de artigos no ScienceDirect usando a API Elsevier
Autor: Diego Vidal
Data: 2025-12-02
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Optional
import time

class ScienceDirectSearch:
    """Classe para realizar buscas na API do ScienceDirect"""
    
    def __init__(self, api_key: str):
        """
        Inicializa a classe com a chave da API
        
        Args:
            api_key: Chave da API do Elsevier
        """
        self.api_key = api_key
        self.base_url = "https://api.elsevier.com/content/search/sciencedirect"
        self.headers = {
            'X-ELS-APIKey': self.api_key,
            'Accept': 'application/json'
        }
        
    def search_articles(self, 
                       query: str,
                       start: int = 0,
                       count: int = 25,
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None,
                       pub_type: Optional[str] = None,
                       open_access: bool = False) -> Dict:
        """
        Realiza busca de artigos no ScienceDirect
        
        Args:
            query: Termo de busca (ex: "geotextiles AND biodegradation")
            start: Índice inicial dos resultados (para paginação)
            count: Número de resultados por página (máximo 100)
            date_from: Data inicial no formato YYYY-MM-DD
            date_to: Data final no formato YYYY-MM-DD
            pub_type: Tipo de publicação ("Research articles", "Review articles", etc)
            open_access: Filtrar apenas artigos de acesso aberto
            
        Returns:
            Dicionário com os resultados da busca
        """
        params = {
            'query': query,
            'start': start,
            'count': min(count, 100),  # Máximo 100 por requisição
        }
        
        # Adicionar filtros opcionais
        filters = []
        if date_from:
            filters.append(f"date > {date_from}")
        if date_to:
            filters.append(f"date < {date_to}")
        if pub_type:
            filters.append(f"pub-type({pub_type})")
        if open_access:
            filters.append("openaccess(1)")
            
        if filters:
            params['filters'] = " AND ".join(filters)
        
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return {}
    
    def search_all_pages(self,
                        query: str,
                        max_results: int = 100,
                        **kwargs) -> List[Dict]:
        """
        Busca múltiplas páginas de resultados
        
        Args:
            query: Termo de busca
            max_results: Número máximo de resultados totais
            **kwargs: Outros parâmetros do search_articles
            
        Returns:
            Lista com todos os artigos encontrados
        """
        all_results = []
        start = 0
        count = min(100, max_results)
        
        while start < max_results:
            print(f"Buscando resultados {start} a {start + count}...")
            
            data = self.search_articles(
                query=query,
                start=start,
                count=count,
                **kwargs
            )
            
            if not data or 'results' not in data:
                break
                
            results = data.get('results', [])
            if not results:
                break
                
            all_results.extend(results)
            
            # Verificar se há mais resultados
            total_results = int(data.get('resultsFound', 0))
            if start + count >= total_results or start + count >= max_results:
                break
                
            start += count
            time.sleep(1)  # Pausa para não sobrecarregar a API
            
        return all_results
    
    def extract_article_info(self, article: Dict) -> Dict:
        """
        Extrai informações relevantes de um artigo
        
        Args:
            article: Dicionário com dados do artigo
            
        Returns:
            Dicionário com informações formatadas
        """
        return {
            'title': article.get('title', 'N/A'),
            'authors': ', '.join([
                author.get('name', 'N/A') 
                for author in article.get('authors', [])
            ]),
            'journal': article.get('publicationName', 'N/A'),
            'date': article.get('coverDate', 'N/A'),
            'doi': article.get('doi', 'N/A'),
            'url': article.get('link', [{}])[0].get('@href', 'N/A'),
            'abstract': article.get('teaser', 'N/A'),
            'open_access': article.get('openaccess', False),
            'volume': article.get('volume', 'N/A'),
            'issue': article.get('issue', 'N/A'),
            'pages': article.get('pages', 'N/A')
        }
    
    def save_to_csv(self, articles: List[Dict], filename: str):
        """
        Salva os resultados em um arquivo CSV
        
        Args:
            articles: Lista de artigos
            filename: Nome do arquivo de saída
        """
        if not articles:
            print("Nenhum artigo para salvar.")
            return
            
        df = pd.DataFrame([self.extract_article_info(art) for art in articles])
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ Resultados salvos em: {filename}")
        
    def save_to_bibtex(self, articles: List[Dict], filename: str):
        """
        Salva os resultados em formato BibTeX
        
        Args:
            articles: Lista de artigos
            filename: Nome do arquivo de saída
        """
        if not articles:
            print("Nenhum artigo para salvar.")
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            for i, article in enumerate(articles, 1):
                info = self.extract_article_info(article)
                
                # Criar chave BibTeX
                first_author = info['authors'].split(',')[0].replace(' ', '')
                year = info['date'][:4] if len(info['date']) >= 4 else '0000'
                key = f"{first_author}{year}"
                
                # Escrever entrada BibTeX
                f.write(f"@article{{{key},\n")
                f.write(f"  title = {{{info['title']}}},\n")
                f.write(f"  author = {{{info['authors']}}},\n")
                f.write(f"  journal = {{{info['journal']}}},\n")
                f.write(f"  year = {{{year}}},\n")
                f.write(f"  volume = {{{info['volume']}}},\n")
                f.write(f"  number = {{{info['issue']}}},\n")
                f.write(f"  pages = {{{info['pages']}}},\n")
                f.write(f"  doi = {{{info['doi']}}},\n")
                f.write(f"  url = {{{info['url']}}}\n")
                f.write("}\n\n")
                
        print(f"✓ Referências BibTeX salvas em: {filename}")
        
    def print_summary(self, articles: List[Dict]):
        """
        Imprime um resumo dos resultados
        
        Args:
            articles: Lista de artigos
        """
        print(f"\n{'='*80}")
        print(f"RESUMO DA BUSCA")
        print(f"{'='*80}")
        print(f"Total de artigos encontrados: {len(articles)}")
        
        if articles:
            # Contar por tipo de acesso
            open_access = sum(1 for a in articles if a.get('openaccess', False))
            print(f"Acesso aberto: {open_access}")
            print(f"Acesso restrito: {len(articles) - open_access}")
            
            # Journals mais frequentes
            journals = {}
            for article in articles:
                journal = article.get('publicationName', 'N/A')
                journals[journal] = journals.get(journal, 0) + 1
                
            print(f"\nTop 5 Journals:")
            for journal, count in sorted(journals.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {journal}: {count} artigos")
                
            # Anos mais frequentes
            years = {}
            for article in articles:
                date = article.get('coverDate', '')
                year = date[:4] if len(date) >= 4 else 'N/A'
                years[year] = years.get(year, 0) + 1
                
            print(f"\nDistribuição por ano:")
            for year, count in sorted(years.items(), reverse=True)[:10]:
                print(f"  • {year}: {count} artigos")
        
        print(f"{'='*80}\n")


def main():
    """Função principal com exemplo de uso"""
    
    # CONFIGURAÇÃO
    API_KEY = "465a2fe04ff2d247552d79c320c3c7c6"  # Sua chave API
    
    # Criar diretório de resultados
    output_dir = "resultados_sciencedirect"
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializar busca
    searcher = ScienceDirectSearch(API_KEY)
    
    # EXEMPLO DE BUSCAS
    print("="*80)
    print("BUSCA DE ARTIGOS NO SCIENCEDIRECT")
    print("="*80)
    
    # Busca 1: Geotêxteis biodegradáveis
    print("\n[1] Buscando: geotextiles AND biodegradation")
    query1 = "geotextiles AND biodegradation"
    results1 = searcher.search_all_pages(
        query=query1,
        max_results=50,
        date_from="2015-01-01",
        pub_type="Research articles"
    )
    
    if results1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"{output_dir}/geotextiles_biodegradation_{timestamp}.csv"
        bib_file = f"{output_dir}/geotextiles_biodegradation_{timestamp}.bib"
        
        searcher.save_to_csv(results1, csv_file)
        searcher.save_to_bibtex(results1, bib_file)
        searcher.print_summary(results1)
        
        # Mostrar primeiros 3 artigos
        print("\nPrimeiros 3 artigos encontrados:")
        for i, article in enumerate(results1[:3], 1):
            info = searcher.extract_article_info(article)
            print(f"\n{i}. {info['title']}")
            print(f"   Autores: {info['authors'][:100]}...")
            print(f"   Journal: {info['journal']}")
            print(f"   Data: {info['date']}")
            print(f"   DOI: {info['doi']}")
    
    # Busca 2: Fibras naturais em engenharia de solos
    print("\n" + "="*80)
    print("\n[2] Buscando: natural fibers AND soil bioengineering")
    query2 = "(natural fibers OR lignocellulosic) AND (soil bioengineering OR slope stabilization)"
    results2 = searcher.search_all_pages(
        query=query2,
        max_results=50,
        date_from="2018-01-01"
    )
    
    if results2:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"{output_dir}/natural_fibers_bioengineering_{timestamp}.csv"
        bib_file = f"{output_dir}/natural_fibers_bioengineering_{timestamp}.bib"
        
        searcher.save_to_csv(results2, csv_file)
        searcher.save_to_bibtex(results2, bib_file)
        searcher.print_summary(results2)
    
    print("\n✓ Buscas concluídas!")
    print(f"✓ Resultados salvos em: {output_dir}/")


if __name__ == "__main__":
    # Verificar se pandas está instalado
    try:
        import pandas as pd
        import requests
    except ImportError:
        print("ERRO: Bibliotecas necessárias não encontradas.")
        print("Execute: pip install pandas requests")
        exit(1)
    
    main()
