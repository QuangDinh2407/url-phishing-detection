# A. TRAIN: từ dataset -> lưu model + tokenizer + scaler + safe_features
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
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
y_pred = (model.predict([X_url_test, X_num_test], verbose=0) > 0.5).astype("int32")
print(classification_report(y_test, y_pred, digits=4))
print("F1-score:", f1_score(y_test, y_pred))

# ---------- save model ----------
model.save(MODEL_OUT)
print("Saved model ->", MODEL_OUT)
