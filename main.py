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

@app.post("/detect-url")
def detect_url(
    url: str = Query(..., description="URL cần kiểm tra"),
    firebase: FirebaseService = Depends(get_firebase_service)
):
    try:
        is_in_blacklist = firebase.check_url_exists(
            url=url,
            collection="url_black_list",
            field_name="URL"
        )
        
        if is_in_blacklist:
            print(f"URL tìm thấy trong blacklist!")
            return {
                "url": url,
                "result": "PHISHING",
                "confidence": 1.0,
                "message": "URL này đã được xác định là phishing"
            }
        
        result = predict_url(url, verbose=False)
        if result.get("result") == "PHISHING":
            firebase.add_url_to_blacklist(url)
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "url": url,
            "result": "ERROR"
        }