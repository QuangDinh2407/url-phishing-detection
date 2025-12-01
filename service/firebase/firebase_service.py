import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Dict, Any, List
from datetime import datetime           



class FirebaseService:    
    _instance: Optional['FirebaseService'] = None
    _initialized: bool = False
    
    def __init__(self):
        self.db: Optional[firestore.client] = None
        
    @classmethod
    def get_instance(cls) -> 'FirebaseService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def connect(self, credentials_path: Optional[str] = None) -> 'FirebaseService':
        if self._initialized:
            print("Firebase đã được khởi tạo!")
            return self
            
        try:
            if credentials_path is None:
                credentials_path = os.path.join(
                    os.path.dirname(__file__), 
                    'firebase-credentials.json'
                )
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Không tìm thấy file credentials: {credentials_path}")
            
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self._initialized = True
            
            print(f"✓ Kết nối Firebase thành công!")
            return self
            
        except Exception as e:
            print(f"✗ Lỗi khi kết nối Firebase: {str(e)}")
            raise
    
    def check_url_exists(self, url: str, collection: str, field_name: str = 'url') -> bool:
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")

        try:
            docs = self.db.collection(collection).where(field_name, '==', url).limit(1).stream()
            for doc in docs:
                return True
            return False
            
        except Exception as e:
            print(f"Lỗi khi kiểm tra URL: {str(e)}")
            raise
    
    def add_url_to_blacklist(self, url: str) -> bool:
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")
        
        try:
            self.add_document(
                collection="url_black_list",
                data={
                    "URL": url,
                    "detected_at": datetime.now().isoformat(),
                    "source": "ai_detection"
                }
            )
            print(f"✓ Đã thêm URL vào blacklist: {url}")
            return True
            
        except Exception as e:
            print(f"✗ Lỗi khi thêm URL vào blacklist: {str(e)}")
            return False


def get_firebase_service() -> FirebaseService:
    service = FirebaseService.get_instance()
    if not service._initialized:
        service.connect()
    return service

