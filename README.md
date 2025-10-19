# 🛡️ Phishing URL Detection API

API phát hiện URL lừa đảo (phishing) sử dụng Deep Learning với mô hình CNN Hybrid và tích hợp Firebase Firestore.

## 📋 Mục lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng](#tính-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cài đặt](#cài-đặt)
- [Cấu hình Firebase](#cấu-hình-firebase)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [API Endpoints](#api-endpoints)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Huấn luyện mô hình](#huấn-luyện-mô-hình)
- [Phát hiện URL](#phát-hiện-url)

---

## 🎯 Giới thiệu

Dự án này là một hệ thống API sử dụng Deep Learning để phát hiện các URL lừa đảo (phishing). Hệ thống sử dụng mô hình CNN Hybrid kết hợp với Firebase Firestore để quản lý blacklist và lưu trữ kết quả phân tích.

### Mô hình AI

- **Kiến trúc**: CNN Hybrid (kết hợp text embedding và features engineering)
- **Dataset**: PhiUSIIL Phishing URL Dataset
- **Độ chính xác**: Tùy thuộc vào quá trình training
- **Features**: Phân tích URL structure, domain age, SSL certificate, HTML content, v.v.

---

## ✨ Tính năng

- ✅ **Phát hiện Phishing URL** sử dụng Deep Learning
- ✅ **API RESTful** với FastAPI
- ✅ **Firebase Firestore Integration** để quản lý blacklist
- ✅ **Dependency Injection** pattern cho service layer
- ✅ **Real-time URL analysis** với nhiều features
- ✅ **Blacklist Management** qua Firestore
- ✅ **Auto Swagger Documentation** tại `/docs`

---

## 🔧 Công nghệ sử dụng

### Backend & API
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Machine Learning
- **TensorFlow/Keras** - Deep Learning framework
- **scikit-learn** - Feature engineering & preprocessing
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation

### Database & Storage
- **Firebase Firestore** - NoSQL cloud database
- **firebase-admin** - Firebase Admin SDK

### Web Scraping & Analysis
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP library
- **urllib3** - URL manipulation

---

## 📦 Cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd train_ai
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
```

### 3. Kích hoạt môi trường ảo

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

**Các packages chính:**
```txt
fastapi
uvicorn
tensorflow
keras
scikit-learn
pandas
numpy
firebase-admin
beautifulsoup4
requests
h5py
```

---

## 🔥 Cấu hình Firebase

### 1. Tạo Firebase Project

1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Tạo project mới
3. Bật Firestore Database

### 2. Lấy Service Account Key

1. Vào **Project Settings** > **Service Accounts**
2. Click **Generate New Private Key**
3. Tải file JSON về

### 3. Đặt credentials vào dự án

Đặt file credentials vào thư mục:
```
service/firebase/firebase-credentials.json
```

### 4. Cấu trúc Firestore

Tạo collection trong Firestore:

**Collection: `url_black_list`**
```json
{
  "url": "https://example-phishing.com",
  "added_date": "2025-01-01",
  "reason": "Phishing detected",
  "status": "active"
}
```

---

## 🚀 Chạy ứng dụng

### Development Mode

```bash
cd train_ai
uvicorn main:app --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Với uv (nếu có)

```bash
uv run uvicorn main:app --reload
```

Server sẽ chạy tại: **http://127.0.0.1:8000**

---

## 📡 API Endpoints

### 1. Health Check

```http
GET /
```

**Response:**
```json
{
  "message": "Hello FastAPI!"
}
```

---

### 2. Test Firebase Connection

```http
GET /test-firebase
```

**Response:**
```json
{
  "message": "Firebase đã kết nối thành công!",
  "status": "connected"
}
```

---

### 3. Get Document from Firestore

```http
GET /document/{collection}/{doc_id}
```

**Parameters:**
- `collection` - Tên collection (string)
- `doc_id` - ID của document (string)

**Example:**
```bash
curl http://127.0.0.1:8000/document/url_black_list/abc123
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "status": "active"
  }
}
```

---

### 4. Get URL Blacklist

```http
GET /black-list
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "doc1",
      "url": "https://phishing-site.com",
      "added_date": "2025-01-01"
    },
    {
      "id": "doc2",
      "url": "https://fake-bank.com",
      "added_date": "2025-01-02"
    }
  ]
}
```

---

## 📁 Cấu trúc thư mục

```
train_ai/
│
├── main.py                          # FastAPI application entry point
│
├── service/                         # Service layer
│   └── firebase/
│       ├── __init__.py
│       ├── firebase_service.py      # Firebase service với DI
│       └── firebase-credentials.json
│
├── modal_ai/                        # AI Models
│   ├── cnn/
│   │   ├── train_cnn.py             # Script huấn luyện mô hình
│   │   ├── detect_url.py            # Script phát hiện phishing
│   │   ├── cnn_hybrid_model.h5      # Trained model
│   │   ├── tokenizer.pkl            # Text tokenizer
│   │   ├── scaler.pkl               # Feature scaler
│   │   └── safe_features.pkl        # Safe features baseline
│   │
│   └── PhiUSIIL_Phishing_URL_Dataset_Updated.csv
│
├── utils/                           # Utilities
│   ├── add_custom_url.py           # Thêm custom URL vào dataset
│   └── ALL-phishing-links.lst      # Phishing links list
│
├── venv/                            # Virtual environment
├── requirements.txt                 # Python dependencies
└── README.md                        # Documentation
```

---

## 🎓 Huấn luyện mô hình

### 1. Chuẩn bị dataset

Đảm bảo có file dataset:
```
modal_ai/PhiUSIIL_Phishing_URL_Dataset_Updated.csv
```

### 2. Chạy training script

```bash
cd modal_ai/cnn
python train_cnn.py
```

### 3. Kết quả

Sau khi train xong, các file sau sẽ được tạo:
- `cnn_hybrid_model.h5` - Trained model
- `tokenizer.pkl` - Tokenizer cho text
- `scaler.pkl` - Scaler cho features
- `safe_features.pkl` - Baseline features

### 4. Tùy chỉnh hyperparameters

Trong file `train_cnn.py`:
```python
MAX_LEN = 150        # Độ dài tối đa của sequence
EMBED_DIM = 64       # Embedding dimension
BATCH_SIZE = 64      # Batch size
EPOCHS = 10          # Số epochs
```

---

## 🔍 Phát hiện URL

### Sử dụng script trực tiếp

```bash
cd modal_ai/cnn
python detect_url.py
```

**Example code:**
```python
from detect_url import URLDetector

# Khởi tạo detector
detector = URLDetector()

# Phát hiện URL
url = "https://example-suspicious.com"
result = detector.predict(url)

print(f"URL: {url}")
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### Kết quả

```python
{
  "prediction": "PHISHING",  # hoặc "SAFE"
  "confidence": 0.95,        # 95%
  "features": {
    "url_length": 45,
    "domain_age": 10,
    "has_https": True,
    ...
  }
}
```

---

## 🔐 Bảo mật

⚠️ **Quan trọng:**

1. **KHÔNG** commit file `firebase-credentials.json` lên Git
2. Thêm vào `.gitignore`:
   ```
   service/firebase/firebase-credentials.json
   *.pkl
   *.h5
   venv/
   __pycache__/
   ```
3. Sử dụng environment variables cho production
4. Giới hạn API rate limiting nếu public

---

## 📊 Performance

### Metrics (ví dụ)

| Metric    | Score |
|-----------|-------|
| Accuracy  | 95%   |
| Precision | 94%   |
| Recall    | 96%   |
| F1-Score  | 95%   |

*Lưu ý: Kết quả thực tế phụ thuộc vào quá trình training*

---

## 📝 TODO / Future Improvements

- [ ] Thêm API endpoint để predict URL
- [ ] Tích hợp real-time detection
- [ ] Thêm authentication & authorization
- [ ] Caching với Redis
- [ ] Logging và monitoring
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API rate limiting
- [ ] Admin dashboard

---

## 🐛 Troubleshooting

### Lỗi Firebase Connection

```bash
Error: Could not import module "main"
```
**Giải pháp:** Đảm bảo chạy từ đúng thư mục

### Lỗi Model Loading

```bash
Error: Cannot load model
```
**Giải pháp:** Đảm bảo đã train model và các file .h5, .pkl tồn tại

### Lỗi Dependencies

```bash
ModuleNotFoundError
```
**Giải pháp:** Cài đặt lại dependencies
```bash
pip install -r requirements.txt
```

---

## 📚 Documentation

- **API Docs (Swagger):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **FastAPI:** https://fastapi.tiangolo.com/
- **Firebase:** https://firebase.google.com/docs

---


## 🙏 Acknowledgments

- PhiUSIIL Dataset
- FastAPI Team
- TensorFlow/Keras Team
- Firebase Team

---


