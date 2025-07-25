"""
サービス層のユニットテスト
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.article import Article
from services.search_service import SearchService
from services.storage_service import StorageService


class TestSearchService:
    """SearchServiceのテスト"""
    
    def test_search_articles_with_valid_query(self, monkeypatch):
        """有効なクエリで検索が実行できることを確認"""
        # モックの設定
        mock_zenn_result = [
            Article(
                title="Zenn記事",
                url="https://zenn.dev/test",
                platform="zenn",
                published_date=datetime.now()
            )
        ]
        
        mock_qiita_result = [
            Article(
                title="Qiita記事",
                url="https://qiita.com/test",
                platform="qiita",
                published_date=datetime.now()
            )
        ]
        
        mock_hatena_result = [
            Article(
                title="はてな記事",
                url="https://hatenablog.com/test",
                platform="hatena",
                published_date=datetime.now()
            )
        ]
        
        # 各クライアントのsearch_articles関数をモック化
        def mock_zenn_search(*args, **kwargs):
            return mock_zenn_result
        
        def mock_qiita_search(*args, **kwargs):
            return mock_qiita_result
        
        def mock_hatena_search(*args, **kwargs):
            return mock_hatena_result
        
        monkeypatch.setattr('services.search_service.ZennClient.search_articles', mock_zenn_search)
        monkeypatch.setattr('services.search_service.QiitaClient.search_articles', mock_qiita_search)
        monkeypatch.setattr('services.search_service.HatenaClient.search_articles', mock_hatena_search)
        
        # テスト実行
        service = SearchService()
        result = service.search_articles("テスト")
        
        # 検証
        assert result.search_query == "テスト"
        assert len(result.articles) == 3
        assert result.total_count == 3
        
        # 各プラットフォームの記事が含まれていることを確認
        platforms = [article.platform for article in result.articles]
        assert "zenn" in platforms
        assert "qiita" in platforms
        assert "hatena" in platforms
    
    def test_search_articles_with_empty_query(self):
        """空のクエリで検索した場合に空の結果が返ることを確認"""
        service = SearchService()
        result = service.search_articles("")
        
        assert result.search_query == ""
        assert len(result.articles) == 0
        assert result.total_count == 0
    
    def test_search_articles_with_api_error(self, monkeypatch):
        """APIエラーが発生した場合でも他のプラットフォームの検索が継続されることを確認"""
        # モックの設定
        mock_zenn_result = [
            Article(
                title="Zenn記事",
                url="https://zenn.dev/test",
                platform="zenn",
                published_date=datetime.now()
            )
        ]
        
        # Qiitaはエラーを発生させる
        def mock_zenn_search(*args, **kwargs):
            return mock_zenn_result
        
        def mock_qiita_search(*args, **kwargs):
            raise Exception("API Error")
        
        def mock_hatena_search(*args, **kwargs):
            return []
        
        monkeypatch.setattr('services.search_service.ZennClient.search_articles', mock_zenn_search)
        monkeypatch.setattr('services.search_service.QiitaClient.search_articles', mock_qiita_search)
        monkeypatch.setattr('services.search_service.HatenaClient.search_articles', mock_hatena_search)
        
        # テスト実行
        service = SearchService()
        result = service.search_articles("テスト")
        
        # 検証 - Qiitaのエラーにもかかわらず、Zennの結果が含まれていることを確認
        assert result.search_query == "テスト"
        assert len(result.articles) == 1
        assert result.total_count == 1
        assert result.articles[0].platform == "zenn"
    
    def test_remove_duplicates(self):
        """重複URLの記事が除去されることを確認"""
        # 重複URLを含む記事リスト
        articles = [
            Article(
                title="記事1",
                url="https://example.com/test1",
                platform="zenn"
            ),
            Article(
                title="記事2",
                url="https://example.com/test2",
                platform="qiita"
            ),
            Article(
                title="記事3（重複）",
                url="https://example.com/test1",  # 重複URL
                platform="hatena"
            )
        ]
        
        service = SearchService()
        unique_articles = service._remove_duplicates(articles)
        
        # 検証
        assert len(unique_articles) == 2
        urls = [article.url for article in unique_articles]
        assert "https://example.com/test1" in urls
        assert "https://example.com/test2" in urls
        assert urls.count("https://example.com/test1") == 1  # 重複が除去されていることを確認


class TestStorageService:
    """StorageServiceのテスト"""
    
    def test_save_search_result(self, test_db, sample_articles):
        """検索結果が正常に保存されることを確認"""
        # テスト用のStorageServiceを作成
        service = StorageService(db_path=':memory:')
        service._get_db_connection = MagicMock(return_value=test_db)
        
        # テスト用の検索結果データ
        search_result = {
            'search_query': 'テスト',
            'articles': sample_articles,
            'search_date': datetime.now(),
            'total_count': len(sample_articles)
        }
        
        # 保存実行
        result = service.save_search_result(search_result)
        
        # 検証
        assert result is True
        
        # データベースに保存されたことを確認
        cursor = test_db.cursor()
        cursor.execute("SELECT * FROM search_history")
        history_rows = cursor.fetchall()
        assert len(history_rows) == 1
        assert history_rows[0]['search_query'] == 'テスト'
        assert history_rows[0]['total_articles'] == len(sample_articles)
        
        # 記事も保存されていることを確認
        cursor.execute("SELECT * FROM articles")
        article_rows = cursor.fetchall()
        assert len(article_rows) == len(sample_articles)
    
    def test_get_search_history(self, test_db):
        """検索履歴が正常に取得できることを確認"""
        # テストデータの準備
        cursor = test_db.cursor()
        cursor.execute(
            """
            INSERT INTO search_history (search_query, search_date, total_articles)
            VALUES (?, ?, ?)
            """,
            ('テスト1', datetime.now().isoformat(), 2)
        )
        history_id = cursor.lastrowid
        
        cursor.execute(
            """
            INSERT INTO articles (
                search_history_id, title, url, platform, 
                published_date, summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                history_id,
                'テスト記事1',
                'https://example.com/test1',
                'zenn',
                datetime.now().isoformat(),
                'テスト記事1の概要',
                datetime.now().isoformat()
            )
        )
        
        cursor.execute(
            """
            INSERT INTO articles (
                search_history_id, title, url, platform, 
                published_date, summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                history_id,
                'テスト記事2',
                'https://example.com/test2',
                'qiita',
                datetime.now().isoformat(),
                'テスト記事2の概要',
                datetime.now().isoformat()
            )
        )
        
        test_db.commit()
        
        # テスト用のStorageServiceを作成
        service = StorageService(db_path=':memory:')
        service._get_db_connection = MagicMock(return_value=test_db)
        
        # 検索履歴取得
        history = service.get_search_history()
        
        # 検証
        assert len(history) == 1
        assert history[0]['search_query'] == 'テスト1'
        assert history[0]['total_articles'] == 2
        assert 'platform_breakdown' in history[0]
        assert 'recent_articles' in history[0]
        assert len(history[0]['recent_articles']) == 2
    
    def test_get_search_result_by_id(self, test_db):
        """IDによる検索結果の取得が正常に動作することを確認"""
        # テストデータの準備
        cursor = test_db.cursor()
        cursor.execute(
            """
            INSERT INTO search_history (search_query, search_date, total_articles)
            VALUES (?, ?, ?)
            """,
            ('テスト1', datetime.now().isoformat(), 1)
        )
        history_id = cursor.lastrowid
        
        cursor.execute(
            """
            INSERT INTO articles (
                search_history_id, title, url, platform, 
                published_date, summary, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                history_id,
                'テスト記事1',
                'https://example.com/test1',
                'zenn',
                datetime.now().isoformat(),
                'テスト記事1の概要',
                datetime.now().isoformat()
            )
        )
        
        test_db.commit()
        
        # テスト用のStorageServiceを作成
        service = StorageService(db_path=':memory:')
        service._get_db_connection = MagicMock(return_value=test_db)
        
        # 検索結果取得
        result = service.get_search_result_by_id(history_id)
        
        # 検証
        assert result is not None
        assert result['search_query'] == 'テスト1'
        assert len(result['articles']) == 1
        assert result['articles'][0].title == 'テスト記事1'
        assert result['articles'][0].platform == 'zenn'
    
    def test_get_nonexistent_search_result(self, test_db):
        """存在しないIDの検索結果を取得しようとした場合にNoneが返ることを確認"""
        # テスト用のStorageServiceを作成
        service = StorageService(db_path=':memory:')
        service._get_db_connection = MagicMock(return_value=test_db)
        
        # 存在しないIDで検索
        result = service.get_search_result_by_id(999)
        
        # 検証
        assert result is None