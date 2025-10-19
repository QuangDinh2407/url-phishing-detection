"""
Script thêm URL tùy chỉnh vào dataset
Cách dùng: python add_custom_url.py
"""

import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import pandas as pd
from detect_url import extract_full_47_features

CSV_PATH = "PhiUSIIL_Phishing_URL_Dataset.csv"

def add_url_to_dataset(url, label):
    """
    Thêm 1 URL vào dataset
    Args:
        url: URL cần thêm
        label: 0=phishing, 1=safe
    """
    print(f"\nDang xu ly: {url}")
    print(f"Label: {'SAFE' if label==1 else 'PHISHING'}")
    
    # Đọc dataset
    df = pd.read_csv(CSV_PATH, low_memory=False)
    columns = df.columns.tolist()
    
    # Kiểm tra đã tồn tại chưa
    if url in df['URL'].values:
        print("-> URL da ton tai trong dataset!")
        return False
    
    # Trích xuất features
    print("-> Dang truy cap va trich xuat features...")
    try:
        features = extract_full_47_features(url, timeout=10)
        
        # Tạo row mới
        row = {}
        row['FILENAME'] = f"custom_{len(df)}.txt"
        row['URL'] = url
        
        for col in columns:
            if col in ['FILENAME', 'URL', 'label']:
                continue
            row[col] = features.get(col, 0)
        
        row['label'] = label
        
        # Thêm vào DataFrame
        df_new = pd.DataFrame([row], columns=columns)
        df_combined = pd.concat([df, df_new], ignore_index=True)
        
        # Lưu
        df_combined.to_csv(CSV_PATH, index=False)
        print(f"-> DA THEM THANH CONG!")
        print(f"   Tong URL trong dataset: {len(df_combined):,}")
        return True
        
    except Exception as e:
        print(f"-> LOI: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("THEM URL TUY CHINH VAO DATASET")
    print("="*70)
    
    # Nhập URL
    url = input("\nNhap URL: ").strip()
    if not url:
        print("URL khong hop le!")
        exit()
    
    # Nhập label
    print("\nChon loai:")
    print("  1 - SAFE (trang an toan)")
    print("  0 - PHISHING (trang lua dao)")
    choice = input("Nhap (0/1): ").strip()
    
    if choice not in ['0', '1']:
        print("Lua chon khong hop le!")
        exit()
    
    label = int(choice)
    
    # Thêm vào dataset
    success = add_url_to_dataset(url, label)
    
    if success:
        print("\n" + "="*70)
        print("THANH CONG! Muon train lai model?")
        print("Chay: python train_cnn.py")
        print("="*70)

