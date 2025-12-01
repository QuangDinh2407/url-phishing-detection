# 🎉 ĐÃ THÊM VÀO train_cnn.py

## ✅ THAY ĐỔI HOÀN TẤT

File `train_cnn.py` đã được cập nhật để **tự động lưu TẤT CẢ metrics** sau khi training!

---

## 📝 NHỮNG GÌ ĐÃ THÊM

### 1. Import Libraries (Dòng 3-13)
```python
import json                    # Lưu JSON
import matplotlib              # Vẽ biểu đồ
matplotlib.use('Agg')          # Non-interactive mode
import matplotlib.pyplot as plt
import seaborn as sns          # Heatmap đẹp
from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score, precision_recall_curve
```

### 2. Predict Probabilities (Dòng 116-118)
```python
# Thay vì chỉ predict 0/1
y_pred_proba = model.predict([X_url_test, X_num_test], verbose=0).flatten()
y_pred = (y_pred_proba > 0.5).astype("int32")
```
**Lý do**: Cần probabilities để vẽ ROC curve và PR curve.

### 3. Save All Metrics (Dòng 128-351)

Code tự động lưu **15 files**:

#### 📊 Training History
- `training_history.json` - Loss/Accuracy mỗi epoch

#### 🔢 Confusion Matrix  
- `confusion_matrix.npy` - NumPy array
- `confusion_matrix.txt` - Text với giải thích
- `confusion_matrix.png` - Heatmap visualization

#### 📈 Classification Metrics
- `classification_report.json` - JSON format
- `classification_report.txt` - Text format

#### 📉 ROC Curve
- `roc_curve_data.json` - FPR, TPR, thresholds, AUC
- `roc_curve.png` - Visualization

#### 📐 Precision-Recall Curve
- `precision_recall_curve_data.json` - Data
- `precision_recall_curve.png` - Visualization

#### 📊 Training Curves
- `training_curves.png` - Loss và Accuracy plots

#### 📄 Summary
- `METRICS_SUMMARY.txt` - Tóm tắt tất cả metrics

---

## 🚀 CÁCH SỬ DỤNG

### Bước 1: Chạy Training như bình thường
```bash
cd modal_ai/cnn
python train_cnn.py
```

### Bước 2: Đợi Training hoàn tất

Console sẽ hiển thị:
```
============================================================
SAVING ALL METRICS AND VISUALIZATIONS
============================================================
✅ Saved: training_history.json
✅ Saved: confusion_matrix.npy, confusion_matrix.txt, confusion_matrix.png
✅ Saved: classification_report.json, classification_report.txt
✅ Saved: roc_curve_data.json, roc_curve.png (AUC = 0.9xxx)
✅ Saved: precision_recall_curve_data.json, precision_recall_curve.png
✅ Saved: training_curves.png
✅ Saved: METRICS_SUMMARY.txt

============================================================
✅ ALL METRICS SAVED SUCCESSFULLY!
============================================================

📄 Quick view: Check METRICS_SUMMARY.txt for overview
📊 Total files created: 15 files
```

### Bước 3: Xem Kết Quả

**Cách nhanh nhất**:
```bash
type METRICS_SUMMARY.txt
```

**Hoặc mở các file PNG**:
- `confusion_matrix.png`
- `roc_curve.png`
- `training_curves.png`
- `precision_recall_curve.png`

---

## 📦 CÁC FILES SAU KHI TRAIN

```
modal_ai/cnn/
├── 🎯 Model Files (Bắt buộc cho inference)
│   ├── cnn_hybrid_model.h5
│   ├── tokenizer.pkl
│   ├── scaler.pkl
│   └── safe_features.pkl
│
├── 📊 Metrics Files (Để phân tích)
│   ├── training_history.json
│   ├── confusion_matrix.npy
│   ├── confusion_matrix.txt
│   ├── confusion_matrix.png
│   ├── classification_report.json
│   ├── classification_report.txt
│   ├── roc_curve_data.json
│   ├── roc_curve.png
│   ├── precision_recall_curve_data.json
│   ├── precision_recall_curve.png
│   ├── training_curves.png
│   └── METRICS_SUMMARY.txt
│
└── 📄 Documentation
    ├── train_cnn.py (Updated)
    ├── README_METRICS.md (How to view metrics)
    └── THAY_DOI_TRAIN_CNN.md (This file)
```

---

## 🔍 XEM LẠI KẾT QUẢ

### Quick View - METRICS_SUMMARY.txt
```bash
type METRICS_SUMMARY.txt
```

