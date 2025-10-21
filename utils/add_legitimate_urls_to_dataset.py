"""
Script để extract features từ legitimate URLs và thêm vào dataset
"""
import os
import sys
import pandas as pd
import pickle
from pathlib import Path

# Thêm parent directory vào path để import detect_url
sys.path.insert(0, str(Path(__file__).parent.parent))

from modal_ai.cnn.detect_url import extract_full_47_features
from utils.collect_legitimate_urls import LEGITIMATE_COMPLEX_URLS

# Paths
CSV_PATH = "modal_ai/PhiUSIIL_Phishing_URL_Dataset_Updated.csv"
CSV_BACKUP = "modal_ai/PhiUSIIL_Phishing_URL_Dataset_Updated_BACKUP.csv"
SAFE_FEATURES_PKL = "modal_ai/cnn/safe_features.pkl"

def add_legitimate_urls_to_dataset():
    """
    Extract features từ legitimate URLs và thêm vào dataset
    """
    print("="*70)
    print("BẮT ĐẦU THÊM LEGITIMATE URLs VÀO DATASET")
    print("="*70)
    
    # 1. Backup dataset gốc
    print(f"\n1. Đang backup dataset gốc...")
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"   Dataset hiện tại: {len(df)} rows")
    print(f"   Label distribution: {df['label'].value_counts().to_dict()}")
    
    if not os.path.exists(CSV_BACKUP):
        df.to_csv(CSV_BACKUP, index=False)
        print(f"   ✓ Đã backup vào: {CSV_BACKUP}")
    else:
        print(f"   ✓ Backup đã tồn tại: {CSV_BACKUP}")
    
    # 2. Load safe_features
    print(f"\n2. Đang load safe_features...")
    with open(SAFE_FEATURES_PKL, "rb") as f:
        safe_features = pickle.load(f)
    print(f"   ✓ Loaded {len(safe_features)} features")
    
    # 3. Extract features từ legitimate URLs
    print(f"\n3. Đang extract features từ {len(LEGITIMATE_COMPLEX_URLS)} URLs...")
    new_rows = []
    
    for idx, url in enumerate(LEGITIMATE_COMPLEX_URLS, 1):
        print(f"\n   [{idx}/{len(LEGITIMATE_COMPLEX_URLS)}] Processing: {url[:80]}...")
        
        try:
            # Extract 47 features
            features = extract_full_47_features(url, timeout=10)
            
            # Tạo row mới
            new_row = {
                'FILENAME': f'legitimate_{idx}.txt',
                'URL': url,
                'label': 1  # 1 = legitimate/safe
            }
            
            # Thêm các features
            for feat in safe_features:
                new_row[feat] = features.get(feat, 0)
            
            # Thêm các cột khác từ dataset gốc (nếu có)
            for col in df.columns:
                if col not in new_row:
                    new_row[col] = 0  # default value
            
            new_rows.append(new_row)
            print(f"      ✓ Extracted {len(features)} features")
            
        except Exception as e:
            print(f"      ✗ Error: {str(e)}")
            continue
    
    # 4. Tạo DataFrame mới và concat
    print(f"\n4. Đang thêm {len(new_rows)} rows vào dataset...")
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        
        # Đảm bảo cùng columns order
        new_df = new_df[df.columns]
        
        # Concat
        updated_df = pd.concat([df, new_df], ignore_index=True)
        
        print(f"   Dataset cũ: {len(df)} rows")
        print(f"   Đã thêm: {len(new_df)} rows")
        print(f"   Dataset mới: {len(updated_df)} rows")
        print(f"\n   Label distribution sau khi thêm:")
        print(updated_df['label'].value_counts())
        
        # 5. Lưu dataset mới
        print(f"\n5. Đang lưu dataset mới...")
        updated_df.to_csv(CSV_PATH, index=False)
        print(f"   ✓ Đã lưu vào: {CSV_PATH}")
        
        print("\n" + "="*70)
        print("HOÀN THÀNH!")
        print("="*70)
        print(f"\nBây giờ bạn cần RETRAIN model bằng lệnh:")
        print(f"  cd modal_ai/cnn")
        print(f"  python train_cnn.py")
        print("="*70)
        
        return True
    else:
        print("\n   ✗ Không có row nào được thêm!")
        return False

if __name__ == "__main__":
    add_legitimate_urls_to_dataset()

