import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

import sys
from pathlib import Path

# Thêm thư mục gốc vào Python path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from modal_ai.cnn.detect_url import extract_full_47_features

CSV_PATH = "../modal_ai/PhiUSIIL_Phishing_URL_Dataset_Updated.csv"

def add_url_to_dataset(url, label):
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
    print("\nLuu y: Nhan Enter (de trong) de thoat chuong trinh")
    
    count_added = 0
    
    while True:
        # Nhập URL
        print("\n" + "-"*70)
        url = input("\nNhap URL (Enter de thoat): ").strip()
        
        # Nếu không nhập gì thì thoát
        if not url:
            print("\n" + "="*70)
            if count_added > 0:
                print(f"Da them thanh cong {count_added} URL vao dataset!")
                print("\nMuon train lai model?")
                print("Chay: cd modal_ai/cnn && python train_cnn.py")
            else:
                print("Khong them URL nao!")
            print("="*70)
            break
        
        # Nhập label
        print("\nChon loai:")
        print("  1 - SAFE (trang an toan)")
        print("  0 - PHISHING (trang lua dao)")
        choice = input("Nhap (0/1): ").strip()
        
        if choice not in ['0', '1']:
            print("Lua chon khong hop le! Bo qua URL nay.")
            continue
        
        label = int(choice)
        
        # Thêm vào dataset
        success = add_url_to_dataset(url, label)
        
        if success:
            count_added += 1

