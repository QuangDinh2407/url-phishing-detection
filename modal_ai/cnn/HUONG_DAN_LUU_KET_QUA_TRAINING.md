# HƯỚNG DẪN LƯU VÀ XEM LẠI KẾT QUẢ TRAINING

## ❓ VẤN ĐỀ

**Câu hỏi**: Sau khi train và lưu model, có thể xem lại kết quả train vs test không?

**Trả lời**: 
- ❌ **Code hiện tại**: KHÔNG THỂ - chỉ lưu model (.h5), không lưu history
- ✅ **Sau khi sửa**: CÓ THỂ - nếu lưu thêm training history

---

## 📦 Model (.h5) Lưu Gì?

```python
model.save("cnn_hybrid_model.h5")
```

**Nội dung được lưu**:
- ✅ Architecture (các layers)
- ✅ Weights (tham số đã học)
- ✅ Optimizer state (Adam momentum, variance)
- ❌ **KHÔNG** lưu training history (loss, accuracy qua epochs)
- ❌ **KHÔNG** lưu classification report
- ❌ **KHÔNG** lưu confusion matrix

---

## 🔧 GIẢI PHÁP 1: Lưu History Object (Khuyến Nghị)

### Thêm Code Vào `train_cnn.py`

Thêm sau dòng 113 (sau khi fit xong):

```python
# ---------- train ----------
es = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = model.fit(
    [X_url_train, X_num_train], y_train,
    validation_data=([X_url_test, X_num_test], y_test),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[es],
    verbose=1
)

# ========== THÊM CODE NÀY ==========
# Lưu training history
import json

HISTORY_OUT = "training_history.json"

history_dict = {
    'loss': history.history['loss'],
    'accuracy': history.history['accuracy'],
    'val_loss': history.history['val_loss'],
    'val_accuracy': history.history['val_accuracy'],
    'epochs_trained': len(history.history['loss']),
    'best_epoch': len(history.history['loss']) - es.patience if es.stopped_epoch > 0 else len(history.history['loss'])
}

with open(HISTORY_OUT, 'w') as f:
    json.dump(history_dict, f, indent=4)
print(f"Saved training history -> {HISTORY_OUT}")
# ===================================
```

### Kết Quả: File `training_history.json`

```json
{
    "loss": [0.4523, 0.3245, 0.2876, 0.2634, 0.2456, 0.2298, 0.2187, 0.2089],
    "accuracy": [0.7834, 0.8567, 0.8792, 0.8934, 0.9023, 0.9087, 0.9134, 0.9178],
    "val_loss": [0.3502, 0.2987, 0.2754, 0.2623, 0.2589, 0.2612, 0.2645, 0.2698],
    "val_accuracy": [0.8456, 0.8723, 0.8856, 0.8945, 0.8978, 0.8967, 0.8934, 0.8912],
    "epochs_trained": 8,
    "best_epoch": 5
}
```

### Xem Lại Kết Quả:

```python
import json
import matplotlib.pyplot as plt

# Load history
with open('training_history.json', 'r') as f:
    history = json.load(f)

# In ra metrics
print(f"Epochs trained: {history['epochs_trained']}")
print(f"Best epoch: {history['best_epoch']}")
print(f"\nFinal metrics:")
print(f"  Train Loss: {history['loss'][-1]:.4f}")
print(f"  Train Acc:  {history['accuracy'][-1]:.4f}")
print(f"  Val Loss:   {history['val_loss'][-1]:.4f}")
print(f"  Val Acc:    {history['val_accuracy'][-1]:.4f}")

# Vẽ biểu đồ
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Loss
ax1.plot(history['loss'], label='Train Loss')
ax1.plot(history['val_loss'], label='Val Loss')
ax1.axvline(x=history['best_epoch']-1, color='r', linestyle='--', label='Best Epoch')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.set_title('Training vs Validation Loss')
ax1.legend()
ax1.grid(True)

# Accuracy
ax2.plot(history['accuracy'], label='Train Acc')
ax2.plot(history['val_accuracy'], label='Val Acc')
ax2.axvline(x=history['best_epoch']-1, color='r', linestyle='--', label='Best Epoch')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.set_title('Training vs Validation Accuracy')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('training_curves.png', dpi=300)
plt.show()
```

