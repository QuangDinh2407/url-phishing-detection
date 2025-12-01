# 📊 HƯỚNG DẪN XEM KẾT QUẢ TRAINING

Sau khi chạy `train_cnn.py`, bạn sẽ có **15 files** chứa đầy đủ thông tin về model.

---

## 📦 CÁC FILES ĐƯỢC TẠO

### 🎯 Model Files (4 files) - BẮT BUỘC cho inference
```
✅ cnn_hybrid_model.h5      - Trained model (weights + architecture)
✅ tokenizer.pkl            - Character tokenizer (URL → numbers)
✅ scaler.pkl               - Feature scaler (normalize numeric features)
✅ safe_features.pkl        - Selected features list
```

### 📈 Training History (2 files)
```
✅ training_history.json    - Loss/Accuracy mỗi epoch (dạng data)
✅ training_curves.png      - Biểu đồ Loss/Accuracy (dạng hình)
```

### 🔢 Confusion Matrix (3 files)
```
✅ confusion_matrix.npy     - Ma trận confusion (dạng NumPy array)
✅ confusion_matrix.txt     - Ma trận với giải thích (dạng text)
✅ confusion_matrix.png     - Heatmap confusion matrix (dạng hình)
```

### 📊 Classification Metrics (2 files)
```
✅ classification_report.json  - Precision/Recall/F1 (dạng JSON)
✅ classification_report.txt   - Classification report (dạng text)
```

### 📉 ROC & PR Curves (4 files)
```
✅ roc_curve_data.json           - ROC data + AUC score
✅ roc_curve.png                 - ROC curve visualization
✅ precision_recall_curve_data.json  - PR curve data
✅ precision_recall_curve.png        - PR curve visualization
```

### 📄 Summary Report (1 file)
```
✅ METRICS_SUMMARY.txt      - Tóm tắt TẤT CẢ metrics
```

---

## 🚀 CÁCH XEM KẾT QUẢ

### 1️⃣ Xem Nhanh: METRICS_SUMMARY.txt

```bash
# Windows
type METRICS_SUMMARY.txt

# Linux/Mac
cat METRICS_SUMMARY.txt
```

**Nội dung**:
- Accuracy, AUC
- Precision/Recall/F1 cho cả 2 classes
- Confusion matrix
- Training info (epochs, loss, accuracy)
- Danh sách files

### 2️⃣ Xem Training History

```python
import json

with open('training_history.json', 'r') as f:
    history = json.load(f)

print(f"Epochs trained: {history['epochs_trained']}")
print(f"\nFinal metrics:")
print(f"  Train Loss: {history['loss'][-1]:.4f}")
print(f"  Train Acc:  {history['accuracy'][-1]:.4f}")
print(f"  Val Loss:   {history['val_loss'][-1]:.4f}")
print(f"  Val Acc:    {history['val_accuracy'][-1]:.4f}")

print(f"\nBest epoch: {history['val_loss'].index(min(history['val_loss'])) + 1}")
print(f"Best val loss: {min(history['val_loss']):.4f}")
```

### 3️⃣ Xem Confusion Matrix

```python
import numpy as np

cm = np.load('confusion_matrix.npy')

print("Confusion Matrix:")
print(cm)
print(f"\nTP (Phishing detected): {cm[0,0]}")
print(f"FN (Phishing missed):   {cm[0,1]} ⚠️ DANGEROUS")
print(f"FP (False alarm):       {cm[1,0]}")
print(f"TN (Legit detected):    {cm[1,1]}")
```

Hoặc xem file text:
```bash
type confusion_matrix.txt
```

### 4️⃣ Xem Classification Report

```python
import json

with open('classification_report.json', 'r') as f:
    report = json.load(f)

print("Phishing (Class 0):")
print(f"  Precision: {report['0']['precision']:.4f}")
print(f"  Recall:    {report['0']['recall']:.4f}")
print(f"  F1-Score:  {report['0']['f1-score']:.4f}")

print("\nLegitimate (Class 1):")
print(f"  Precision: {report['1']['precision']:.4f}")
print(f"  Recall:    {report['1']['recall']:.4f}")
print(f"  F1-Score:  {report['1']['f1-score']:.4f}")

print(f"\nOverall Accuracy: {report['accuracy']:.4f}")
```

### 5️⃣ Xem ROC AUC

```python
import json

with open('roc_curve_data.json', 'r') as f:
    roc = json.load(f)

print(f"AUC Score: {roc['auc']:.4f}")
print(f"\nInterpretation:")
if roc['auc'] > 0.9:
    print("  Excellent model! 🎉")
elif roc['auc'] > 0.8:
    print("  Good model! 👍")
elif roc['auc'] > 0.7:
    print("  Fair model")
else:
    print("  Needs improvement")
```

### 6️⃣ Xem Hình Ảnh

Mở các file PNG trong thư mục:
- `confusion_matrix.png` - Ma trận confusion
- `roc_curve.png` - Đường cong ROC
- `precision_recall_curve.png` - Đường cong Precision-Recall
- `training_curves.png` - Loss và Accuracy qua các epochs

---

## 📊 SO SÁNH TRAIN VS TEST

