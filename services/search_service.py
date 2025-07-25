"""
検索サービス - 複数プラットフォームからの記事検索を統合
"""
import logging
from typing import List, Optional
from datetime import datetime
import requests_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

# データモデルのインポート（実装予定）
try:
    from models.article import Article
    from models.search_result import SearchResult
except ImportError:
    # モデルが未実装の場合の仮定義
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class Article:
        title: str
        url: str
        platform: str
        published_date: Optional[datetime]
        summary: Optional[str] = None
    
    @dataclass
    class SearchResult:
        id: Optional[int]
        search_query: str
        articles: List[Article]
        search_date: datetime
        total_count: int

# 外部API統合クライアントのインポート（実装予定）
try:
    from integrations.zenn_client import ZennClient
    from integrations.qiita_client import QiitaClient
    from integrations.hatena_client import HatenaClient
except ImportError:
    # クライアントが未実装の場合のモッククラス
    class ZennClient:
        def search_articles(self, query: str) -> List[Article]:
            return []
    
    class QiitaClient:
        def search_articles(self, query: str) -> List[Article]:
            return []
    
    class HatenaClient:
        def search_articles(self, query: str) -> List[Article]:
            return []


logger = logging.getLogger(__name__)


class SearchService:
    """
    複数プラットフォームからの記事検索を統合するサービス
    
    要件:
    - 1.1: Zenn、Qiita、はてなブログから関連記事を検索
    - 1.2: 検索結果を一覧表示
    - 4.1: 1時間のキャッシュを適用
    - 4.2: 同じ検索クエリが短時間で実行される場合はキャッシュされた結果を返す
    """
    
    def __init__(self):
        """検索サービスを初期化"""
        # requests-cacheで1時間のキャッシュを設定
        self.session = requests_cache.CachedSession(
            cache_name='search_cache',
            expire_after=3600,  # 1時間
            backend='sqlite'
        )
        
        # 各プラットフォームのクライアントを初期化
        self.zenn_client = ZennClient()
        self.qiita_client = QiitaClient()
        self.hatena_client = HatenaClient()
        
        logger.info("SearchService initialized with 1-hour cache")
    
    def search_articles(self, tool_name: str) -> SearchResult:
        """
        指定されたツール名で複数プラットフォームから記事を検索
        
        Args:
            tool_name (str): 検索するツール名
            
        Returns:
            SearchResult: 検索結果オブジェクト
            
        要件:
        - 1.1: 複数プラットフォームから検索
        - 4.1: キャッシュ機能
        - 4.4: APIが利用できない場合は他のプラットフォームの検索を継続
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
            ("はてなブログ", self._search_hatena)
        ]
        
        # 並列実行で各プラットフォームを検索
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_platform = {
                executor.submit(search_func, tool_name): platform_name
                for platform_name, search_func in search_functions
            }
            
            for future in as_completed(future_to_platform):
                platform_name = future_to_platform[future]
                try:
                    articles = future.result(timeout=30)  # 30秒タイムアウト
                    all_articles.extend(articles)
                    logger.info(f"Found {len(articles)} articles from {platform_name}")
                except Exception as e:
                    logger.error(f"Error searching {platform_name}: {str(e)}")
                    # 他のプラットフォームの検索を継続（要件4.4）
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
        
        Args:
            query (str): 検索クエリ
            
        Returns:
            List[Article]: 検索結果の記事リスト
        """
        try:
            logger.debug(f"Searching Zenn for: {query}")
            return self.zenn_client.search_articles(query)
        except Exception as e:
            logger.error(f"Zenn search failed: {str(e)}")
            return []
    
    def _search_qiita(self, query: str) -> List[Article]:
        """
        Qiitaから記事を検索
        
        Args:
            query (str): 検索クエリ
            
        Returns:
            List[Article]: 検索結果の記事リスト
        """
        try:
            logger.debug(f"Searching Qiita for: {query}")
            return self.qiita_client.search_articles(query)
        except Exception as e:
            logger.error(f"Qiita search failed: {str(e)}")
            return []
    
    def _search_hatena(self, query: str) -> List[Article]:
        """
        はてなブログから記事を検索
        
        Args:
            query (str): 検索クエリ
            
        Returns:
            List[Article]: 検索結果の記事リスト
        """
        try:
            logger.debug(f"Searching はてなブログ for: {query}")
            return self.hatena_client.search_articles(query)
        except Exception as e:
            logger.error(f"はてなブログ search failed: {str(e)}")
            return []
    
    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """
        記事リストから重複URLを除去
        
        Args:
            articles (List[Article]): 記事リスト
            
        Returns:
            List[Article]: 重複除去後の記事リスト
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
        try:
            self.session.cache.clear()
            logger.info("Search cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
    
    def get_cache_info(self) -> dict:
        """
        キャッシュ情報を取得
        
        Returns:
            dict: キャッシュ統計情報
        """
        try:
            return {
                'cache_size': len(self.session.cache.responses),
                'cache_backend': str(type(self.session.cache.responses)),
                'expire_after': self.session.cache.expire_after
            }
        except Exception as e:
            logger.error(f"Failed to get cache info: {str(e)}")
            return {}