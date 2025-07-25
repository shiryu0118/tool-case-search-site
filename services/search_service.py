"""
検索サービス - 複数プラットフォームからの記事検索を統合
"""
import logging
import requests
from typing import List, Optional
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from models.article import Article
from models.search_result import SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    """
    複数プラットフォームからの記事検索を統合するサービス
    """
    
    def __init__(self):
        """検索サービスを初期化"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Tool-Case-Search-Site/1.0'
        })
        logger.info("SearchService initialized")
    
    def search_articles(self, tool_name: str) -> SearchResult:
        """
        指定されたツール名で複数プラットフォームから記事を検索
        
        Args:
            tool_name (str): 検索するツール名
            
        Returns:
            SearchResult: 検索結果オブジェクト
        """
        if not tool_name or not tool_name.strip():
            logger.warning("Empty search query provided")
            return SearchResult(
                id=None,
                search_query=tool_name,
                articles=[],
                search_date=datetime.now(),
                total_count=0
            )
        
        logger.info(f"Starting search for tool: {tool_name}")
        
        all_articles = []
        search_functions = [
            ("Zenn", self._search_zenn),
            ("Qiita", self._search_qiita),
        ]
        
        # 各プラットフォームを検索
        for platform_name, search_func in search_functions:
            try:
                articles = search_func(tool_name)
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {platform_name}")
            except Exception as e:
                logger.error(f"Error searching {platform_name}: {str(e)}")
                continue
        
        # 重複URLを除去
        unique_articles = self._remove_duplicates(all_articles)
        
        search_result = SearchResult(
            id=None,
            search_query=tool_name,
            articles=unique_articles,
            search_date=datetime.now(),
            total_count=len(unique_articles)
        )
        
        logger.info(f"Search completed. Total unique articles: {len(unique_articles)}")
        return search_result
    
    def _search_zenn(self, query: str) -> List[Article]:
        """
        Zennから記事を検索
        """
        try:
            logger.debug(f"Searching Zenn for: {query}")
            
            # Zenn APIを使用して検索
            url = "https://zenn.dev/api/search"
            params = {
                'q': query,
                'order': 'latest',
                'count': 20
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('articles', []):
                try:
                    article = Article(
                        title=item.get('title', ''),
                        url=f"https://zenn.dev{item.get('path', '')}",
                        platform='Zenn',
                        published_date=datetime.fromisoformat(item.get('published_at', '').replace('Z', '+00:00')) if item.get('published_at') else None,
                        summary=item.get('body_letters_count', '')[:200] if item.get('body_letters_count') else None
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to parse Zenn article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Zenn search failed: {str(e)}")
            return []
    
    def _search_qiita(self, query: str) -> List[Article]:
        """
        Qiitaから記事を検索
        """
        try:
            logger.debug(f"Searching Qiita for: {query}")
            
            # Qiita APIを使用して検索
            url = "https://qiita.com/api/v2/items"
            params = {
                'query': query,
                'per_page': 20,
                'page': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data:
                try:
                    article = Article(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        platform='Qiita',
                        published_date=datetime.fromisoformat(item.get('created_at', '').replace('Z', '+00:00')) if item.get('created_at') else None,
                        summary=item.get('body', '')[:200] if item.get('body') else None
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to parse Qiita article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Qiita search failed: {str(e)}")
            return []
    
    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """
        記事リストから重複URLを除去
        """
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
            else:
                logger.debug(f"Duplicate URL removed: {article.url}")
        
        return unique_articles
    
    def clear_cache(self):
        """
        検索キャッシュをクリア
        """
        logger.info("Cache clear requested (not implemented)")
    
    def get_cache_info(self) -> dict:
        """
        キャッシュ情報を取得
        """
        return {
            'cache_size': 0,
            'cache_backend': 'none',
            'expire_after': 0
        }