"""
外部API統合のユニットテスト
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from integrations.google_sheets_client import GoogleSheetsClient


class TestGoogleSheetsClient:
    """GoogleSheetsClientのテスト"""
    
    @patch('integrations.google_sheets_client.build')
    @patch('integrations.google_sheets_client.Credentials')
    def test_initialize_service_with_credentials(self, mock_credentials, mock_build):
        """認証情報がある場合にサービスが正常に初期化されることを確認"""
        # モックの設定
        mock_credentials.from_service_account_info.return_value = "mock_credentials"
        mock_build.return_value = "mock_service"
        
        # 環境変数のモック
        with patch.dict('os.environ', {'GOOGLE_CREDENTIALS_JSON': '{"key": "value"}'}):
            client = GoogleSheetsClient(sheet_id="test_sheet_id")
            
            # 検証
            assert client.service == "mock_service"
            mock_credentials.from_service_account_info.assert_called_once()
            mock_build.assert_called_once_with('sheets', 'v4', credentials="mock_credentials")
    
    @patch('integrations.google_sheets_client.os.path.exists')
    @patch('integrations.google_sheets_client.Credentials')
    def test_initialize_service_with_credentials_file(self, mock_credentials, mock_exists):
        """認証情報ファイルがある場合にサービスが正常に初期化されることを確認"""
        # モックの設定
        mock_exists.return_value = True
        mock_credentials.from_service_account_file.return_value = "mock_credentials"
        
        with patch('integrations.google_sheets_client.build') as mock_build:
            mock_build.return_value = "mock_service"
            
            # 環境変数のモック（JSONなし、ファイルパスあり）
            with patch.dict('os.environ', {'GOOGLE_CREDENTIALS_FILE': 'test_credentials.json'}):
                client = GoogleSheetsClient(sheet_id="test_sheet_id")
                
                # 検証
                assert client.service == "mock_service"
                mock_credentials.from_service_account_file.assert_called_once()
                mock_build.assert_called_once_with('sheets', 'v4', credentials="mock_credentials")
    
    @patch('integrations.google_sheets_client.os.path.exists')
    def test_initialize_service_without_credentials(self, mock_exists):
        """認証情報がない場合にサービスが初期化されないことを確認"""
        # モックの設定
        mock_exists.return_value = False
        
        # 環境変数のモック（認証情報なし）
        with patch.dict('os.environ', {}, clear=True):
            client = GoogleSheetsClient(sheet_id="test_sheet_id")
            
            # 検証
            assert client.service is None
    
    @patch('integrations.google_sheets_client.build')
    @patch('integrations.google_sheets_client.Credentials')
    def test_append_row_success(self, mock_credentials, mock_build):
        """行の追加が成功することを確認"""
        # モックの設定
        mock_service = MagicMock()
        mock_sheets = MagicMock()
        mock_values = MagicMock()
        mock_append = MagicMock()
        
        mock_service.spreadsheets.return_value = mock_sheets
        mock_sheets.values.return_value = mock_values
        mock_values.append.return_value = mock_append
        mock_append.execute.return_value = {"updates": {"updatedRows": 1}}
        
        mock_build.return_value = mock_service
        mock_credentials.from_service_account_info.return_value = "mock_credentials"
        
        # 環境変数のモック
        with patch.dict('os.environ', {'GOOGLE_CREDENTIALS_JSON': '{"key": "value"}'}):
            client = GoogleSheetsClient(sheet_id="test_sheet_id")
            
            # サービスのモックを設定
            client.service = mock_service
            
            # 行の追加を実行
            result = client.append_row(["値1", "値2", "値3"])
            
            # 検証
            assert result is True
            mock_values.append.assert_called_once()
    
    def test_append_row_without_service(self):
        """サービスがない場合に行の追加が失敗することを確認"""
        client = GoogleSheetsClient(sheet_id="test_sheet_id")
        client.service = None
        
        result = client.append_row(["値1", "値2", "値3"])
        
        assert result is False
    
    @patch('integrations.google_sheets_client.build')
    @patch('integrations.google_sheets_client.Credentials')
    def test_append_row_with_api_error(self, mock_credentials, mock_build):
        """APIエラーが発生した場合に行の追加が失敗することを確認"""
        # モックの設定
        from googleapiclient.errors import HttpError
        
        mock_service = MagicMock()
        mock_sheets = MagicMock()
        mock_values = MagicMock()
        mock_append = MagicMock()
        
        mock_service.spreadsheets.return_value = mock_sheets
        mock_sheets.values.return_value = mock_values
        mock_values.append.return_value = mock_append
        mock_append.execute.side_effect = HttpError(resp=MagicMock(status=403), content=b'Access Denied')
        
        mock_build.return_value = mock_service
        mock_credentials.from_service_account_info.return_value = "mock_credentials"
        
        # 環境変数のモック
        with patch.dict('os.environ', {'GOOGLE_CREDENTIALS_JSON': '{"key": "value"}'}):
            client = GoogleSheetsClient(sheet_id="test_sheet_id")
            
            # サービスのモックを設定
            client.service = mock_service
            
            # 行の追加を実行
            result = client.append_row(["値1", "値2", "値3"])
            
            # 検証
            assert result is False
    
    def test_is_available(self):
        """サービスの可用性チェックが正常に動作することを確認"""
        # サービスがある場合
        client1 = GoogleSheetsClient(sheet_id="test_sheet_id")
        client1.service = "mock_service"
        assert client1.is_available() is True
        
        # サービスがない場合
        client2 = GoogleSheetsClient(sheet_id="test_sheet_id")
        client2.service = None
        assert client2.is_available() is False