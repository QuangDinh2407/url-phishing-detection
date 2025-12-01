"""
Script để chuẩn bị external dataset
Extract features từ URLs nếu dataset chỉ có URL + label
"""

import sys
import pandas as pd
from tqdm import tqdm

# Import extract_full_47_features từ detect_url.py
sys.path.append('..')
try:
    from detect_url import extract_full_47_features
except:
    print("❌ Error: Cannot import extract_full_47_features from detect_url.py")
    print("💡 Make sure detect_url.py exists in parent directory")
    sys.exit(1)


def prepare_external_dataset(input_csv, output_csv):
    """
    Chuẩn bị external dataset bằng cách extract features từ URLs
    
    Parameters:
    -----------
    input_csv : str
        Path to input CSV (chỉ cần có URL và label)
    output_csv : str
        Path to output CSV (sẽ có đủ features)
    """
    
    print("="*70)
    print("PREPARING EXTERNAL DATASET FOR VALIDATION")
    print("="*70)
    
    # Load dataset
    print(f"\n📂 Loading: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"✅ Loaded {len(df)} rows")
    
    # Tìm cột URL và label
    url_cols = [c for c in df.columns if 'url' in c.lower()]
    label_cols = [c for c in df.columns if 'label' in c.lower()]
    
    if not url_cols:
        print("❌ Error: No URL column found!")
        print(f"   Available columns: {df.columns.tolist()}")
        return
    
    if not label_cols:
        print("❌ Error: No label column found!")
        print(f"   Available columns: {df.columns.tolist()}")
        return
    
    url_col = url_cols[0]
    label_col = label_cols[0]
    
    print(f"\n✅ URL column: {url_col}")
    print(f"✅ Label column: {label_col}")
    print(f"\n📊 Label distribution:")
    print(df[label_col].value_counts())
    
    # Extract features
    print(f"\n🔧 Extracting features from URLs...")
    print(f"   This may take a while...")
    
    features_list = []
    failed_urls = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        url = str(row[url_col])
        
        try:
            # Extract features
            features = extract_full_47_features(url)
            features['url'] = url
            features['label'] = row[label_col]
            features_list.append(features)
            
        except Exception as e:
            # Nếu lỗi, lưu lại
            failed_urls.append({
                'url': url,
                'error': str(e)
            })
    
    # Tạo DataFrame mới
    df_new = pd.DataFrame(features_list)
    
    print(f"\n✅ Successfully extracted features for {len(df_new)} URLs")
    
    if failed_urls:
        print(f"⚠️ Failed to extract {len(failed_urls)} URLs")
        print("\nSample failed URLs:")
        for item in failed_urls[:5]:
            print(f"  - {item['url'][:50]}... | Error: {item['error']}")
    
    # Save
    df_new.to_csv(output_csv, index=False)
    print(f"\n💾 Saved to: {output_csv}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Original rows:     {len(df)}")
    print(f"Processed rows:    {len(df_new)}")
    print(f"Failed rows:       {len(failed_urls)}")
    print(f"Total features:    {len(df_new.columns)}")
    print(f"\nFeatures extracted:")
    print(f"  {list(df_new.columns[:10])}...")
    
    print("\n✅ Dataset ready for external validation!")
    print(f"   Use this file in external_validation.py:")
    print(f"   EXTERNAL_CSV_PATH = '{output_csv}'")


def validate_dataset(csv_path, required_features_pkl='safe_features.pkl'):
    """
    Kiểm tra xem dataset có đủ features không
    
    Parameters:
    -----------
    csv_path : str
        Path to CSV
    required_features_pkl : str
        Path to safe_features.pkl
    """
    import pickle
    
    print("\n" + "="*70)
    print("VALIDATING DATASET")
    print("="*70)
    
    # Load required features
    with open(required_features_pkl, 'rb') as f:
        required_features = pickle.load(f)
    
    print(f"\n📋 Required features: {len(required_features)}")
    
    # Load dataset
    df = pd.read_csv(csv_path)
    print(f"📂 Dataset columns: {len(df.columns)}")
    
    # Check
    missing = [f for f in required_features if f not in df.columns]
    extra = [c for c in df.columns if c not in required_features and c not in ['url', 'label']]
    
    if missing:
        print(f"\n❌ Missing {len(missing)} features:")
        print(f"   {missing[:10]}...")
        print("\n💡 Run prepare_external_dataset() to extract these features")
        return False
    else:
        print(f"\n✅ All required features present!")
    
    if extra:
        print(f"\n⚠️ {len(extra)} extra columns (will be ignored):")
        print(f"   {extra[:10]}...")
    
    print("\n✅ Dataset is ready for external validation!")
    return True


if __name__ == "__main__":
    """
    Example usage:
    
    # Nếu dataset chỉ có URL và label:
    prepare_external_dataset(
        input_csv="raw_phishing_dataset.csv",
        output_csv="external_dataset_with_features.csv"
    )
    
    # Kiểm tra dataset:
    validate_dataset("external_dataset_with_features.csv")
    """
    
    print("="*70)
    print("EXTERNAL DATASET PREPARATION TOOL")
    print("="*70)
    print("\n💡 Usage:")
    print("\n1. If your dataset has only URL + label:")
    print("   prepare_external_dataset(")
    print("       input_csv='raw_dataset.csv',")
    print("       output_csv='dataset_with_features.csv'")
    print("   )")
    print("\n2. Validate dataset has all required features:")
    print("   validate_dataset('dataset_with_features.csv')")
    print("\n3. Then use in external_validation.py")
    print("\n" + "="*70)
    
    # Example (comment out if not needed)
    # Uncomment và modify paths này để chạy:
    
    # EXAMPLE_INPUT = "../raw_phishing_urls.csv"  # CSV với URL + label
    # EXAMPLE_OUTPUT = "../external_dataset_ready.csv"  # Output
    
    # prepare_external_dataset(EXAMPLE_INPUT, EXAMPLE_OUTPUT)
    # validate_dataset(EXAMPLE_OUTPUT)




