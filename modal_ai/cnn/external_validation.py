"""
External Validation Script
Đánh giá model trên dataset khác để kiểm tra generalization
"""

import pickle
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns


def load_trained_model():
    """Load model và artifacts đã train"""
    print("Loading trained model and artifacts...")
    
    model = load_model("cnn_hybrid_model.h5")
    
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    
    with open("safe_features.pkl", "rb") as f:
        safe_features = pickle.load(f)
    
    print("✅ Model loaded successfully!")
    return model, tokenizer, scaler, safe_features


def prepare_external_dataset(external_csv_path, safe_features, tokenizer, scaler):
    """
    Chuẩn bị external dataset
    
    Parameters:
    -----------
    external_csv_path : str
        Path to external CSV file
    safe_features : list
        List of feature names
    tokenizer : Tokenizer
        Fitted tokenizer
    scaler : StandardScaler
        Fitted scaler
    
    Returns:
    --------
    X_url, X_num, y : arrays
    """
    print(f"\nLoading external dataset: {external_csv_path}")
    df = pd.read_csv(external_csv_path)
    print(f"Dataset size: {df.shape}")
    
    # Tìm cột URL và label
    url_col = [c for c in df.columns if 'url' in c.lower()][0]
    label_col = [c for c in df.columns if 'label' in c.lower()][0]
    
    print(f"URL column: {url_col}")
    print(f"Label column: {label_col}")
    
    # Kiểm tra features
    missing_features = [f for f in safe_features if f not in df.columns]
    
    if missing_features:
        print(f"\n⚠️ Warning: Missing {len(missing_features)} features!")
        print(f"Missing features: {missing_features[:10]}...")
        print("\n🔧 Solutions:")
        print("  1. Extract these features from URLs")
        print("  2. Use detect_url.py extract_full_47_features()")
        print("  3. Or provide dataset with same features")
        raise ValueError("Missing features - cannot proceed")
    
    # Process numeric features
    print("\n📊 Processing numeric features...")
    X_num = df[safe_features].fillna(0).values
    X_num_scaled = scaler.transform(X_num)
    print(f"✅ Numeric features shape: {X_num_scaled.shape}")
    
    # Process URLs
    print("\n🔤 Processing URLs...")
    urls = df[url_col].astype(str).tolist()
    seq = tokenizer.texts_to_sequences(urls)
    X_url = pad_sequences(seq, maxlen=150, padding='post', truncating='post')
    print(f"✅ URL features shape: {X_url.shape}")
    
    # Labels
    y = df[label_col].values
    print(f"✅ Labels shape: {y.shape}")
    print(f"   Phishing (0): {(y == 0).sum()}")
    print(f"   Legitimate (1): {(y == 1).sum()}")
    
    return X_url, X_num_scaled, y


