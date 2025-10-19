import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, Dict, Any, List


class FirebaseService:
    """Firebase Service với Dependency Injection"""
    
    _instance: Optional['FirebaseService'] = None
    _initialized: bool = False
    
    def __init__(self):
        """Initialize Firebase Service"""
        self.db: Optional[firestore.client] = None
        
    @classmethod
    def get_instance(cls) -> 'FirebaseService':
        """Singleton pattern để đảm bảo chỉ có 1 instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def connect(self, credentials_path: Optional[str] = None) -> 'FirebaseService':
        """
        Kết nối với Firebase
        
        Args:
            credentials_path: Đường dẫn đến file credentials JSON
            
        Returns:
            self để support method chaining
        """
        if self._initialized:
            print("Firebase đã được khởi tạo!")
            return self
            
        try:
            # Nếu không truyền path, sử dụng path mặc định
            if credentials_path is None:
                credentials_path = os.path.join(
                    os.path.dirname(__file__), 
                    'firebase-credentials.json'
                )
            
            # Kiểm tra file có tồn tại
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Không tìm thấy file credentials: {credentials_path}")
            
            # Khởi tạo Firebase
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            
            # Lấy Firestore client
            self.db = firestore.client()
            self._initialized = True
            
            print(f"✓ Kết nối Firebase thành công!")
            return self
            
        except Exception as e:
            print(f"✗ Lỗi khi kết nối Firebase: {str(e)}")
            raise
    
    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy một document từ Firestore
        
        Args:
            collection: Tên collection
            document_id: ID của document
            
        Returns:
            Dict chứa data của document hoặc None nếu không tìm thấy
        """
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"Không tìm thấy document: {collection}/{document_id}")
                return None
                
        except Exception as e:
            print(f"Lỗi khi lấy document: {str(e)}")
            raise
    
    def get_all_documents(self, collection: str) -> List[Dict[str, Any]]:
        """
        Lấy tất cả documents từ một collection
        
        Args:
            collection: Tên collection
            
        Returns:
            List các documents
        """
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")
        
        try:
            docs = self.db.collection(collection).stream()
            return [
                {**doc.to_dict(), 'id': doc.id} 
                for doc in docs
            ]
        except Exception as e:
            print(f"Lỗi khi lấy documents: {str(e)}")
            raise
    
    def add_document(self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> str:
        """
        Thêm document vào Firestore
        
        Args:
            collection: Tên collection
            data: Dữ liệu cần thêm
            document_id: ID của document (optional, nếu không có sẽ tự động tạo)
            
        Returns:
            ID của document vừa tạo
        """
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")
        
        try:
            if document_id:
                doc_ref = self.db.collection(collection).document(document_id)
                doc_ref.set(data)
                return document_id
            else:
                _, doc_ref = self.db.collection(collection).add(data)
                return doc_ref.id
        except Exception as e:
            print(f"Lỗi khi thêm document: {str(e)}")
            raise
    
    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """
        Cập nhật document trong Firestore
        
        Args:
            collection: Tên collection
            document_id: ID của document
            data: Dữ liệu cần cập nhật
            
        Returns:
            True nếu thành công
        """
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")
        
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật document: {str(e)}")
            raise
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """
        Xóa document từ Firestore
        
        Args:
            collection: Tên collection
            document_id: ID của document
            
        Returns:
            True nếu thành công
        """
        if not self._initialized:
            raise RuntimeError("Firebase chưa được khởi tạo! Gọi connect() trước.")
        
        try:
            self.db.collection(collection).document(document_id).delete()
            return True
        except Exception as e:
            print(f"Lỗi khi xóa document: {str(e)}")
            raise


# Dependency injection function cho FastAPI
def get_firebase_service() -> FirebaseService:
    """
    Dependency injection function cho FastAPI
    
    Returns:
        FirebaseService instance đã được kết nối
    """
    service = FirebaseService.get_instance()
    if not service._initialized:
        service.connect()
    return service

