"""
Script để lưu TẤT CẢ metrics sau khi training
Thêm vào cuối train_cnn.py hoặc chạy riêng sau khi train
"""

import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, 
    classification_report,
    precision_recall_fscore_support,
    accuracy_score,
    roc_curve,
    roc_auc_score,
    precision_recall_curve
)

def save_all_metrics(y_test, y_pred, y_pred_proba, history=None, output_dir="./"):
    """
    Lưu tất cả metrics vào files
    
    Parameters:
    -----------
    y_test : array
        True labels của test set
    y_pred : array  
        Predicted labels (0 hoặc 1)
    y_pred_proba : array
        Predicted probabilities (0.0 - 1.0)
    history : dict, optional
        Training history từ model.fit()
    output_dir : str
        Thư mục lưu outputs
    """
    
    print("\n" + "="*60)
    print("SAVING ALL METRICS AND VISUALIZATIONS")
    print("="*60 + "\n")
    
    # ========== 1. CONFUSION MATRIX ==========
    print("1. Saving Confusion Matrix...")
    
    cm = confusion_matrix(y_test, y_pred)
    
    # Lưu dạng số
    np.save(f"{output_dir}/confusion_matrix.npy", cm)
    
    # Lưu dạng text với giải thích
    with open(f"{output_dir}/confusion_matrix.txt", 'w', encoding='utf-8') as f:
        f.write("CONFUSION MATRIX\n")
        f.write("="*60 + "\n\n")
        f.write("Format:\n")
        f.write("                  Predicted\n")
        f.write("              Legit(1)  Phishing(0)\n")
        f.write("Actual Legit      TN        FP\n")
        f.write("       Phishing   FN        TP\n\n")
        f.write("Matrix:\n")
        f.write(str(cm) + "\n\n")
        f.write(f"True Negatives (TN):  {cm[1,1]:>5} - Legit correctly identified\n")
        f.write(f"False Positives (FP): {cm[1,0]:>5} - Legit wrongly flagged as Phishing\n")
        f.write(f"False Negatives (FN): {cm[0,1]:>5} - Phishing missed (DANGEROUS!)\n")
        f.write(f"True Positives (TP):  {cm[0,0]:>5} - Phishing correctly detected\n\n")
        f.write(f"Total samples: {cm.sum()}\n")
        f.write(f"Correctly classified: {cm[0,0] + cm[1,1]} ({(cm[0,0] + cm[1,1])/cm.sum()*100:.2f}%)\n")
        f.write(f"Misclassified: {cm[0,1] + cm[1,0]} ({(cm[0,1] + cm[1,0])/cm.sum()*100:.2f}%)\n")
    
    # Vẽ heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Phishing(0)', 'Legitimate(1)'],
                yticklabels=['Phishing(0)', 'Legitimate(1)'])
    plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/confusion_matrix.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: confusion_matrix.npy")
    print("   ✅ Saved: confusion_matrix.txt")
    print("   ✅ Saved: confusion_matrix.png")
    
    # ========== 2. CLASSIFICATION REPORT ==========
    print("\n2. Saving Classification Report...")
    
    report_dict = classification_report(y_test, y_pred, output_dict=True, digits=4)
    report_text = classification_report(y_test, y_pred, digits=4)
    
    # Lưu dạng JSON
    with open(f"{output_dir}/classification_report.json", 'w') as f:
        json.dump(report_dict, f, indent=4)
    
    # Lưu dạng text có format đẹp
    with open(f"{output_dir}/classification_report.txt", 'w', encoding='utf-8') as f:
        f.write("CLASSIFICATION REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(report_text)
        f.write("\n" + "="*60 + "\n")
        f.write("INTERPRETATION:\n")
        f.write("="*60 + "\n\n")
        f.write("Class 0 (Phishing):\n")
        f.write(f"  Precision: {report_dict['0']['precision']:.4f} - When model says Phishing, it's correct {report_dict['0']['precision']*100:.2f}% of the time\n")
        f.write(f"  Recall:    {report_dict['0']['recall']:.4f} - Model detects {report_dict['0']['recall']*100:.2f}% of all Phishing URLs\n")
        f.write(f"  F1-Score:  {report_dict['0']['f1-score']:.4f} - Harmonic mean of Precision & Recall\n\n")
        
        f.write("Class 1 (Legitimate):\n")
        f.write(f"  Precision: {report_dict['1']['precision']:.4f} - When model says Legitimate, it's correct {report_dict['1']['precision']*100:.2f}% of the time\n")
        f.write(f"  Recall:    {report_dict['1']['recall']:.4f} - Model detects {report_dict['1']['recall']*100:.2f}% of all Legitimate URLs\n")
        f.write(f"  F1-Score:  {report_dict['1']['f1-score']:.4f} - Harmonic mean of Precision & Recall\n\n")
        
        f.write(f"Overall Accuracy: {report_dict['accuracy']:.4f} ({report_dict['accuracy']*100:.2f}%)\n")
    
    print("   ✅ Saved: classification_report.json")
    print("   ✅ Saved: classification_report.txt")
    
    # ========== 3. DETAILED METRICS ==========
    print("\n3. Saving Detailed Metrics...")
    
    precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    
    metrics_dict = {
        'accuracy': float(accuracy),
        'class_0_phishing': {
            'precision': float(precision[0]),
            'recall': float(recall[0]),
            'f1_score': float(f1[0]),
            'support': int(support[0])
        },
        'class_1_legitimate': {
            'precision': float(precision[1]),
            'recall': float(recall[1]),
            'f1_score': float(f1[1]),
            'support': int(support[1])
        },
        'confusion_matrix': {
            'TP': int(cm[0,0]),
            'FP': int(cm[1,0]),
            'FN': int(cm[0,1]),
            'TN': int(cm[1,1])
        },
        'total_samples': int(len(y_test)),
        'phishing_samples': int(support[0]),
        'legitimate_samples': int(support[1])
    }
    
    with open(f"{output_dir}/detailed_metrics.json", 'w') as f:
        json.dump(metrics_dict, f, indent=4)
    
    print("   ✅ Saved: detailed_metrics.json")
    
    # ========== 4. ROC CURVE ==========
    print("\n4. Saving ROC Curve...")
    
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    # Lưu data
    roc_data = {
        'fpr': fpr.tolist(),
        'tpr': tpr.tolist(),
        'thresholds': thresholds.tolist(),
        'auc': float(roc_auc)
    }
    
    with open(f"{output_dir}/roc_curve_data.json", 'w') as f:
        json.dump(roc_data, f, indent=4)
    
    # Vẽ ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/roc_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: roc_curve_data.json")
    print("   ✅ Saved: roc_curve.png")
    print(f"   📊 AUC Score: {roc_auc:.4f}")
    
    # ========== 5. PRECISION-RECALL CURVE ==========
    print("\n5. Saving Precision-Recall Curve...")
    
    precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)
    
    # Lưu data
    pr_data = {
        'precision': precision_curve.tolist(),
        'recall': recall_curve.tolist(),
        'thresholds': pr_thresholds.tolist()
    }
    
    with open(f"{output_dir}/precision_recall_curve_data.json", 'w') as f:
        json.dump(pr_data, f, indent=4)
    
    # Vẽ PR curve
    plt.figure(figsize=(8, 6))
    plt.plot(recall_curve, precision_curve, color='blue', lw=2)
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/precision_recall_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print("   ✅ Saved: precision_recall_curve_data.json")
    print("   ✅ Saved: precision_recall_curve.png")
    
    # ========== 6. TRAINING HISTORY ==========
    if history is not None:
        print("\n6. Saving Training History...")
        
        # Lưu history
        with open(f"{output_dir}/training_history.json", 'w') as f:
            json.dump(history, f, indent=4)
        
        # Vẽ training curves
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        epochs = range(1, len(history['loss']) + 1)
        
        # Loss plot
        ax1.plot(epochs, history['loss'], 'b-', label='Training Loss', linewidth=2)
        ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Accuracy plot
        ax2.plot(epochs, history['accuracy'], 'b-', label='Training Accuracy', linewidth=2)
        ax2.plot(epochs, history['val_accuracy'], 'r-', label='Validation Accuracy', linewidth=2)
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Accuracy', fontsize=12)
        ax2.set_title('Training and Validation Accuracy', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/training_curves.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("   ✅ Saved: training_history.json")
        print("   ✅ Saved: training_curves.png")
    else:
        print("\n6. Training History not available (skip)")
    
    # ========== 7. SUMMARY REPORT ==========
    print("\n7. Creating Summary Report...")
    
    with open(f"{output_dir}/SUMMARY_REPORT.txt", 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(" "*15 + "MODEL EVALUATION SUMMARY REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write("📊 OVERALL PERFORMANCE\n")
        f.write("-"*70 + "\n")
        f.write(f"Accuracy:      {accuracy:.4f} ({accuracy*100:.2f}%)\n")
        f.write(f"AUC Score:     {roc_auc:.4f}\n\n")
        
        f.write("📈 PHISHING DETECTION (Class 0)\n")
        f.write("-"*70 + "\n")
        f.write(f"Precision:     {precision[0]:.4f} - {precision[0]*100:.2f}% of Phishing predictions are correct\n")
        f.write(f"Recall:        {recall[0]:.4f} - Detected {recall[0]*100:.2f}% of all Phishing URLs\n")
        f.write(f"F1-Score:      {f1[0]:.4f}\n")
        f.write(f"Support:       {support[0]} samples\n\n")
        
        f.write("✅ LEGITIMATE DETECTION (Class 1)\n")
        f.write("-"*70 + "\n")
        f.write(f"Precision:     {precision[1]:.4f} - {precision[1]*100:.2f}% of Legitimate predictions are correct\n")
        f.write(f"Recall:        {recall[1]:.4f} - Detected {recall[1]*100:.2f}% of all Legitimate URLs\n")
        f.write(f"F1-Score:      {f1[1]:.4f}\n")
        f.write(f"Support:       {support[1]} samples\n\n")
        
        f.write("⚠️  ERROR ANALYSIS\n")
        f.write("-"*70 + "\n")
        f.write(f"False Positives: {cm[1,0]:>4} - Legitimate URLs wrongly flagged (annoying)\n")
        f.write(f"False Negatives: {cm[0,1]:>4} - Phishing URLs missed (DANGEROUS!)\n")
        f.write(f"Total Errors:    {cm[0,1] + cm[1,0]:>4} ({(cm[0,1] + cm[1,0])/cm.sum()*100:.2f}%)\n\n")
        
        if history is not None:
            f.write("🎓 TRAINING INFORMATION\n")
            f.write("-"*70 + "\n")
            f.write(f"Epochs Trained:        {len(history['loss'])}\n")
            f.write(f"Final Train Loss:      {history['loss'][-1]:.4f}\n")
            f.write(f"Final Train Accuracy:  {history['accuracy'][-1]:.4f}\n")
            f.write(f"Final Val Loss:        {history['val_loss'][-1]:.4f}\n")
            f.write(f"Final Val Accuracy:    {history['val_accuracy'][-1]:.4f}\n")
            f.write(f"Best Val Loss:         {min(history['val_loss']):.4f} (Epoch {history['val_loss'].index(min(history['val_loss']))+1})\n\n")
        
        f.write("💾 SAVED FILES\n")
        f.write("-"*70 + "\n")
        f.write("✅ confusion_matrix.npy / .txt / .png\n")
        f.write("✅ classification_report.json / .txt\n")
        f.write("✅ detailed_metrics.json\n")
        f.write("✅ roc_curve_data.json / .png\n")
        f.write("✅ precision_recall_curve_data.json / .png\n")
        if history is not None:
            f.write("✅ training_history.json\n")
            f.write("✅ training_curves.png\n")
        f.write("✅ SUMMARY_REPORT.txt\n\n")
        
        f.write("="*70 + "\n")
        f.write("Report generated successfully!\n")
        f.write("="*70 + "\n")
    
    print("   ✅ Saved: SUMMARY_REPORT.txt")
    
    print("\n" + "="*60)
    print("✅ ALL METRICS SAVED SUCCESSFULLY!")
    print("="*60)
    print(f"\nTotal files created: {11 if history is not None else 9}")
    print(f"Output directory: {output_dir}")
    print("\n📄 Quick view: Check SUMMARY_REPORT.txt for overview")


# ========== EXAMPLE USAGE ==========
if __name__ == "__main__":
    """
    Cách sử dụng:
    1. Thêm vào cuối train_cnn.py
    2. Hoặc chạy riêng sau khi train (cần load lại model và data)
    """
    
    # Ví dụ 1: Thêm vào train_cnn.py
    # (Sau dòng 116: y_pred = ...)
    
    """
    # Tính probability (cần cho ROC curve)
    y_pred_proba = model.predict([X_url_test, X_num_test], verbose=0).flatten()
    
    # Lưu tất cả metrics
    from save_all_metrics import save_all_metrics
    
    save_all_metrics(
        y_test=y_test,
        y_pred=y_pred,
        y_pred_proba=y_pred_proba,
        history=history.history if history else None,
        output_dir="./"
    )
    """
    
    # Ví dụ 2: Load lại model và evaluate
    """
    from tensorflow.keras.models import load_model
    import pickle
    
    # Load model
    model = load_model("cnn_hybrid_model.h5")
    
    # Load data và preprocess (như trong train_cnn.py)
    # ... (code load và preprocess)
    
    # Predict
    y_pred_proba = model.predict([X_url_test, X_num_test], verbose=0).flatten()
    y_pred = (y_pred_proba > 0.5).astype("int32")
    
    # Save metrics
    save_all_metrics(
        y_test=y_test,
        y_pred=y_pred,
        y_pred_proba=y_pred_proba,
        history=None,  # Không có history nếu load lại
        output_dir="./"
    )
    """
    
    print("See function docstring for usage examples")



