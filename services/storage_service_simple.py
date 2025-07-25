"""
Simple storage service for testing
"""

class StorageService:
    def __init__(self):
        pass
    
    def save_search_result(self, search_result):
        return True
    
    def get_search_history(self):
        return []
    
    def get_search_result_by_id(self, search_id):
        return None