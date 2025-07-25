"""
外部API統合のモックテスト
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
import json
from datetime import datetime
from services.search_service import SearchService
from models.article import Article


class TestAPIIntegration:
    """外部API統合のモックテスト"""
    
    @patch('requests.get')
    def test_zenn_api_integration(self, mock_get):
        """ZennのAPI統合が正常に動作することを確認"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'Zennのテスト記事',
                    'path': '/username/articles/test-article',
                    'published_at': '2023-01-01T00:00:00Z',
                    'body_letters_count': 1000
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # ZennClientのインポート
        from integrations.zenn_client import ZennClient
        
        # テスト実行
        client = ZennClient()
        articles = client.search_articles('テスト')
        
        # 検証
        assert len(articles) == 1
        assert articles[0].title == 'Zennのテスト記事'
        assert articles[0].url == 'https://zenn.dev/username/articles/test-article'
        assert articles[0].platform == 'zenn'
        
        # APIが正しく呼び出されたことを確認
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'https://zenn.dev/api/search' in args[0]
        assert 'q=テスト' in args[0]
    
    @patch('requests.get')
    def test_qiita_api_integration(self, mock_get):
        """QiitaのAPI統合が正常に動作することを確認"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'title': 'Qiitaのテスト記事',
                'url': 'https://qiita.com/username/items/test-article',
                'created_at': '2023-01-01T00:00:00Z',
                'body': 'テスト記事の本文'
            }
        ]
        mock_get.return_value = mock_response
        
        # QiitaClientのインポート
        from integrations.qiita_client import QiitaClient
        
        # テスト実行
        client = QiitaClient()
        articles = client.search_articles('テスト')
        
        # 検証
        assert len(articles) == 1
        assert articles[0].title == 'Qiitaのテスト記事'
        assert articles[0].url == 'https://qiita.com/username/items/test-article'
        assert articles[0].platform == 'qiita'
        
        # APIが正しく呼び出されたことを確認
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'https://qiita.com/api/v2/items' in args[0]
        assert 'query=テスト' in args[0]
    
    @patch('requests.get')
    def test_hatena_api_integration(self, mock_get):
        """はてなブログのAPI統合が正常に動作することを確認"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="search-result">
                    <h3 class="entry-title">
                        <a href="https://example.hatenablog.com/entry/test-article">はてなブログのテスト記事</a>
                    </h3>
                    <div class="entry-summary">テスト記事の概要</div>
                    <div class="entry-date">2023-01-01</div>
                </div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # HatenaClientのインポート
        from integrations.hatena_client import HatenaClient
        
        # テスト実行
        client = HatenaClient()
        articles = client.search_articles('テスト')
        
        # 検証
        assert len(articles) == 1
        assert articles[0].title == 'はてなブログのテスト記事'
        assert articles[0].url == 'https://example.hatenablog.com/entry/test-article'
        assert articles[0].platform == 'hatena'
        
        # APIが正しく呼び出されたことを確認
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'https://search.hatena.ne.jp/search' in args[0]
        assert 'q=テスト' in args[0]
    
    @patch('services.search_service.ZennClient')
    @patch('services.search_service.QiitaClient')
    @patch('services.search_service.HatenaClient')
    def test_search_service_integration(self, mock_hatena, mock_qiita, mock_zenn):
        """SearchServiceが各APIクライアントを正しく統合していることを確認"""
        # モックの設定
        mock_zenn_instance = MagicMock()
        mock_qiita_instance = MagicMock()
        mock_hatena_instance = MagicMock()
        
        mock_zenn.return_value = mock_zenn_instance
        mock_qiita.return_value = mock_qiita_instance
        mock_hatena.return_value = mock_hatena_instance
        
        mock_zenn_instance.search_articles.return_value = [
            Article(
                title="Zennのテスト記事",
                url="https://zenn.dev/test",
                platform="zenn",
                published_date=datetime.now()
            )
        ]
        
        mock_qiita_instance.search_articles.return_value = [
            Article(
                title="Qiitaのテスト記事",
                url="https://qiita.com/test",
                platform="qiita",
                published_date=datetime.now()
            )
        ]
        
        mock_hatena_instance.search_articles.return_value = [
            Article(
                title="はてなブログのテスト記事",
                url="https://hatenablog.com/test",
                platform="hatena",
                published_date=datetime.now()
            )
        ]
        
        # テスト実行
        service = SearchService()
        result = service.search_articles('テスト')
        
        # 検証
        assert result.search_query == 'テスト'
        assert len(result.articles) == 3
        assert result.total_count == 3
        
        # 各クライアントが呼び出されたことを確認
        mock_zenn_instance.search_articles.assert_called_once_with('テスト')
        mock_qiita_instance.search_articles.assert_called_once_with('テスト')
        mock_hatena_instance.search_articles.assert_called_once_with('テスト')
    
    @patch('requests_cache.CachedSession')
    def test_search_service_caching(self, mock_cached_session):
        """SearchServiceのキャッシュ機能が正常に動作することを確認"""
        # モックの設定
        mock_session = MagicMock()
        mock_cached_session.return_value = mock_session
        
        # テスト実行
        service = SearchService()
        
        # 検証
        mock_cached_session.assert_called_once()
        assert service.session == mock_session
        
        # キャッシュ設定の確認
        args, kwargs = mock_cached_session.call_args
        assert kwargs['cache_name'] == 'search_cache'
        assert kwargs['expire_after'] == 3600  # 1時間
        assert kwargs['backend'] == 'sqlite'