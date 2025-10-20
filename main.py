from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from service.firebase import FirebaseService, get_firebase_service
from modal_ai.cnn.detect_url import predict_url


app = FastAPI(title="Phishing URL Detection API")

# Thêm CORS middleware để cho phép extension gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins (có thể điều chỉnh để bảo mật hơn)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.post("/detect-url")
def detect_url(url: str = Query(..., description="URL cần kiểm tra")):
    print(f"URL: {url}")
    try:
        result = predict_url(url, verbose=False)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "url": url,
            "result": "ERROR"
        }