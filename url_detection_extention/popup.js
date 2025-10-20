const $ = document.querySelector.bind(document)
const $$ = document.querySelectorAll.bind(document)

// Các phần tử DOM
const urlInput = $('#urlInput');
const checkBtn = $('#checkBtn');
const getCurrentUrlBtn = $('#getCurrentUrlBtn');
const result = $('#result');
const loading = $('#loading');
const resultIcon = $('#resultIcon');
const resultText = $('#resultText');
const resultDetails = $('#resultDetails');

// Xử lý sự kiện click nút kiểm tra
checkBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (url) {
        checkURL(url);
    } else {
        showResult('warning', '<img src="icons/icon_warning_64.png" alt="Warning" class="result-icon">', 'Vui lòng nhập URL', 'Bạn cần nhập một URL để kiểm tra.');
    }
});

// Xử lý sự kiện nhấn Enter trong input
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        checkBtn.click();
    }
});

// Xử lý sự kiện lấy URL hiện tại
getCurrentUrlBtn.addEventListener('click', async () => {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
            urlInput.value = tab.url;
            checkURL(tab.url);
        }
    } catch (error) {
        console.error('Error getting current URL:', error);
        showResult('danger', '<img src="icons/icon_danger_64.png" alt="Error" class="result-icon">', 'Lỗi', 'Không thể lấy URL hiện tại.');
    }
});

// Hàm kiểm tra URL
async function checkURL(url) {
    // Hiển thị loading
    result.classList.add('hidden');
    loading.classList.remove('hidden');
    
    try {
        // Validate URL
        if (!isValidURL(url)) {
            showResult('warning', '<img src="icons/icon_warning_64.png" alt="Warning" class="result-icon">', 'URL không hợp lệ', 'Vui lòng nhập một URL đúng định dạng.');
            return;
        }
        
        // Gọi API để kiểm tra URL
        await callDetectionAPI(url);
        
    } catch (error) {
        console.error('Error checking URL:', error);
        showResult('danger', '<img src="icons/icon_danger_64.png" alt="Error" class="result-icon">', 'Lỗi', 'Đã có lỗi xảy ra khi kiểm tra URL. Vui lòng kiểm tra server đang chạy.');
    } finally {
        loading.classList.add('hidden');
    }
}

// Hàm validate URL
function isValidURL(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Hàm hiển thị kết quả
function showResult(type, icon, title, details) {
    loading.classList.add('hidden');
    
    resultIcon.innerHTML = icon;
    resultText.textContent = title;
    resultDetails.textContent = details;
    
    result.className = 'result ' + type;
    result.classList.remove('hidden');
}

// Gọi API phát hiện URL lừa đảo
async function callDetectionAPI(url) {
    const API_URL = 'http://localhost:8000/detect-url';
    
    try {
        const response = await fetch(`${API_URL}?url=${encodeURIComponent(url)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Xử lý kết quả từ API
        if (data.result === 'SAFE') {
            showResult(
                'safe',
                '<img src="icons/icon_safe_64.png" alt="Safe" class="result-icon">',
                '✓ URL an toàn',
                `Độ chắc chắn: ${(data.confidence * 100).toFixed(2)}%\nXác suất SAFE: ${(data.prob * 100).toFixed(2)}%`
            );
        } else if (data.result === 'PHISHING') {
            showResult(
                'danger',
                '<img src="icons/icon_danger_64.png" alt="Danger" class="result-icon">',
                '⚠ CẢNH BÁO: URL lừa đảo!',
                `Độ chắc chắn: ${(data.confidence * 100).toFixed(2)}%\nXác suất PHISHING: ${((1 - data.prob) * 100).toFixed(2)}%\n\nĐây có thể là trang web lừa đảo. KHÔNG truy cập!`
            );
        } else {
            showResult(
                'warning',
                '<img src="icons/icon_warning_64.png" alt="Warning" class="result-icon">',
                'Không xác định',
                'Không thể xác định độ an toàn của URL này.'
            );
        }
        
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Tự động focus vào input khi mở popup
window.addEventListener('load', () => {
    urlInput.focus();
});

