from fastapi import FastAPI, Depends
from service.firebase import FirebaseService, get_firebase_service

app = FastAPI(title="Phishing URL Detection API")


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}


@app.get("/test-firebase")
def test_firebase(firebase: FirebaseService = Depends(get_firebase_service)):
    """
    Test endpoint để kiểm tra kết nối Firebase
    
    Ví dụ: GET /test-firebase?collection=users&doc_id=test123
    """
    return {
        "message": "Firebase đã kết nối thành công!",
        "status": "connected"
    }


@app.get("/document/{collection}/{doc_id}")
def get_document(
    collection: str, 
    doc_id: str,
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """
    Lấy một document từ Firestore
    
    Args:
        collection: Tên collection
        doc_id: ID của document
    
    Returns:
        Document data hoặc lỗi
    """
    try:
        document = firebase.get_document(collection, doc_id)
        
        if document:
            return {
                "success": True,
                "data": document
            }
        else:
            return {
                "success": False,
                "message": f"Không tìm thấy document {doc_id} trong collection {collection}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/black-list")
def get_all_documents(
    firebase: FirebaseService = Depends(get_firebase_service)
):
    """
    Lấy tất cả documents từ một collection
    
    Args:
        collection: Tên collection
    
    Returns:
        List documents hoặc lỗi
    """
    try:
        documents = firebase.get_all_documents('url_black_list')
        return {
            "success": True,
            "data": documents
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
