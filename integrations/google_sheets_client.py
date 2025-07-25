"""
Google Sheets API クライアント
"""
import os
import json
import logging
from typing import List, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Google Sheets API クライアント"""
    
    def __init__(self, sheet_id: str, sheet_name: str = "Sheet1"):
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Google Sheets APIサービスを初期化"""
        try:
            credentials = self._get_credentials()
            if credentials:
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info("Google Sheets APIサービスを初期化しました")
            else:
                logger.warning("Google Sheets認証情報が見つかりません")
        except Exception as e:
            logger.error(f"Google Sheets APIサービスの初期化に失敗: {e}")
            self.service = None
    
    def _get_credentials(self) -> Optional[Credentials]:
        """認証情報を取得"""
        try:
            # 環境変数から認証情報を取得
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if credentials_json:
                credentials_info = json.loads(credentials_json)
                return Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            
            # ファイルから認証情報を取得
            credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
            if os.path.exists(credentials_file):
                return Credentials.from_service_account_file(
                    credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            
            return None
        except Exception as e:
            logger.error(f"認証情報の取得に失敗: {e}")
            return None
    
    def append_row(self, values: List[str]) -> bool:
        """スプレッドシートに行を追加"""
        if not self.service:
            logger.error("Google Sheets APIサービスが初期化されていません")
            return False
        
        try:
            range_name = f"{self.sheet_name}!A:F"
            body = {
                'values': [values]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"スプレッドシートに行を追加しました: {result.get('updates', {}).get('updatedRows', 0)}行")
            return True
            
        except HttpError as e:
            logger.error(f"Google Sheets APIエラー: {e}")
            return False
        except Exception as e:
            logger.error(f"スプレッドシートへの書き込みに失敗: {e}")
            return False
    
    def is_available(self) -> bool:
        """Google Sheets APIが利用可能かチェック"""
        return self.service is not None