def evaluate_external_dataset(model, X_url, X_num, y, save_prefix="external"):
    """Đánh giá model trên external dataset"""
    
    print("\n" + "="*70)
    print("EXTERNAL VALIDATION RESULTS")
    print("="*70)
    
    # Predict
    print("\nPredicting...")
    y_pred_proba = model.predict([X_url, X_num], verbose=0).flatten()
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    # Metrics
    accuracy = accuracy_score(y, y_pred)
    
    print("\n📊 Classification Report:")
    print(classification_report(y, y_pred, digits=4))
    
    # Confusion Matrix
    cm = confusion_matrix(y, y_pred)
    print("\n🔢 Confusion Matrix:")
    print(cm)
    print(f"\nTrue Positives (Phishing detected):  {cm[0,0]}")
    print(f"False Negatives (Phishing missed):   {cm[0,1]} ⚠️")
    print(f"False Positives (False alarms):      {cm[1,0]}")
    print(f"True Negatives (Legit detected):     {cm[1,1]}")
    
    # AUC
    try:
        auc = roc_auc_score(y, y_pred_proba)
        print(f"\n📈 AUC Score: {auc:.6f}")
    except:
        print("\n⚠️ Cannot compute AUC (only one class in y_true?)")
        auc = None
    
    # Save confusion matrix plot
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Phishing(0)', 'Legitimate(1)'],
                yticklabels=['Phishing(0)', 'Legitimate(1)'])
    plt.title('External Validation - Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(f'{save_prefix}_confusion_matrix.png', dpi=300)
    print(f"\n✅ Saved: {save_prefix}_confusion_matrix.png")
    plt.close()
    
    return accuracy, auc, cm


def compare_performance(internal_acc=0.9996, external_acc=None):
    """So sánh internal vs external performance"""
    
    if external_acc is None:
        return
    
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)
    
    print(f"\n📊 Internal Test (PhiUSIIL 20%):  {internal_acc:.4f} ({internal_acc*100:.2f}%)")
    print(f"📊 External Test:                  {external_acc:.4f} ({external_acc*100:.2f}%)")
    print(f"📉 Difference:                      {internal_acc - external_acc:.4f} ({(internal_acc - external_acc)*100:.2f}%)")
    
    gap = internal_acc - external_acc
    
    print("\n💡 Analysis:")
    if gap < 0.05:
        print("   ✅ EXCELLENT - Model generalizes very well!")
        print("   ✅ Performance drop < 5% is acceptable")
        print("   ✅ Ready for production")
    elif gap < 0.15:
        print("   ⚠️ GOOD - Model generalizes reasonably")
        print("   ⚠️ Performance drop 5-15% is acceptable")
        print("   💡 Consider fine-tuning on external data")
    else:
        print("   🔴 CONCERN - Significant performance drop")
        print("   🔴 Model may be overfitting to training dataset")
        print("   💡 Recommendations:")
        print("      1. Analyze distribution shift")
        print("      2. Retrain with mixed datasets")
        print("      3. Review feature engineering")
        print("      4. Add more regularization")


def main():
    """Main function"""
    
    print("="*70)
    print("EXTERNAL VALIDATION FOR PHISHING DETECTION MODEL")
    print("="*70)
    
    # Load model
    model, tokenizer, scaler, safe_features = load_trained_model()
    
    # ========== THAY ĐỔI PATH NÀY ==========
    EXTERNAL_CSV_PATH = "../external_phishing_dataset.csv"
    # ========================================
    
    print(f"\n⚠️ Please ensure your external CSV has:")
    print(f"   1. URL column (name contains 'url')")
    print(f"   2. Label column (name contains 'label', 0=phishing, 1=legitimate)")
    print(f"   3. Same {len(safe_features)} features as training:")
    print(f"      {safe_features[:5]}...")
    
    try:
        # Prepare external dataset
        X_url_ext, X_num_ext, y_ext = prepare_external_dataset(
            EXTERNAL_CSV_PATH, 
            safe_features, 
            tokenizer, 
            scaler
        )
        
        # Evaluate
        external_acc, external_auc, cm_ext = evaluate_external_dataset(
            model, 
            X_url_ext, 
            X_num_ext, 
            y_ext,
            save_prefix="external"
        )
        
        # Compare
        compare_performance(
            internal_acc=0.9996,  # From training
            external_acc=external_acc
        )
        
        print("\n" + "="*70)
        print("✅ EXTERNAL VALIDATION COMPLETED!")
        print("="*70)
        
    except FileNotFoundError:
        print(f"\n❌ Error: File not found: {EXTERNAL_CSV_PATH}")
        print("\n💡 To use this script:")
        print("   1. Prepare an external phishing dataset CSV")
        print("   2. Update EXTERNAL_CSV_PATH in the script")
        print("   3. Ensure it has URL, label, and feature columns")
        print("   4. Run this script again")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 You may need to:")
        print("   1. Extract features from URLs using detect_url.py")
        print("   2. Or use a dataset with compatible features")


if __name__ == "__main__":
    main()




