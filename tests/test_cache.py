"""
キャッシュ機能のテスト
"""

import pytest
import os
import time
from unittest.mock import patch, MagicMock
import requests_cache
from services.search_service import SearchService


class TestCaching:
    """キャッシュ機能のテスト"""
    
    @pytest.fixture
    def test_cache_file(self):
        """テスト用の一時キャッシュファイルを作成"""
        cache_path = "test_search_cache.sqlite"
        
        # テスト前にキャッシュファイルが存在する場合は削除
        if os.path.exists(cache_path):
            os.remove(cache_path)
        
        yield cache_path
        
        # テスト後にキャッシュファイルを削除
        if os.path.exists(cache_path):
            os.remove(cache_path)
    
    def test_cache_initialization(self):
        """キャッシュが正しく初期化されることを確認"""
        with patch('requests_cache.CachedSession') as mock_cached_session:
            mock_session = MagicMock()
            mock_cached_session.return_value = mock_session
            
            service = SearchService()
            
            mock_cached_session.assert_called_once_with(
                cache_name='search_cache',
                expire_after=3600,
                backend='sqlite'
            )
            assert service.session == mock_session
    
    def test_cache_usage(self, test_cache_file):
        """キャッシュが正しく使用されることを確認"""
        # 実際のキャッシュセッションを作成
        session = requests_cache.CachedSession(
            cache_name=test_cache_file.replace('.sqlite', ''),
            expire_after=3600,
            backend='sqlite'
        )
        
        # モックレスポンスを設定
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>テスト</body></html>"
            mock_get.return_value = mock_response
            
            # 最初のリクエスト（キャッシュなし）
            response1 = session.get('https://example.com/test')
            
            # 2回目のリクエスト（キャッシュあり）
            response2 = session.get('https://example.com/test')
            
            # 検証
            assert mock_get.call_count == 1  # 実際のリクエストは1回だけ
            assert response1.from_cache is False  # 1回目はキャッシュなし
            assert response2.from_cache is True   # 2回目はキャッシュあり
    
    def test_cache_expiration(self, test_cache_file):
        """キャッシュの有効期限が正しく動作することを確認"""
        # 短い有効期限でキャッシュセッションを作成
        session = requests_cache.CachedSession(
            cache_name=test_cache_file.replace('.sqlite', ''),
            expire_after=1,  # 1秒
            backend='sqlite'
        )
        
        # モックレスポンスを設定
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>テスト</body></html>"
            mock_get.return_value = mock_response
            
            # 最初のリクエスト
            response1 = session.get('https://example.com/test')
            
            # 2回目のリクエスト（キャッシュあり）
            response2 = session.get('https://example.com/test')
            
            # キャッシュの有効期限が切れるまで待機
            time.sleep(2)
            
            # 3回目のリクエスト（キャッシュ期限切れ）
            response3 = session.get('https://example.com/test')
            
            # 検証
            assert mock_get.call_count == 2  # 実際のリクエストは2回
            assert response1.from_cache is False  # 1回目はキャッシュなし
            assert response2.from_cache is True   # 2回目はキャッシュあり
            assert response3.from_cache is False  # 3回目はキャッシュ期限切れ
    
    def test_clear_cache(self):
        """キャッシュのクリア機能が正常に動作することを確認"""
        with patch('requests_cache.CachedSession') as mock_cached_session:
            mock_session = MagicMock()
            mock_cache = MagicMock()
            mock_session.cache = mock_cache
            mock_cached_session.return_value = mock_session
            
            service = SearchService()
            service.clear_cache()
            
            mock_cache.clear.assert_called_once()
    
    def test_get_cache_info(self):
        """キャッシュ情報の取得機能が正常に動作することを確認"""
        with patch('requests_cache.CachedSession') as mock_cached_session:
            mock_session = MagicMock()
            mock_cache = MagicMock()
            mock_cache.responses = {'key1': 'value1', 'key2': 'value2'}
            mock_cache.expire_after = 3600
            mock_session.cache = mock_cache
            mock_cached_session.return_value = mock_session
            
            service = SearchService()
            cache_info = service.get_cache_info()
            
            assert cache_info['cache_size'] == 2
            assert cache_info['expire_after'] == 3600