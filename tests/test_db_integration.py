"""
データベース操作の統合テスト
"""

import pytest
import sqlite3
import os
from datetime import datetime
from models.article import Article
from database.init_db import initialize_database


class TestDatabaseIntegration:
    """データベース操作の統合テスト"""
    
    @pytest.fixture
    def test_db_file(self):
        """テスト用の一時データベースファイルを作成"""
        db_path = "test_app.db"
        
        # テスト前にデータベースファイルが存在する場合は削除
        if os.path.exists(db_path):
            os.remove(db_path)
        
        yield db_path
        
        # テスト後にデータベースファイルを削除
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_initialize_database(self, test_db_file):
        """データベースの初期化が正常に動作することを確認"""
        # 環境変数のモック
        os.environ['DATABASE_PATH'] = test_db_file
        
        # データベース初期化
        initialize_database()
        
        # データベースが作成されたことを確認
        assert os.path.exists(test_db_file)
        
        # テーブルが作成されたことを確認
        conn = sqlite3.connect(test_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # search_historyテーブルの確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_history'")
        assert cursor.fetchone() is not None
        
        # articlesテーブルの確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
        assert cursor.fetchone() is not None
        
        # インデックスの確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_search_query'")
        assert cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_platform'")
        assert cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_url'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_database_crud_operations(self, test_db_file):
        """データベースのCRUD操作が正常に動作することを確認"""
        # 環境変数のモック
        os.environ['DATABASE_PATH'] = test_db_file
        
        # データベース初期化
        initialize_database()
        
        # データベース接続
        conn = sqlite3.connect(test_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. 検索履歴の作成（Create）
        cursor.execute(
            """
            INSERT INTO search_history (search_query, search_date, total_articles)
            VALUES (?, ?, ?)
            """,
            ('テスト', datetime.now().isoformat(), 2)
        )
        history_id = cursor.lastrowid
        
        # 記事の作成
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
        
        conn.commit()
        
        # 2. 検索履歴の読み取り（Read）
        cursor.execute("SELECT * FROM search_history WHERE id = ?", (history_id,))
        history = cursor.fetchone()
        
        assert history is not None
        assert history['search_query'] == 'テスト'
        assert history['total_articles'] == 2
        
        # 記事の読み取り
        cursor.execute("SELECT * FROM articles WHERE search_history_id = ?", (history_id,))
        articles = cursor.fetchall()
        
        assert len(articles) == 2
        assert articles[0]['title'] == 'テスト記事1'
        assert articles[1]['title'] == 'テスト記事2'
        
        # 3. 検索履歴の更新（Update）
        cursor.execute(
            "UPDATE search_history SET search_query = ? WHERE id = ?",
            ('更新テスト', history_id)
        )
        conn.commit()
        
        cursor.execute("SELECT search_query FROM search_history WHERE id = ?", (history_id,))
        updated_history = cursor.fetchone()
        
        assert updated_history['search_query'] == '更新テスト'
        
        # 4. 検索履歴の削除（Delete）
        cursor.execute("DELETE FROM articles WHERE search_history_id = ?", (history_id,))
        cursor.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM search_history WHERE id = ?", (history_id,))
        deleted_history = cursor.fetchone()
        
        assert deleted_history is None
        
        cursor.execute("SELECT * FROM articles WHERE search_history_id = ?", (history_id,))
        deleted_articles = cursor.fetchall()
        
        assert len(deleted_articles) == 0
        
        conn.close()
    
    def test_database_constraints(self, test_db_file):
        """データベースの制約が正常に動作することを確認"""
        # 環境変数のモック
        os.environ['DATABASE_PATH'] = test_db_file
        
        # データベース初期化
        initialize_database()
        
        # データベース接続
        conn = sqlite3.connect(test_db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 検索履歴の作成
        cursor.execute(
            """
            INSERT INTO search_history (search_query, search_date, total_articles)
            VALUES (?, ?, ?)
            """,
            ('テスト', datetime.now().isoformat(), 1)
        )
        history_id = cursor.lastrowid
        
        # 記事の作成
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
                'テスト記事',
                'https://example.com/test',
                'zenn',
                datetime.now().isoformat(),
                'テスト記事の概要',
                datetime.now().isoformat()
            )
        )
        conn.commit()
        
        # URLの一意性制約のテスト
        with pytest.raises(sqlite3.IntegrityError):
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
                    'テスト記事（重複URL）',
                    'https://example.com/test',  # 重複URL
                    'qiita',
                    datetime.now().isoformat(),
                    'テスト記事の概要',
                    datetime.now().isoformat()
                )
            )
            conn.commit()
        
        # 外部キー制約のテスト
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO articles (
                    search_history_id, title, url, platform, 
                    published_date, summary, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    999,  # 存在しない検索履歴ID
                    'テスト記事',
                    'https://example.com/test2',
                    'zenn',
                    datetime.now().isoformat(),
                    'テスト記事の概要',
                    datetime.now().isoformat()
                )
            )
            conn.commit()
        
        conn.close()