"""
検索フローのエンドツーエンドテスト
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestSearchFlowE2E:
    """検索フローのエンドツーエンドテスト"""
    
    @pytest.fixture(scope="class")
    def setup_webdriver(self):
        """Seleniumウェブドライバーのセットアップ"""
        options = Options()
        options.add_argument("--headless")  # ヘッドレスモード
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            pytest.skip(f"Chromeドライバーのセットアップに失敗しました: {e}")
            return None
        
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    @pytest.mark.e2e
    @patch('services.search_service.SearchService.search_articles')
    def test_complete_search_flow(self, mock_search, setup_webdriver, app):
        """
        検索から結果表示、履歴確認までの完全なフローをテスト
        """
        if setup_webdriver is None:
            pytest.skip("ウェブドライバーのセットアップに失敗しました")
        
        driver = setup_webdriver
        
        # モックの設定
        from models.article import Article
        from datetime import datetime
        
        mock_articles = [
            Article(
                title="E2Eテスト用記事1",
                url="https://example.com/e2e-test-1",
                platform="zenn",
                published_date=datetime.now(),
                summary="E2Eテスト用の記事1の概要"
            ),
            Article(
                title="E2Eテスト用記事2",
                url="https://example.com/e2e-test-2",
                platform="qiita",
                published_date=datetime.now(),
                summary="E2Eテスト用の記事2の概要"
            )
        ]
        mock_search.return_value = mock_articles
        
        # テスト用サーバーの起動
        with app.test_server() as server_url:
            # ホームページにアクセス
            driver.get(server_url)
            assert "ホーム - ツール活用事例検索サイト" in driver.title
            
            # 検索フォームに入力して送信
            search_input = driver.find_element(By.NAME, "tool_name")
            search_input.send_keys("E2Eテスト")
            
            search_form = driver.find_element(By.TAG_NAME, "form")
            search_form.submit()
            
            # 検索結果ページの表示を確認
            WebDriverWait(driver, 10).until(
                EC.title_contains("検索結果 - E2Eテスト")
            )
            
            # 検索結果の内容を確認
            assert "E2Eテスト用記事1" in driver.page_source
            assert "E2Eテスト用記事2" in driver.page_source
            assert "https://example.com/e2e-test-1" in driver.page_source
            assert "https://example.com/e2e-test-2" in driver.page_source
            
            # 履歴ページに移動
            history_link = driver.find_element(By.LINK_TEXT, "検索履歴")
            history_link.click()
            
            # 履歴ページの表示を確認
            WebDriverWait(driver, 10).until(
                EC.title_contains("検索履歴")
            )
            
            # 履歴に検索結果が表示されていることを確認
            assert "E2Eテスト" in driver.page_source
            
            # 履歴詳細ページに移動
            detail_link = driver.find_element(By.LINK_TEXT, "詳細")
            detail_link.click()
            
            # 詳細ページの表示を確認
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
            )
            
            # 詳細ページの内容を確認
            assert "E2Eテスト用記事1" in driver.page_source
            assert "E2Eテスト用記事2" in driver.page_source
    
    @pytest.mark.e2e
    def test_error_handling_flow(self, setup_webdriver, app):
        """
        エラーハンドリングのフローをテスト
        """
        if setup_webdriver is None:
            pytest.skip("ウェブドライバーのセットアップに失敗しました")
        
        driver = setup_webdriver
        
        # テスト用サーバーの起動
        with app.test_server() as server_url:
            # ホームページにアクセス
            driver.get(server_url)
            
            # 空の検索フォームを送信
            search_form = driver.find_element(By.TAG_NAME, "form")
            search_form.submit()
            
            # エラーメッセージの表示を確認
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-error"))
            )
            
            error_message = driver.find_element(By.CLASS_NAME, "alert-error")
            assert "ツール名を入力してください" in error_message.text
            
            # 存在しない履歴詳細ページにアクセス
            driver.get(f"{server_url}/history/99999")
            
            # リダイレクト後のエラーメッセージを確認
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert-error"))
            )
            
            error_message = driver.find_element(By.CLASS_NAME, "alert-error")
            assert "指定された検索結果が見つかりません" in error_message.text
            
            # 存在しないページにアクセス
            driver.get(f"{server_url}/non_existent_page")
            
            # 404ページの表示を確認
            assert "404" in driver.page_source
            assert "ページが見つかりません" in driver.page_source