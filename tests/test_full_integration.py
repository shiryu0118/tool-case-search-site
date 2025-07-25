"""
全機能の統合テスト
"""

import pytest
import os
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime

from app import create_app
from database.init_db import initialize_database
from services.search_service import SearchService
from services.storage_service import StorageService
from models.article import Article


class TestFullIntegration:
    """全機能の統合テスト"""
    
    @pytest.fixture
    def setup_real_db(self):
        """実際のSQLiteデータベースを使用するテスト環境をセットアップ"""
        # 一時ファイルを作成
        db_fd, db_path = tempfile.mkstemp()
        
        # アプリケーションを設定
        app = create_app(testing=True)
        app.config['DATABASE_PATH'] = db_path
        
        # データベースを初期化
        with app.app_context():
            initialize_database()
        
        yield app, db_path
        
        # クリーンアップ
        os.close(db_fd)
        os.unlink(db_path)
    
    @pytest.mark.integration
    @patch('integrations.zenn_client.ZennClient.search_articles')
    @patch('integrations.qiita_client.QiitaClient.search_articles')
    @patch('integrations.hatena_client.HatenaClient.search_articles')
    def test_search_and_storage_integration(self, mock_hatena, mock_qiita, mock_zenn, setup_real_db):
        """
        検索サービスとストレージサービスの統合テスト
        """
        app, db_path = setup_real_db
        
        # モックの設定
        mock_zenn.return_value = [
            Article(
                title="Zennのテスト記事",
                url="https://zenn.dev/test/articles/integration-test",
                platform="zenn",
                published_date=datetime.now(),
                summary="Zennのテスト記事の概要"
            )
        ]
        
        mock_qiita.return_value = [
            Article(
                title="Qiitaのテスト記事",
                url="https://qiita.com/test/items/integration-test",
                platform="qiita",
                published_date=datetime.now(),
                summary="Qiitaのテスト記事の概要"
            )
        ]
        
        mock_hatena.return_value = [
            Article(
                title="はてなブログのテスト記事",
                url="https://test.hatenablog.com/entry/integration-test",
                platform="hatena",
                published_date=datetime.now(),
                summary="はてなブログのテスト記事の概要"
            )
        ]
        
        with app.app_context():
            # サービスのインスタンス化
            search_service = SearchService()
            storage_service = StorageService()
            
            # 検索実行
            articles = search_service.search_articles("統合テスト")
            
            # 検索結果の検証
            assert len(articles) == 3
            platforms = [article.platform for article in articles]
            assert "zenn" in platforms
            assert "qiita" in platforms
            assert "hatena" in platforms
            
            # 検索結果の保存
            search_result = {
                'search_query': "統合テスト",
                'articles': articles,
                'search_date': datetime.now(),
                'total_count': len(articles)
            }
            
            save_success = storage_service.save_search_result(search_result)
            assert save_success is True
            
            # 保存された検索履歴の取得
            search_history = storage_service.get_search_history()
            
            # 検索履歴の検証
            assert len(search_history) == 1
            assert search_history[0]['search_query'] == "統合テスト"
            assert search_history[0]['total_articles'] == 3
            
            # 検索結果詳細の取得
            result_detail = storage_service.get_search_result_by_id(search_history[0]['id'])
            
            # 検索結果詳細の検証
            assert result_detail is not None
            assert result_detail['search_query'] == "統合テスト"
            assert len(result_detail['articles']) == 3
    
    @pytest.mark.integration
    def test_error_handling_integration(self, setup_real_db):
        """
        エラーハンドリングの統合テスト
        """
        app, db_path = setup_real_db
        
        with app.test_client() as client:
            # 存在しないページへのアクセス
            response = client.get('/non_existent_page')
            assert response.status_code == 404
            
            # 空の検索クエリ
            response = client.post('/search', data={'tool_name': ''}, follow_redirects=True)
            assert response.status_code == 200
            assert b'ツール名を入力してください' in response.data
            
            # 存在しない検索結果ID
            response = client.get('/history/999', follow_redirects=True)
            assert response.status_code == 200
            assert b'指定された検索結果が見つかりません' in response.data
    
    @pytest.mark.integration
    @patch('services.search_service.SearchService.search_articles')
    def test_full_web_flow_integration(self, mock_search, setup_real_db):
        """
        Webフロー全体の統合テスト
        """
        app, db_path = setup_real_db
        
        # モックの設定
        mock_articles = [
            Article(
                title="統合テスト記事1",
                url="https://example.com/integration-test-1",
                platform="zenn",
                published_date=datetime.now(),
                summary="統合テスト用の記事1の概要"
            ),
            Article(
                title="統合テスト記事2",
                url="https://example.com/integration-test-2",
                platform="qiita",
                published_date=datetime.now(),
                summary="統合テスト用の記事2の概要"
            )
        ]
        mock_search.return_value = mock_articles
        
        with app.test_client() as client:
            # ホームページにアクセス
            response = client.get('/')
            assert response.status_code == 200
            assert b'<title>ホーム - ツール活用事例検索サイト</title>' in response.data
            
            # 検索を実行
            response = client.post('/search', data={'tool_name': '統合テスト'}, follow_redirects=True)
            assert response.status_code == 200
            assert b'統合テスト記事1' in response.data
            assert b'統合テスト記事2' in response.data
            
            # 検索履歴ページにアクセス
            response = client.get('/history')
            assert response.status_code == 200
            assert b'<title>検索履歴 - ツール活用事例検索サイト</title>' in response.data
            assert b'統合テスト' in response.data
            
            # データベースに直接アクセスして検証
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 検索履歴の確認
            cursor.execute("SELECT * FROM search_history")
            history = cursor.fetchall()
            assert len(history) == 1
            assert history[0]['search_query'] == '統合テスト'
            
            # 記事データの確認
            cursor.execute("SELECT * FROM articles")
            articles = cursor.fetchall()
            assert len(articles) == 2
            
            conn.close()