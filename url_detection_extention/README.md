# URL Phishing Detector Extension

Extension Chrome để phát hiện URL lừa đảo với AI model thông minh.

## ✨ Tính năng mới (v1.1)

### 🔥 Kiểm tra tự động khi hover vào link
- **Background script chạy ngầm** - Không cần click extension!
- **Tooltip hiển thị ngay lập tức** - Rê chuột vào link là biết kết quả
- **Highlight links nguy hiểm** - Đánh dấu màu đỏ với cảnh báo ⚠️
- **Cache thông minh** - Giảm 80% số lần gọi API
- **Popup xác nhận** - Ngăn chặn click nhầm vào link lừa đảo

## Cài đặt Extension

### Cài đặt trên Chrome/Edge:

1. Mở Chrome hoặc Edge browser
2. Truy cập `chrome://extensions/` (hoặc `edge://extensions/` với Edge)
3. Bật chế độ "Developer mode" ở góc trên bên phải
4. Click "Load unpacked" (Tải tiện ích đã giải nén)
5. Chọn thư mục `url_detection_extention` 
6. Extension sẽ được cài đặt và hiển thị icon trên thanh công cụ

### Khởi động API Server (BẮT BUỘC):

```bash
cd d:\Document\DATN\train_ai
venv\Scripts\activate
uvicorn main:app --reload
```

Server sẽ chạy tại: `http://localhost:8000`

## Sử dụng

### Cách 1: Kiểm tra tự động (MỚI! ⭐)

1. Duyệt web bình thường
2. Rê chuột vào bất kỳ link nào
3. Đợi 0.5 giây → Tooltip hiển thị kết quả
4. Link được highlight theo màu:
   - 🟢 **Xanh lá**: An toàn
   - 🔴 **Đỏ**: Lừa đảo (có cảnh báo)
   - 🔵 **Xanh dương**: Đang kiểm tra

### Cách 2: Kiểm tra thủ công (Popup)

1. Click vào icon extension trên thanh công cụ
2. Nhập URL cần kiểm tra vào ô input
3. Click "Kiểm tra URL" hoặc nhấn Enter
4. Hoặc click "Kiểm tra URL hiện tại" để kiểm tra trang web đang mở

## Tính năng

### Kiểm tra tự động
- ✅ Rê chuột vào link → tự động kiểm tra
- ✅ Tooltip hiển thị kết quả ngay lập tức
- ✅ Highlight links theo mức độ nguy hiểm
- ✅ Cảnh báo khi click vào link lừa đảo
- ✅ Cache 30 phút - tránh gọi API lặp lại

### Kiểm tra thủ công
- ✅ Nhập URL thủ công để kiểm tra
- ✅ Kiểm tra URL của trang web hiện tại
- ✅ Giao diện đẹp và dễ sử dụng
- ✅ Hiển thị độ tin cậy theo %

### AI Model
- 🧠 CNN Hybrid Model (URL + 47 features)
- 🎯 Độ chính xác cao với legitimate URLs phức tạp
- 📊 Dataset được cải thiện với URLs từ Google, Facebook, Microsoft, v.v.

## Cấu trúc File

```
url_detection_extention/
├── manifest.json          # Config extension (v1.1)
├── background.js          # ⭐ Service worker (MỚI)
├── content.js             # ⭐ Detect hover & show tooltip (MỚI)
├── tooltip.css            # ⭐ Style cho tooltip (MỚI)
├── popup.html             # Giao diện popup
├── popup.js               # Logic popup
├── styles.css             # Style popup
├── icons/                 # Icons
├── README.md              # File này
└── HUONG_DAN_SU_DUNG.md  # Hướng dẫn chi tiết
```

## Xử lý sự cố

### Tooltip không hiển thị
- ✅ Kiểm tra API server đang chạy: `http://localhost:8000`
- ✅ Mở Console (F12) để xem lỗi
- ✅ Reload extension tại `chrome://extensions/`

### Link không được highlight
- ✅ Đợi đủ 0.5 giây trên link
- ✅ Kiểm tra link có protocol http/https
- ✅ Xem log trong Console

## Hướng dẫn chi tiết

Xem file **[HUONG_DAN_SU_DUNG.md](./HUONG_DAN_SU_DUNG.md)** để biết thêm:
- Cấu hình nâng cao
- Debug và troubleshooting
- Performance optimization
- Tính năng tương lai

## Changelog

### v1.1 (2025-10-21)
- ⭐ Thêm background service worker
- ⭐ Thêm content script cho hover detection
- ⭐ Tooltip hiển thị kết quả tự động
- ⭐ Cache kết quả kiểm tra
- ⭐ Highlight links theo màu
- ⭐ Popup cảnh báo khi click link nguy hiểm

### v1.0
- ✅ Popup kiểm tra URL thủ công
- ✅ Tích hợp AI model
- ✅ Giao diện đẹp

---

**Version**: 1.1  
**Tác giả**: DATN Team

