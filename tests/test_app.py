"""
Flaskアプリケーションの統合テスト
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from models.article import Article


class TestFlaskApp:
    """Flaskアプリケーションの統合テスト"""
    
    def test_index_route(self, client):
        """インデックスページが正常に表示されることを確認"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<title>ホーム - ツール活用事例検索サイト</title>' in response.data
        assert b'<form method="POST" action="/search"' in response.data
    
    @patch('services.search_service.SearchService.search_articles')
    @patch('services.storage_service.StorageService.save_search_result')
    def test_search_route_with_valid_query(self, mock_save, mock_search, client):
        """有効なクエリでの検索が正常に動作することを確認"""
        # モックの設定
        mock_articles = [
            Article(
                title="テスト記事",
                url="https://example.com/test",
                platform="zenn",
                published_date=datetime.now(),
                summary="テスト記事の概要"
            )
        ]
        mock_search.return_value = mock_articles
        mock_save.return_value = True
        
        # 検索リクエスト
        response = client.post('/search', data={'tool_name': 'テスト'}, follow_redirects=True)
        
        # 検証
        assert response.status_code == 200
        assert b'<title>検索結果 - テスト - ツール活用事例検索サイト</title>' in response.data
        assert b'テスト記事' in response.data
        assert b'https://example.com/test' in response.data
        
        # モックが呼び出されたことを確認
        mock_search.assert_called_once_with('テスト')
        mock_save.assert_called_once()
    
    def test_search_route_with_empty_query(self, client):
        """空のクエリでの検索がエラーメッセージを表示することを確認"""
        response = client.post('/search', data={'tool_name': ''}, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'ツール名を入力してください' in response.data
    
    @patch('services.storage_service.StorageService.get_search_history')
    def test_history_route(self, mock_get_history, client):
        """検索履歴ページが正常に表示されることを確認"""
        # モックの設定
        mock_history = [
            {
                'id': 1,
                'search_query': 'テスト',
                'search_date': datetime.now(),
                'total_articles': 2,
                'platform_breakdown': {'zenn': 1, 'qiita': 1},
                'recent_articles': [
                    {
                        'title': 'テスト記事1',
                        'url': 'https://example.com/test1',
                        'platform': 'zenn',
                        'published_date': datetime.now()
                    },
                    {
                        'title': 'テスト記事2',
                        'url': 'https://example.com/test2',
                        'platform': 'qiita',
                        'published_date': datetime.now()
                    }
                ]
            }
        ]
        mock_get_history.return_value = mock_history
        
        # 履歴ページリクエスト
        response = client.get('/history')
        
        # 検証
        assert response.status_code == 200
        assert b'<title>検索履歴 - ツール活用事例検索サイト</title>' in response.data
        assert b'テスト' in response.data
        assert b'テスト記事1' in response.data
        
        # モックが呼び出されたことを確認
        mock_get_history.assert_called_once()
    
    @patch('services.storage_service.StorageService.get_search_history')
    def test_history_route_with_empty_history(self, mock_get_history, client):
        """空の検索履歴の場合に適切なメッセージが表示されることを確認"""
        # モックの設定
        mock_get_history.return_value = []
        
        # 履歴ページリクエスト
        response = client.get('/history')
        
        # 検証
        assert response.status_code == 200
        assert b'検索履歴がありません' in response.data
        
        # モックが呼び出されたことを確認
        mock_get_history.assert_called_once()
    
    @patch('services.storage_service.StorageService.get_search_result_by_id')
    def test_history_detail_route(self, mock_get_result, client):
        """検索履歴詳細ページが正常に表示されることを確認"""
        # モックの設定
        mock_articles = [
            Article(
                title="テスト記事",
                url="https://example.com/test",
                platform="zenn",
                published_date=datetime.now(),
                summary="テスト記事の概要"
            )
        ]
        mock_result = {
            'id': 1,
            'search_query': 'テスト',
            'search_date': datetime.now(),
            'total_count': 1,
            'articles': mock_articles,
            'platform_stats': {'zenn': 1}
        }
        mock_get_result.return_value = mock_result
        
        # 履歴詳細ページリクエスト
        response = client.get('/history/1')
        
        # 検証
        assert response.status_code == 200
        assert b'テスト記事' in response.data
        assert b'https://example.com/test' in response.data
        
        # モックが呼び出されたことを確認
        mock_get_result.assert_called_once_with(1)
    
    @patch('services.storage_service.StorageService.get_search_result_by_id')
    def test_history_detail_route_with_invalid_id(self, mock_get_result, client):
        """無効なIDでの履歴詳細リクエストがエラーメッセージを表示することを確認"""
        # モックの設定
        mock_get_result.return_value = None
        
        # 履歴詳細ページリクエスト
        response = client.get('/history/999', follow_redirects=True)
        
        # 検証
        assert response.status_code == 200
        assert b'指定された検索結果が見つかりません' in response.data
        
        # モックが呼び出されたことを確認
        mock_get_result.assert_called_once_with(999)
    
    def test_health_check_route(self, client):
        """ヘルスチェックエンドポイントが正常に動作することを確認"""
        response = client.get('/health')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_not_found_error(self, client):
        """存在しないページへのアクセスが404エラーを返すことを確認"""
        response = client.get('/non_existent_page')
        
        assert response.status_code == 404