"""
パフォーマンステスト
"""

import pytest
import time
import statistics
from unittest.mock import patch, MagicMock
from datetime import datetime

from models.article import Article


class TestPerformance:
    """アプリケーションのパフォーマンステスト"""
    
    @pytest.mark.performance
    @patch('services.search_service.SearchService.search_articles')
    def test_search_performance(self, mock_search, client):
        """
        検索機能のパフォーマンスをテスト
        """
        # モックの設定
        mock_articles = []
        for i in range(100):  # 100件の記事を生成
            mock_articles.append(
                Article(
                    title=f"パフォーマンステスト記事 {i}",
                    url=f"https://example.com/performance-test-{i}",
                    platform="zenn" if i % 3 == 0 else "qiita" if i % 3 == 1 else "hatena",
                    published_date=datetime.now(),
                    summary=f"パフォーマンステスト用の記事{i}の概要"
                )
            )
        mock_search.return_value = mock_articles
        
        # 複数回検索を実行して応答時間を測定
        response_times = []
        for i in range(10):  # 10回実行
            start_time = time.time()
            response = client.post('/search', data={'tool_name': f'パフォーマンステスト{i}'})
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # 応答時間の統計を計算
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n検索パフォーマンス統計:")
        print(f"平均応答時間: {avg_time:.4f}秒")
        print(f"最大応答時間: {max_time:.4f}秒")
        print(f"最小応答時間: {min_time:.4f}秒")
        
        # 応答時間が許容範囲内であることを確認
        assert avg_time < 1.0, f"平均応答時間が許容範囲を超えています: {avg_time:.4f}秒"
    
    @pytest.mark.performance
    @patch('services.storage_service.StorageService.get_search_history')
    def test_history_performance(self, mock_get_history, client):
        """
        検索履歴表示のパフォーマンスをテスト
        """
        # モックの設定 - 多数の履歴データを生成
        mock_history = []
        for i in range(50):  # 50件の履歴を生成
            mock_history.append({
                'id': i,
                'search_query': f'パフォーマンステスト{i}',
                'search_date': datetime.now(),
                'total_articles': 10,
                'platform_breakdown': {'zenn': 3, 'qiita': 4, 'hatena': 3},
                'recent_articles': [
                    {
                        'title': f'テスト記事{j}',
                        'url': f'https://example.com/test{i}-{j}',
                        'platform': 'zenn' if j % 3 == 0 else 'qiita' if j % 3 == 1 else 'hatena',
                        'published_date': datetime.now()
                    } for j in range(5)  # 各履歴に5件の記事
                ]
            })
        mock_get_history.return_value = mock_history
        
        # 応答時間を測定
        start_time = time.time()
        response = client.get('/history')
        end_time = time.time()
        
        assert response.status_code == 200
        
        response_time = end_time - start_time
        print(f"\n履歴表示パフォーマンス: {response_time:.4f}秒")
        
        # 応答時間が許容範囲内であることを確認
        assert response_time < 1.0, f"履歴表示の応答時間が許容範囲を超えています: {response_time:.4f}秒"
    
    @pytest.mark.performance
    def test_database_performance(self, test_db):
        """
        データベース操作のパフォーマンスをテスト
        """
        # 大量のデータを挿入して性能を測定
        start_time = time.time()
        
        # 検索履歴の挿入
        cursor = test_db.cursor()
        cursor.execute(
            "INSERT INTO search_history (search_query, search_date, total_articles) VALUES (?, ?, ?)",
            ("パフォーマンステスト", datetime.now().isoformat(), 100)
        )
        search_history_id = cursor.lastrowid
        
        # 記事データの一括挿入
        articles_data = []
        for i in range(100):  # 100件の記事を挿入
            articles_data.append((
                search_history_id,
                f"パフォーマンステスト記事 {i}",
                f"https://example.com/performance-test-{i}",
                "zenn" if i % 3 == 0 else "qiita" if i % 3 == 1 else "hatena",
                datetime.now().isoformat(),
                f"パフォーマンステスト用の記事{i}の概要"
            ))
        
        cursor.executemany(
            """
            INSERT INTO articles 
            (search_history_id, title, url, platform, published_date, summary) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            articles_data
        )
        
        test_db.commit()
        insert_time = time.time() - start_time
        
        # データ取得の性能を測定
        start_time = time.time()
        
        cursor.execute("""
            SELECT sh.id, sh.search_query, sh.search_date, sh.total_articles,
                   a.id as article_id, a.title, a.url, a.platform, a.published_date, a.summary
            FROM search_history sh
            JOIN articles a ON sh.id = a.search_history_id
            WHERE sh.id = ?
        """, (search_history_id,))
        
        results = cursor.fetchall()
        query_time = time.time() - start_time
        
        assert len(results) == 100
        
        print(f"\nデータベースパフォーマンス:")
        print(f"100件のデータ挿入時間: {insert_time:.4f}秒")
        print(f"100件のデータ取得時間: {query_time:.4f}秒")
        
        # 応答時間が許容範囲内であることを確認
        assert insert_time < 0.5, f"データ挿入時間が許容範囲を超えています: {insert_time:.4f}秒"
        assert query_time < 0.1, f"データ取得時間が許容範囲を超えています: {query_time:.4f}秒"