---

## 🔧 GIẢI PHÁP 2: Lưu Metrics Chi Tiết

### Thêm Code Lưu Classification Report

```python
# ---------- evaluate ----------
y_pred = (model.predict([X_url_test, X_num_test], verbose=0) > 0.5).astype("int32")
report = classification_report(y_test, y_pred, digits=4)
f1 = f1_score(y_test, y_pred)

print(report)
print("F1-score:", f1)

# ========== THÊM CODE NÀY ==========
# Lưu evaluation metrics
METRICS_OUT = "evaluation_metrics.txt"

with open(METRICS_OUT, 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("EVALUATION METRICS ON TEST SET\n")
    f.write("=" * 60 + "\n\n")
    f.write(report)
    f.write(f"\nOverall F1-score: {f1:.4f}\n")
    f.write("\n" + "=" * 60 + "\n")
    f.write("CONFUSION MATRIX\n")
    f.write("=" * 60 + "\n")
    
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, y_pred)
    f.write(f"\n{cm}\n\n")
    f.write(f"True Negatives (Legit predicted as Legit):   {cm[1,1]}\n")
    f.write(f"False Positives (Legit predicted as Phish):  {cm[1,0]}\n")
    f.write(f"False Negatives (Phish predicted as Legit):  {cm[0,1]}\n")
    f.write(f"True Positives (Phish predicted as Phish):   {cm[0,0]}\n")

print(f"Saved evaluation metrics -> {METRICS_OUT}")
# ===================================
```

### Kết Quả: File `evaluation_metrics.txt`

```
============================================================
EVALUATION METRICS ON TEST SET
============================================================

              precision    recall  f1-score   support

           0     0.9234    0.8876    0.9052       600
           1     0.9456    0.9623    0.9539      1400

    accuracy                         0.9387      2000
   macro avg     0.9345    0.9250    0.9296      2000
weighted avg     0.9381    0.9387    0.9383      2000

Overall F1-score: 0.9539

============================================================
CONFUSION MATRIX
============================================================

[[533  67]
 [ 53 1347]]

True Negatives (Legit predicted as Legit):   1347
False Positives (Legit predicted as Phish):  53
False Negatives (Phish predicted as Legit):  67
True Positives (Phish predicted as Phish):   533
```

---

## 🔧 GIẢI PHÁP 3: Evaluate Lại Sau Khi Load Model

Nếu đã train xong và chỉ có model (.h5), bạn vẫn có thể evaluate lại:

```python
import pickle
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.metrics import classification_report, f1_score

# Load model và artifacts
model = load_model("cnn_hybrid_model.h5")

# Load data (cần có dataset gốc)
df = pd.read_csv("../PhiUSIIL_Phishing_URL_Dataset_Updated.csv", low_memory=False)

# Giả sử bạn còn lưu train/test indices
# HOẶC chia lại dataset (với cùng RANDOM_STATE=42)
from sklearn.model_selection import train_test_split

url_col = [c for c in df.columns if 'url' in c.lower()][0]
label_col = [c for c in df.columns if 'label' in c.lower()][0]

# Preprocess lại (dùng cùng tokenizer, scaler đã lưu)
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("safe_features.pkl", "rb") as f:
    safe_features = pickle.load(f)

# Chia train/test (CÙNG random_state=42)
from tensorflow.keras.preprocessing.sequence import pad_sequences

urls = df[url_col].astype(str).tolist()
X_num = df[safe_features].fillna(0).values
y = df[label_col].values

seq = tokenizer.texts_to_sequences(urls)
X_url = pad_sequences(seq, maxlen=150, padding='post', truncating='post')
X_num_scaled = scaler.transform(X_num)

X_url_train, X_url_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
    X_url, X_num_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Evaluate trên TRAIN set
y_train_pred = (model.predict([X_url_train, X_num_train], verbose=0) > 0.5).astype("int32")
print("========== TRAIN SET ==========")
print(classification_report(y_train, y_train_pred, digits=4))

# Evaluate trên TEST set
y_test_pred = (model.predict([X_url_test, X_num_test], verbose=0) > 0.5).astype("int32")
print("\n========== TEST SET ==========")
print(classification_report(y_test, y_test_pred, digits=4))

# So sánh
print("\n========== COMPARISON ==========")
from sklearn.metrics import accuracy_score
print(f"Train Accuracy: {accuracy_score(y_train, y_train_pred):.4f}")
print(f"Test Accuracy:  {accuracy_score(y_test, y_test_pred):.4f}")
print(f"Overfitting Gap: {accuracy_score(y_train, y_train_pred) - accuracy_score(y_test, y_test_pred):.4f}")
```

