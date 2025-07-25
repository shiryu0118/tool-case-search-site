"""
pytest用の共通フィクスチャ定義
"""

import os
import sys
import pytest
import tempfile
import sqlite3
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database.init_db import initialize_database
from models.article import Article
from models.search_result import SearchResult


@pytest.fixture
def app():
    """
    テスト用のFlaskアプリケーションを作成
    """
    app = create_app(testing=True)
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = ':memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    yield app


@pytest.fixture
def client(app):
    """
    テスト用のFlaskクライアントを作成
    """
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def test_db():
    """
    テスト用のインメモリSQLiteデータベースを作成
    """
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # スキーマの読み込みと実行
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    
    yield conn
    
    conn.close()


@pytest.fixture
def sample_articles():
    """
    テスト用のサンプル記事データを作成
    """
    return [
        Article(
            title="Dockerを使った開発環境の構築方法",
            url="https://zenn.dev/sample/articles/docker-dev-env",
            platform="zenn",
            published_date=datetime(2023, 1, 15),
            summary="Dockerを使った効率的な開発環境の構築方法について解説します。"
        ),
        Article(
            title="React Hooksの基本と応用",
            url="https://qiita.com/sample/items/react-hooks-basics",
            platform="qiita",
            published_date=datetime(2023, 2, 20),
            summary="React Hooksの基本的な使い方と実践的な応用例を紹介します。"
        ),
        Article(
            title="Pythonによるデータ分析入門",
            url="https://sample.hatenablog.com/entry/python-data-analysis",
            platform="hatena",
            published_date=datetime(2023, 3, 10),
            summary="Pythonを使ったデータ分析の基礎から応用までを解説します。"
        )
    ]


@pytest.fixture
def sample_search_result(sample_articles):
    """
    テスト用のサンプル検索結果データを作成
    """
    return SearchResult(
        id=None,
        search_query="Docker",
        articles=sample_articles,
        search_date=datetime.now(),
        total_count=len(sample_articles)
    )


@pytest.fixture
def mock_external_apis(monkeypatch):
    """
    外部APIをモック化
    """
    def mock_search(*args, **kwargs):
        return [
            Article(
                title="モックAPIからの記事",
                url="https://example.com/mock-article",
                platform="zenn",
                published_date=datetime.now(),
                summary="これはモックAPIからの記事です。"
            )
        ]
    
    # 各クライアントのsearch_articles関数をモック化
    from integrations.zenn_client import ZennClient
    from integrations.qiita_client import QiitaClient
    from integrations.hatena_client import HatenaClient
    
    monkeypatch.setattr(ZennClient, 'search_articles', mock_search)
    monkeypatch.setattr(QiitaClient, 'search_articles', mock_search)
    monkeypatch.setattr(HatenaClient, 'search_articles', mock_search)