import os
import warnings

# Tắt TensorFlow warnings (PHẢI set TRƯỚC khi import tensorflow)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 3 = tắt tất cả warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Tắt scikit-learn và các warnings khác
warnings.filterwarnings('ignore')

import re, math, socket, requests
# Tắt SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from urllib.parse import urlparse
from collections import Counter
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ---------- config ----------
MODEL_PATH = "cnn_hybrid_model.h5"
TOKENIZER_PKL = "tokenizer.pkl"
SCALER_PKL = "scaler.pkl"
SAFE_FEATURES_PKL = "safe_features.pkl"

MAX_LEN = 150
THRESHOLD = 0.3  # Giảm xuống để nhạy hơn với phishing

# ---------- load artifacts ----------
model = load_model(MODEL_PATH)
with open(TOKENIZER_PKL, "rb") as f:
    tokenizer = pickle.load(f)
with open(SCALER_PKL, "rb") as f:
    scaler = pickle.load(f)
with open(SAFE_FEATURES_PKL, "rb") as f:
    SAFE_FEATURES = pickle.load(f)

# ---------- helper ----------
def _safe_get(url, timeout=5):
    try:
        # print(f"Dang truy cap: {url}")  # Tat de khong spam khi test batch
        resp = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, allow_redirects=True)
        print(f"Status: {resp.status_code} | URL: {resp.url}")
        return resp.status_code, resp.text
    except Exception as e:
        # print(f"Loi khi truy cap URL: {str(e)}")
        return None, None

def _similarity(a, b):
    if not a or not b: return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def _is_ip(host):
    try:
        socket.inet_aton(host)
        return True
    except:
        return False

def _char_entropy(s):
    if not s: return 0.0
    c = Counter(s)
    total = len(s)
    ent = -sum((v/total) * math.log2(v/total) for v in c.values())
    return ent

# ---------- trích 47 đặc trưng ----------
def extract_full_47_features(url, timeout=5):
    """Tạo ra dict 47 features tương ứng SAFE_FEATURES"""
    features = {}
    parsed = urlparse(url if '://' in url else 'http://' + url)
    host = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query
    full = url

    # --- URL cơ bản ---
    features['URLLength'] = len(full)
    features['NoOfAmpersandInURL'] = full.count('&')
    features['NoOfEqualsInURL'] = full.count('=')
    features['NoOfQMarkInURL'] = full.count('?')
    features['NoOfDegitsInURL'] = sum(ch.isdigit() for ch in full)
    features['NoOfLettersInURL'] = sum(ch.isalpha() for ch in full)
    features['NoOfOtherSpecialCharsInURL'] = sum(1 for ch in full if not (ch.isalnum() or ch in '/:._-?=&%+#~'))
    features['IsDomainIP'] = int(_is_ip(host))
    features['TLDLength'] = len(host.split('.')[-1]) if '.' in host else 0
    features['DomainLength'] = len(host)
    features['NoOfSubDomain'] = host.count('.') - 1 if host.count('.') > 1 else 0

    # --- tỷ lệ ký tự ---
    features['LetterRatioInURL'] = features['NoOfLettersInURL'] / (features['URLLength']+1e-6)
    features['DegitRatioInURL'] = features['NoOfDegitsInURL'] / (features['URLLength']+1e-6)
    features['SpacialCharRatioInURL'] = features['NoOfOtherSpecialCharsInURL'] / (features['URLLength']+1e-6)

    # --- https ---
    features['IsHTTPS'] = int(parsed.scheme == 'https')

    # --- khởi tạo mặc định ---
    for c in SAFE_FEATURES:
        if c not in features:
            features[c] = 0

    # --- lấy HTML ---
    status, html = _safe_get(url, timeout=timeout)
    if not html:
        return {c: features.get(c, 0) for c in SAFE_FEATURES}

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    text = soup.get_text(separator=' ') if soup else ""
    features['HasTitle'] = int(bool(title))
    features['HasDescription'] = int(bool(soup.find('meta', attrs={'name':'description'})))
    features['HasFavicon'] = int(bool(soup.find('link', rel=lambda r: r and 'icon' in r.lower())))
    features['IsResponsive'] = int(bool(soup.find('meta', attrs={'name':'viewport'})))
    features['Robots'] = int(bool(soup.find('meta', attrs={'name':'robots'})))

    features['DomainTitleMatchScore'] = _similarity(host, title)
    features['URLTitleMatchScore'] = _similarity(full, title)

    # --- tags ---
    features['NoOfJS'] = len(soup.find_all('script'))
    features['NoOfImage'] = len(soup.find_all('img'))
    features['NoOfiFrame'] = len(soup.find_all('iframe'))
    features['NoOfCSS'] = len([l for l in soup.find_all('link') if l.get('rel') and 'stylesheet' in ' '.join(l.get('rel'))])
    features['LineOfCode'] = len(html.splitlines())
    features['LargestLineLength'] = max((len(l) for l in html.splitlines()), default=0)

    # --- forms ---
    forms = soup.find_all('form')
    features['HasSubmitButton'] = int(any(f.find('input', attrs={'type':'submit'}) or f.find('button') for f in forms))
    features['HasHiddenFields'] = int(any(f.find('input', attrs={'type':'hidden'}) for f in forms))
    features['HasPasswordField'] = int(any(f.find('input', attrs={'type':'password'}) for f in forms))
    features['HasExternalFormSubmit'] = int(any(urlparse(f.get('action') or '').netloc not in [host,''] for f in forms))

    # --- links ---
    links = soup.find_all('a')
    self_ref, ext_ref, empty_ref = 0, 0, 0
    for a in links:
        href = a.get('href') or ''
        if href.strip() in ['', '#']: empty_ref += 1
        elif host in href: self_ref += 1
        else: ext_ref += 1
    features['NoOfSelfRef'] = self_ref
    features['NoOfExternalRef'] = ext_ref
    features['NoOfEmptyRef'] = empty_ref

    # --- nội dung nghi ngờ ---
    lower = html.lower()
    features['Pay'] = int(any(k in lower for k in ['pay', 'payment', 'checkout']))
    features['Bank'] = int(any(k in lower for k in ['bank', 'securebank', 'atm']))
    features['Crypto'] = int(any(k in lower for k in ['crypto', 'bitcoin', 'wallet']))

    # --- độ nhiễu ---
    runs = re.findall(r'(.)\1{1,}', full)
    features['CharContinuationRate'] = len(''.join(runs)) / (len(full)+1e-6)
    ent = _char_entropy(full)
    norm = ent / math.log2(max(len(set(full)),2))
    features['URLCharProb'] = max(0.0, 1.0 - norm)

    # --- fallback các cột chưa có ---
    for c in SAFE_FEATURES:
        if c not in features:
            features[c] = 0

    return {c: features[c] for c in SAFE_FEATURES}