Bạn sẽ thấy:
- Accuracy, AUC
- Precision/Recall/F1 cho cả 2 classes
- Confusion Matrix chi tiết
- Training history
- Danh sách files

### Load trong Python
```python
import json
import numpy as np

# Load training history
with open('training_history.json', 'r') as f:
    history = json.load(f)
print("Train Acc:", history['accuracy'][-1])
print("Val Acc:", history['val_accuracy'][-1])

# Load confusion matrix
cm = np.load('confusion_matrix.npy')
print("Confusion Matrix:")
print(cm)

# Load ROC data
with open('roc_curve_data.json', 'r') as f:
    roc = json.load(f)
print("AUC:", roc['auc'])
```

---

## 📊 SO SÁNH TRƯỚC VÀ SAU

### ❌ TRƯỚC (Code cũ)
```
Chỉ có 4 files:
- cnn_hybrid_model.h5
- tokenizer.pkl
- scaler.pkl
- safe_features.pkl

❌ Không lưu training history
❌ Không lưu confusion matrix
❌ Không lưu ROC curve
❌ Phải train lại để xem metrics
```

### ✅ SAU (Code mới)
```
Có 15 files:
- 4 model files (như trước)
- 11 metrics files (MỚI!)

✅ Training history được lưu
✅ Confusion matrix (3 formats)
✅ ROC & PR curves
✅ Classification report
✅ Summary report
✅ Visualizations (PNG files)
```

---

## 🎯 LỢI ÍCH

### 1. Không Mất Thông Tin
- Training history được lưu vĩnh viễn
- Có thể xem lại bất cứ lúc nào
- Không cần train lại để xem metrics

### 2. Phân Tích Dễ Dàng
- Nhiều formats: JSON, TXT, PNG
- Visualizations sẵn có
- Summary report dễ đọc

### 3. So Sánh Models
- Lưu metrics của mỗi lần train
- So sánh AUC, accuracy, F1
- Chọn model tốt nhất

### 4. Debugging
- Xem confusion matrix để hiểu lỗi
- Training curves để phát hiện overfitting
- ROC curve để đánh giá discrimination

---

## ⚙️ TÙY CHỈNH

Nếu muốn thêm/bớt metrics, sửa trong train_cnn.py từ dòng 128-351.

### Ví dụ: Lưu thêm Per-Class Metrics
```python
# Thêm sau dòng 253
per_class_metrics = {
    'phishing': {
        'precision': report_dict['0']['precision'],
        'recall': report_dict['0']['recall'],
        'f1': report_dict['0']['f1-score']
    },
    'legitimate': {
        'precision': report_dict['1']['precision'],
        'recall': report_dict['1']['recall'],
        'f1': report_dict['1']['f1-score']
    }
}
with open('per_class_metrics.json', 'w') as f:
    json.dump(per_class_metrics, f, indent=4)
```

---

## 🆘 TROUBLESHOOTING

### Lỗi: ModuleNotFoundError: No module named 'seaborn'
```bash
pip install seaborn
```

### Lỗi: No display found (trên server)
→ Đã fix bằng `matplotlib.use('Agg')` (dòng 8)

### Lỗi: Permission denied khi save file
→ Đảm bảo có quyền write trong thư mục hiện tại

---

## 📚 TÀI LIỆU THAM KHẢO

- **README_METRICS.md** - Hướng dẫn chi tiết xem metrics
- **METRICS_SUMMARY.txt** - Summary sau mỗi lần train
- **train_cnn.py** - Source code đã update

---

## ✅ CHECKLIST

Sau khi train, kiểm tra:

- [ ] Console hiển thị "ALL METRICS SAVED SUCCESSFULLY"
- [ ] Có 15 files mới trong thư mục
- [ ] METRICS_SUMMARY.txt có nội dung đầy đủ
- [ ] Các file PNG mở được và hiển thị đúng
- [ ] training_history.json chứa loss/accuracy
- [ ] confusion_matrix.npy load được
- [ ] AUC score > 0.9 (nếu model tốt)

---

**Cập nhật**: 28/10/2025  
**Version**: 2.0  
**Changes**: Thêm tự động lưu 11 metrics files  
**Backward compatible**: ✅ Có - vẫn tạo 4 model files như cũ  
**Breaking changes**: ❌ Không - chỉ thêm features mới

🎉 **Hoàn tất! Giờ bạn có đầy đủ thông tin về model sau mỗi lần train!**