**Lưu ý**: Phương pháp này cần:
- ✅ Dataset gốc vẫn còn
- ✅ Dùng CÙNG `random_state=42` khi split
- ✅ Tất cả artifacts (tokenizer, scaler, safe_features) vẫn còn

---

## 📊 GIẢI PHÁP 4: Lưu Train/Test Indices

Để chắc chắn evaluate đúng train/test set:

```python
# Sau khi train_test_split
X_url_train, X_url_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
    X_url, X_num_scaled, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

# ========== LƯU INDICES ==========
train_indices = X_url_train.index if hasattr(X_url_train, 'index') else np.arange(len(X_url_train))
test_indices = X_url_test.index if hasattr(X_url_test, 'index') else np.arange(len(X_url_train), len(X_url))

np.save("train_indices.npy", train_indices)
np.save("test_indices.npy", test_indices)
print("Saved train/test indices")
# =================================
```

Sau đó load lại:

```python
train_indices = np.load("train_indices.npy")
test_indices = np.load("test_indices.npy")

# Dùng indices này để lấy đúng train/test samples
```

---

## 📋 KHUYẾN NGHỊ

### Sửa Code `train_cnn.py` - Thêm Đầy Đủ:

```python
# ---------- config ----------
CSV_PATH = "../PhiUSIIL_Phishing_URL_Dataset_Updated.csv"
MODEL_OUT = "cnn_hybrid_model.h5"
TOKENIZER_OUT = "tokenizer.pkl"
SCALER_OUT = "scaler.pkl"
SAFE_FEATURES_OUT = "safe_features.pkl"

# ===== THÊM MỚI =====
HISTORY_OUT = "training_history.json"
METRICS_OUT = "evaluation_metrics.txt"
TRAIN_INDICES_OUT = "train_indices.npy"
TEST_INDICES_OUT = "test_indices.npy"
# ====================

# ... (code training như cũ) ...

# Sau khi fit xong:
history = model.fit(...)

# ===== LƯU HISTORY =====
import json
history_dict = {
    'loss': history.history['loss'],
    'accuracy': history.history['accuracy'],
    'val_loss': history.history['val_loss'],
    'val_accuracy': history.history['val_accuracy'],
    'epochs_trained': len(history.history['loss'])
}
with open(HISTORY_OUT, 'w') as f:
    json.dump(history_dict, f, indent=4)
print(f"Saved history -> {HISTORY_OUT}")
# ========================

# Sau khi evaluate:
y_pred = (model.predict([X_url_test, X_num_test], verbose=0) > 0.5).astype("int32")
report = classification_report(y_test, y_pred, digits=4)

# ===== LƯU METRICS =====
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

with open(METRICS_OUT, 'w') as f:
    f.write("EVALUATION METRICS\n")
    f.write("=" * 60 + "\n\n")
    f.write(report)
    f.write(f"\nF1-score: {f1:.4f}\n\n")
    f.write("Confusion Matrix:\n")
    f.write(str(cm))

print(f"Saved metrics -> {METRICS_OUT}")
# ========================
```

---

## 🎯 TÓM TẮT

| Muốn xem gì | Cần lưu | File | Có thể tái tạo? |
|-------------|---------|------|-----------------|
| **Training curves** | History object | `training_history.json` | ❌ Không (mất sau khi train) |
| **Test metrics** | Evaluation results | `evaluation_metrics.txt` | ✅ Có (nếu còn dataset + model) |
| **Train metrics** | Evaluate train set | `train_metrics.txt` | ✅ Có (nếu còn dataset + model) |
| **Train/Test indices** | Indices array | `*_indices.npy` | ✅ Có (nếu dùng cùng random_state) |

**Khuyến nghị**: Lưu history và metrics ngay sau khi train để có đầy đủ thông tin!