# ---------- helper chuyển dict -> vector ----------
def _to_ordered_vector(feat_dict, columns):
    return np.array([[feat_dict.get(col, 0) for col in columns]], dtype=float)

# ---------- dự đoán ----------
def predict_url(url, threshold=THRESHOLD, verbose=True):
    feat47 = extract_full_47_features(url, timeout=7)
    X_num = _to_ordered_vector(feat47, SAFE_FEATURES)
    X_num_scaled = scaler.transform(X_num)

    seq = tokenizer.texts_to_sequences([url])
    X_url = pad_sequences(seq, maxlen=MAX_LEN, padding='post', truncating='post')

    # prob = xác suất là SAFE (càng cao càng an toàn)
    prob = float(model.predict([X_url, X_num_scaled], verbose=0)[0,0])
    label = int(prob >= threshold)
    
    # label: 0=phishing, 1=safe
    is_safe = (label == 1)
    result = "SAFE" if is_safe else "PHISHING"
    confidence = prob if is_safe else (1 - prob)
    
    if verbose:
        print("\n" + "="*70)
        print(f"URL: {url}")
        print("-"*70)
        print(f"KET QUA: {result}")
        print(f"Xac suat SAFE: {prob*100:.2f}%")
        print(f"Xac suat PHISHING: {(1-prob)*100:.2f}%")
        print(f"Do chac chan: {confidence*100:.2f}%")
        print("="*70)
    
    return {
        "url": url,
        "result": result,
        "confidence": confidence,
        "label": label,
        "prob": prob
    }

# Giữ tên cũ để backward compatible
def predict_url_end2end(url, threshold=THRESHOLD, verbose=True):
    return predict_url(url, threshold, verbose)

# ---------- main ----------
if __name__ == "__main__":
    import sys
    
    # Nếu có argument từ command line
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        result = predict_url(test_url, verbose=True)
    else:
        # Test mặc định
        print("CACH SU DUNG:")
        print("  python detect_url.py <url>")
        print("\nVI DU:")
        print("  python detect_url.py https://www.google.com")
        print("  python detect_url.py http://www.teramill.com")
        print("\n" + "="*70)
        
        # Test phishing
        predict_url("https://www.facebook.com", verbose=True)
        predict_url("https://www.youtube.com", verbose=True)
        predict_url("https://www.instagram.com", verbose=True)
        predict_url("https://pub-0f913529526241fc8964926c7777865b.r2.dev/index.html", verbose=True)