```python
import json

with open('training_history.json', 'r') as f:
    history = json.load(f)

train_acc = history['accuracy'][-1]
val_acc = history['val_accuracy'][-1]
gap = train_acc - val_acc

print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy:  {val_acc:.4f}")
print(f"Gap:            {gap:.4f}")

if gap < 0.02:
    print("✅ No overfitting - Model generalizes well!")
elif gap < 0.05:
    print("⚠️ Slight overfitting - Acceptable")
else:
    print("❌ Overfitting detected - Consider regularization")
```

---

## 🔍 PHÂN TÍCH CHI TIẾT

### Kiểm Tra False Negatives (Nguy Hiểm!)

```python
import numpy as np

cm = np.load('confusion_matrix.npy')
fn = cm[0, 1]  # False Negatives
total_phishing = cm[0, 0] + cm[0, 1]

print(f"Total Phishing URLs: {total_phishing}")
print(f"Missed (FN):         {fn}")
print(f"Miss Rate:           {fn/total_phishing*100:.2f}%")

if fn/total_phishing < 0.05:
    print("✅ Excellent! Very few phishing URLs missed")
elif fn/total_phishing < 0.10:
    print("⚠️ Acceptable, but can improve")
else:
    print("❌ Too many phishing URLs missed - DANGEROUS!")
```

### So Sánh với Baseline

```python
import json

with open('classification_report.json', 'r') as f:
    report = json.load(f)

print("Model vs Random Classifier:")
print(f"Model Accuracy:  {report['accuracy']:.4f}")
print(f"Random Baseline: 0.5000")
print(f"Improvement:     {(report['accuracy'] - 0.5)*100:.2f}%")
```

---

## 📈 VẼ BIỂU ĐỒ CUSTOM

### Vẽ Confusion Matrix với Percentages

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

cm = np.load('confusion_matrix.npy')
cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

plt.figure(figsize=(8, 6))
sns.heatmap(cm_percent, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=['Phishing', 'Legitimate'],
            yticklabels=['Phishing', 'Legitimate'])
plt.title('Confusion Matrix (%)')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.savefig('confusion_matrix_percent.png', dpi=300)
plt.show()
```

### So Sánh Train vs Val Loss

```python
import json
import matplotlib.pyplot as plt

with open('training_history.json', 'r') as f:
    history = json.load(f)

plt.figure(figsize=(10, 6))
epochs = range(1, len(history['loss']) + 1)
plt.plot(epochs, history['loss'], 'b-', label='Training Loss', linewidth=2)
plt.plot(epochs, history['val_loss'], 'r-', label='Validation Loss', linewidth=2)

# Highlight best epoch
best_epoch = history['val_loss'].index(min(history['val_loss'])) + 1
plt.axvline(x=best_epoch, color='g', linestyle='--', label=f'Best Epoch ({best_epoch})')

plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training vs Validation Loss')
plt.legend()
plt.grid(alpha=0.3)
plt.savefig('loss_comparison.png', dpi=300)
plt.show()
```

---

## 💾 LOAD LẠI MODEL VÀ EVALUATE

```python
from tensorflow.keras.models import load_model
import pickle
import numpy as np

# Load model
model = load_model('cnn_hybrid_model.h5')

# Load preprocessors
with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('safe_features.pkl', 'rb') as f:
    safe_features = pickle.load(f)

print("✅ Model loaded successfully!")
print(f"Model inputs: {model.input_names}")
print(f"Model output: {model.output_names}")
```

---

## 🎯 CHECKLIST ĐÁNH GIÁ MODEL

```
✅ Accuracy > 90%
✅ AUC > 0.90
✅ Recall (Phishing) > 85%
✅ False Negatives < 10%
✅ Train-Test gap < 5%
✅ Confusion matrix balanced
✅ ROC curve well above diagonal
✅ All metrics files saved
```

---

## 🚨 DẤU HIỆU CẦN LƯU Ý

### ⚠️ Overfitting
```
Train Accuracy: 99%
Test Accuracy:  85%
→ Gap quá lớn (14%)
```

**Giải pháp**: Tăng Dropout, thêm regularization, hoặc thu thập thêm data.

### ⚠️ Underfitting
```
Train Accuracy: 70%
Test Accuracy:  68%
→ Cả 2 đều thấp
```

**Giải pháp**: Model phức tạp hơn, thêm features, train lâu hơn.

### ⚠️ High False Negatives
```
False Negatives: 100 (20% of phishing URLs)
→ Bỏ sót quá nhiều phishing!
```

**Giải pháp**: Điều chỉnh threshold (<0.5), tăng recall, hoặc sử dụng class weights.

---

## 📞 HỖ TRỢ

Nếu có vấn đề:
1. Kiểm tra `METRICS_SUMMARY.txt` trước
2. Xem confusion matrix để hiểu lỗi
3. So sánh train vs test để phát hiện overfitting
4. Review training curves để xem model có học tốt không

**Files quan trọng nhất để check**:
1. `METRICS_SUMMARY.txt` - Overview
2. `confusion_matrix.png` - Visual errors
3. `training_curves.png` - Training progress
4. `roc_curve.png` - Model discrimination ability

---

**Generated by**: train_cnn.py  
**Total Files**: 15 files  
**Quick Start**: Xem `METRICS_SUMMARY.txt` 📄




