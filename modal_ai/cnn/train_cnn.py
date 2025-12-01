# A. TRAIN: từ dataset -> lưu model + tokenizer + scaler + safe_features
import os
import pickle
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, confusion_matrix, roc_curve, roc_auc_score, precision_recall_curve
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout, Concatenate
from tensorflow.keras.callbacks import EarlyStopping


# ---------- config ----------
CSV_PATH = "../PhiUSIIL_Phishing_URL_Dataset_Updated.csv"
MODEL_OUT = "cnn_hybrid_model.h5"
TOKENIZER_OUT = "tokenizer.pkl"
SCALER_OUT = "scaler.pkl"
SAFE_FEATURES_OUT = "safe_features.pkl"

MAX_LEN = 150
EMBED_DIM = 64
BATCH_SIZE = 64
EPOCHS = 10
RANDOM_STATE = 42

# ---------- load dataset ----------
df = pd.read_csv(CSV_PATH, low_memory=False)
print("Raw shape:", df.shape)

# tìm cột url + label
url_col = [c for c in df.columns if 'url' in c.lower()][0]
label_col = [c for c in df.columns if 'label' in c.lower()][0]
df = df.dropna(subset=[url_col, label_col]).copy()
df[label_col] = df[label_col].astype(int)

# ---------- chọn safe_features dựa trên corr ----------
corr = df.corr(numeric_only=True)[label_col].sort_values(ascending=False)
safe_features = [c for c in corr.index if c != label_col and abs(corr[c]) <= 0.7]
print("Chọn được", len(safe_features), "feature:", safe_features)

# lưu safe_features để dùng later (inference)
with open(SAFE_FEATURES_OUT, "wb") as f:
    pickle.dump(safe_features, f)
print("Saved safe_features ->", SAFE_FEATURES_OUT)

# ---------- DÙNG TRỰC TIẾP CÁC CỘT FEATURE TRONG CSV ----------
# KHÔNG gọi extract_full_47_features, KHÔNG crawl HTML khi train
missing = [c for c in safe_features if c not in df.columns]
if missing:
    raise ValueError(f"Thiếu cột trong CSV so với safe_features: {missing}")

X_num = df[safe_features].fillna(0).values  # (N, 47)

# ---------- chuẩn hóa numeric ----------
scaler = StandardScaler()
X_num_scaled = scaler.fit_transform(X_num)
with open(SCALER_OUT, "wb") as f:
    pickle.dump(scaler, f)
print("Saved scaler ->", SCALER_OUT)

# ---------- Tokenizer (char-level) cho URL ----------
urls = df[url_col].astype(str).tolist()
tokenizer = Tokenizer(char_level=True, oov_token=None)
tokenizer.fit_on_texts(urls)
with open(TOKENIZER_OUT, "wb") as f:
    pickle.dump(tokenizer, f)
print("Saved tokenizer ->", TOKENIZER_OUT)

# ---------- tạo X_url (chuỗi đã token hóa & pad) ----------
seq = tokenizer.texts_to_sequences(urls)
X_url = pad_sequences(seq, maxlen=MAX_LEN, padding='post', truncating='post')

y = df[label_col].values

# ---------- chia train/test ----------
X_url_train, X_url_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
    X_url, X_num_scaled, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

# ---------- build hybrid CNN ----------
num_features = X_num_train.shape[1]
url_input = Input(shape=(MAX_LEN,), name="url_input")
x1 = Embedding(len(tokenizer.word_index) + 1, EMBED_DIM)(url_input)
x1 = Conv1D(128, 5, activation='relu')(x1)
x1 = GlobalMaxPooling1D()(x1)
x1 = Dropout(0.4)(x1)

num_input = Input(shape=(num_features,), name="num_input")
x2 = Dense(64, activation='relu')(num_input)
x2 = Dropout(0.3)(x2)

merged = Concatenate()([x1, x2])
merged = Dense(64, activation='relu')(merged)
merged = Dropout(0.3)(merged)
output = Dense(1, activation='sigmoid')(merged)

model = Model(inputs=[url_input, num_input], outputs=output)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

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

# ---------- evaluate ----------
# Predict probabilities (needed for ROC curve)
y_pred_proba = model.predict([X_url_test, X_num_test], verbose=0).flatten()
y_pred = (y_pred_proba > 0.5).astype("int32")

print(classification_report(y_test, y_pred, digits=4))
print("F1-score:", f1_score(y_test, y_pred))

# ---------- save all metrics ----------
print("\n" + "="*60)
print("SAVING ALL METRICS AND VISUALIZATIONS")
print("="*60)

