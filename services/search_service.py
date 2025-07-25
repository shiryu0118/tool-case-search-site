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
            ("はてなブログ", self._search_hatena),
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
        Zennから記事を検索（デモ用サンプルデータ）
        """
        try:
            logger.debug(f"Searching Zenn for: {query}")
            
            # デモ用のサンプル記事データ
            sample_articles = [
                {
                    'title': f'{query}を使った開発環境構築のベストプラクティス',
                    'url': f'https://zenn.dev/example/{query.lower()}-development-setup',
                    'published_at': '2024-01-15T10:00:00Z',
                    'summary': f'{query}を使用した効率的な開発環境の構築方法について詳しく解説します。'
                },
                {
                    'title': f'{query}入門：初心者向けガイド',
                    'url': f'https://zenn.dev/example/{query.lower()}-beginner-guide',
                    'published_at': '2024-01-10T14:30:00Z',
                    'summary': f'{query}の基本概念から実践的な使い方まで、初心者にもわかりやすく説明します。'
                },
                {
                    'title': f'{query}のトラブルシューティング集',
                    'url': f'https://zenn.dev/example/{query.lower()}-troubleshooting',
                    'published_at': '2024-01-05T09:15:00Z',
                    'summary': f'{query}でよく遭遇する問題とその解決方法をまとめました。'
                }
            ]
            
            articles = []
            for item in sample_articles:
                try:
                    article = Article(
                        title=item['title'],
                        url=item['url'],
                        platform='Zenn',
                        published_date=datetime.fromisoformat(item['published_at'].replace('Z', '+00:00')),
                        summary=item['summary']
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to create Zenn article: {e}")
                    continue
            
            logger.info(f"Generated {len(articles)} sample Zenn articles for: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"Zenn search failed: {str(e)}")
            return []
    
    def _search_qiita(self, query: str) -> List[Article]:
        """
        Qiitaから記事を検索（デモ用サンプルデータ）
        """
        try:
            logger.debug(f"Searching Qiita for: {query}")
            
            # デモ用のサンプル記事データ
            sample_articles = [
                {
                    'title': f'{query}の基本的な使い方と応用例',
                    'url': f'https://qiita.com/example/{query.lower()}-basic-usage',
                    'created_at': '2024-01-20T16:45:00Z',
                    'body': f'{query}の基本的な使い方から応用例まで、実際のコード例を交えて解説します。初心者から上級者まで参考になる内容です。'
                },
                {
                    'title': f'{query}でのパフォーマンス最適化テクニック',
                    'url': f'https://qiita.com/example/{query.lower()}-performance',
                    'created_at': '2024-01-18T11:20:00Z',
                    'body': f'{query}を使用する際のパフォーマンス最適化について、実践的なテクニックを紹介します。'
                },
                {
                    'title': f'{query}と他ツールとの連携方法',
                    'url': f'https://qiita.com/example/{query.lower()}-integration',
                    'created_at': '2024-01-12T13:30:00Z',
                    'body': f'{query}を他のツールやサービスと連携させる方法について詳しく説明します。'
                },
                {
                    'title': f'{query}のセキュリティベストプラクティス',
                    'url': f'https://qiita.com/example/{query.lower()}-security',
                    'created_at': '2024-01-08T08:15:00Z',
                    'body': f'{query}を安全に使用するためのセキュリティ対策とベストプラクティスをまとめました。'
                }
            ]
            
            articles = []
            for item in sample_articles:
                try:
                    article = Article(
                        title=item['title'],
                        url=item['url'],
                        platform='Qiita',
                        published_date=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                        summary=item['body'][:200] + '...' if len(item['body']) > 200 else item['body']
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to create Qiita article: {e}")
                    continue
            
            logger.info(f"Generated {len(articles)} sample Qiita articles for: {query}")
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
    
    def _search_hatena(self, query: str) -> List[Article]:
        """
        はてなブログから記事を検索（デモ用サンプルデータ）
        """
        try:
            logger.debug(f"Searching はてなブログ for: {query}")
            
            # デモ用のサンプル記事データ
            sample_articles = [
                {
                    'title': f'{query}を導入してみた感想と注意点',
                    'url': f'https://example.hatenablog.com/entry/{query.lower()}-introduction',
                    'published_at': '2024-01-25T20:00:00Z',
                    'summary': f'実際に{query}を導入してみた体験談と、導入時に注意すべきポイントについて書きました。'
                },
                {
                    'title': f'{query}の学習ロードマップ',
                    'url': f'https://example.hatenablog.com/entry/{query.lower()}-roadmap',
                    'published_at': '2024-01-22T19:30:00Z',
                    'summary': f'{query}を効率的に学習するためのロードマップを作成しました。初心者向けです。'
                }
            ]
            
            articles = []
            for item in sample_articles:
                try:
                    article = Article(
                        title=item['title'],
                        url=item['url'],
                        platform='はてなブログ',
                        published_date=datetime.fromisoformat(item['published_at'].replace('Z', '+00:00')),
                        summary=item['summary']
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to create はてなブログ article: {e}")
                    continue
            
            logger.info(f"Generated {len(articles)} sample はてなブログ articles for: {query}")
            return articles
            
        except Exception as e:
            logger.error(f"はてなブログ search failed: {str(e)}")
            return []