# 1. Save Training History
HISTORY_OUT = "training_history.json"
history_dict = {
    'loss': history.history['loss'],
    'accuracy': history.history['accuracy'],
    'val_loss': history.history['val_loss'],
    'val_accuracy': history.history['val_accuracy'],
    'epochs_trained': len(history.history['loss'])
}
with open(HISTORY_OUT, 'w') as f:
    json.dump(history_dict, f, indent=4)
print(f"✅ Saved: {HISTORY_OUT}")

# 2. Save Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
CM_NPY_OUT = "confusion_matrix.npy"
CM_TXT_OUT = "confusion_matrix.txt"
CM_PNG_OUT = "confusion_matrix.png"

np.save(CM_NPY_OUT, cm)

# Save as text with explanation
with open(CM_TXT_OUT, 'w', encoding='utf-8') as f:
    f.write("CONFUSION MATRIX\n")
    f.write("="*60 + "\n\n")
    f.write("Format:\n")
    f.write("                  Predicted\n")
    f.write("              Legit(1)  Phishing(0)\n")
    f.write("Actual Legit      TN        FP\n")
    f.write("       Phishing   FN        TP\n\n")
    f.write("Matrix:\n")
    f.write(str(cm) + "\n\n")
    f.write(f"True Positives (TP):  {cm[0,0]:>5} - Phishing correctly detected\n")
    f.write(f"False Negatives (FN): {cm[0,1]:>5} - Phishing missed (DANGEROUS!)\n")
    f.write(f"False Positives (FP): {cm[1,0]:>5} - Legit wrongly flagged\n")
    f.write(f"True Negatives (TN):  {cm[1,1]:>5} - Legit correctly identified\n")

# Plot confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Phishing(0)', 'Legitimate(1)'],
            yticklabels=['Phishing(0)', 'Legitimate(1)'])
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig(CM_PNG_OUT, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {CM_NPY_OUT}, {CM_TXT_OUT}, {CM_PNG_OUT}")

# 3. Save Classification Report
REPORT_JSON_OUT = "classification_report.json"
REPORT_TXT_OUT = "classification_report.txt"

report_dict = classification_report(y_test, y_pred, output_dict=True, digits=4)
with open(REPORT_JSON_OUT, 'w') as f:
    json.dump(report_dict, f, indent=4)

report_text = classification_report(y_test, y_pred, digits=4)
with open(REPORT_TXT_OUT, 'w', encoding='utf-8') as f:
    f.write("CLASSIFICATION REPORT\n")
    f.write("="*60 + "\n\n")
    f.write(report_text)

print(f"✅ Saved: {REPORT_JSON_OUT}, {REPORT_TXT_OUT}")

# 4. Save ROC Curve
ROC_DATA_OUT = "roc_curve_data.json"
ROC_PNG_OUT = "roc_curve.png"

fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = roc_auc_score(y_test, y_pred_proba)

roc_data = {
    'fpr': fpr.tolist(),
    'tpr': tpr.tolist(),
    'thresholds': thresholds.tolist(),
    'auc': float(roc_auc)
}
with open(ROC_DATA_OUT, 'w') as f:
    json.dump(roc_data, f, indent=4)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curve', fontsize=14, fontweight='bold')
plt.legend(loc="lower right")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(ROC_PNG_OUT, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {ROC_DATA_OUT}, {ROC_PNG_OUT} (AUC = {roc_auc:.4f})")

# 5. Save Precision-Recall Curve
PR_DATA_OUT = "precision_recall_curve_data.json"
PR_PNG_OUT = "precision_recall_curve.png"

precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)

pr_data = {
    'precision': precision_curve.tolist(),
    'recall': recall_curve.tolist(),
    'thresholds': pr_thresholds.tolist()
}
with open(PR_DATA_OUT, 'w') as f:
    json.dump(pr_data, f, indent=4)

plt.figure(figsize=(8, 6))
plt.plot(recall_curve, precision_curve, color='blue', lw=2)
plt.xlabel('Recall', fontsize=12)
plt.ylabel('Precision', fontsize=12)
plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(PR_PNG_OUT, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {PR_DATA_OUT}, {PR_PNG_OUT}")

# 6. Save Training Curves
CURVES_PNG_OUT = "training_curves.png"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
epochs_range = range(1, len(history.history['loss']) + 1)

# Loss plot
ax1.plot(epochs_range, history.history['loss'], 'b-', label='Training Loss', linewidth=2)
ax1.plot(epochs_range, history.history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
ax1.set_xlabel('Epoch', fontsize=12)
ax1.set_ylabel('Loss', fontsize=12)
ax1.set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Accuracy plot
ax2.plot(epochs_range, history.history['accuracy'], 'b-', label='Training Accuracy', linewidth=2)
ax2.plot(epochs_range, history.history['val_accuracy'], 'r-', label='Validation Accuracy', linewidth=2)
ax2.set_xlabel('Epoch', fontsize=12)
ax2.set_ylabel('Accuracy', fontsize=12)
ax2.set_title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(CURVES_PNG_OUT, dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Saved: {CURVES_PNG_OUT}")

# 7. Save Summary Report
SUMMARY_OUT = "METRICS_SUMMARY.txt"

with open(SUMMARY_OUT, 'w', encoding='utf-8') as f:
    f.write("="*70 + "\n")
    f.write(" "*20 + "MODEL EVALUATION SUMMARY\n")
    f.write("="*70 + "\n\n")
    
    f.write("📊 OVERALL PERFORMANCE\n")
    f.write("-"*70 + "\n")
    f.write(f"Accuracy:      {report_dict['accuracy']:.4f} ({report_dict['accuracy']*100:.2f}%)\n")
    f.write(f"AUC Score:     {roc_auc:.4f}\n\n")
    
    f.write("📈 PHISHING DETECTION (Class 0)\n")
    f.write("-"*70 + "\n")
    f.write(f"Precision:     {report_dict['0']['precision']:.4f} ({report_dict['0']['precision']*100:.2f}%)\n")
    f.write(f"Recall:        {report_dict['0']['recall']:.4f} ({report_dict['0']['recall']*100:.2f}%)\n")
    f.write(f"F1-Score:      {report_dict['0']['f1-score']:.4f}\n")
    f.write(f"Support:       {int(report_dict['0']['support'])} samples\n\n")
    
    f.write("✅ LEGITIMATE DETECTION (Class 1)\n")
    f.write("-"*70 + "\n")
    f.write(f"Precision:     {report_dict['1']['precision']:.4f} ({report_dict['1']['precision']*100:.2f}%)\n")
    f.write(f"Recall:        {report_dict['1']['recall']:.4f} ({report_dict['1']['recall']*100:.2f}%)\n")
    f.write(f"F1-Score:      {report_dict['1']['f1-score']:.4f}\n")
    f.write(f"Support:       {int(report_dict['1']['support'])} samples\n\n")
    
    f.write("🔢 CONFUSION MATRIX\n")
    f.write("-"*70 + "\n")
    f.write(f"True Positives:  {cm[0,0]:>4} - Phishing correctly detected\n")
    f.write(f"False Negatives: {cm[0,1]:>4} - Phishing missed (DANGEROUS!)\n")
    f.write(f"False Positives: {cm[1,0]:>4} - Legitimate wrongly flagged\n")
    f.write(f"True Negatives:  {cm[1,1]:>4} - Legitimate correctly identified\n\n")
    
    f.write("🎓 TRAINING INFORMATION\n")
    f.write("-"*70 + "\n")
    f.write(f"Epochs Trained:        {len(history.history['loss'])}\n")
    f.write(f"Final Train Loss:      {history.history['loss'][-1]:.4f}\n")
    f.write(f"Final Train Accuracy:  {history.history['accuracy'][-1]:.4f}\n")
    f.write(f"Final Val Loss:        {history.history['val_loss'][-1]:.4f}\n")
    f.write(f"Final Val Accuracy:    {history.history['val_accuracy'][-1]:.4f}\n")
    f.write(f"Best Val Loss:         {min(history.history['val_loss']):.4f} (Epoch {history.history['val_loss'].index(min(history.history['val_loss']))+1})\n\n")
    
    f.write("💾 OUTPUT FILES\n")
    f.write("-"*70 + "\n")
    f.write("✅ cnn_hybrid_model.h5 - Trained model\n")
    f.write("✅ tokenizer.pkl - Character tokenizer\n")
    f.write("✅ scaler.pkl - Feature scaler\n")
    f.write("✅ safe_features.pkl - Selected features list\n")
    f.write("✅ training_history.json - Training metrics by epoch\n")
    f.write("✅ confusion_matrix.npy/.txt/.png - Confusion matrix\n")
    f.write("✅ classification_report.json/.txt - Detailed metrics\n")
    f.write("✅ roc_curve_data.json/.png - ROC curve\n")
    f.write("✅ precision_recall_curve_data.json/.png - PR curve\n")
    f.write("✅ training_curves.png - Loss/Accuracy plots\n")
    f.write("✅ METRICS_SUMMARY.txt - This summary\n\n")
    
    f.write("="*70 + "\n")
    f.write("Training completed successfully!\n")
    f.write("="*70 + "\n")

print(f"✅ Saved: {SUMMARY_OUT}")

print("\n" + "="*60)
print("✅ ALL METRICS SAVED SUCCESSFULLY!")
print("="*60)
print(f"\n📄 Quick view: Check {SUMMARY_OUT} for overview")
print(f"📊 Total files created: 15 files")

# ---------- save model ----------
model.save(MODEL_OUT)
print("\nSaved model ->", MODEL_OUT)
