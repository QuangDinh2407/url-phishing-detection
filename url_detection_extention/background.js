// Background Service Worker cho URL Detection Extension
// Xử lý các request kiểm tra URL từ content script

const API_URL = 'http://localhost:8000/detect-url';

// Cache để lưu kết quả đã kiểm tra (tránh gọi API lặp lại)
const urlCache = new Map();
const CACHE_EXPIRY = 1000 * 60 * 30; // 30 phút

// Lắng nghe messages từ content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkURL') {
        checkURLWithCache(request.url)
            .then(result => {
                sendResponse({ success: true, data: result });
            })
            .catch(error => {
                console.error('Error checking URL:', error);
                sendResponse({ 
                    success: false, 
                    error: error.message || 'Không thể kiểm tra URL'
                });
            });
        
        // Return true để giữ message channel mở cho async response
        return true;
    }
    
    if (request.action === 'clearCache') {
        urlCache.clear();
        sendResponse({ success: true, message: 'Cache đã được xóa' });
        return true;
    }
});

// Kiểm tra URL với cache
async function checkURLWithCache(url) {
    // Chuẩn hóa URL
    const normalizedUrl = normalizeURL(url);
    
    // Kiểm tra cache
    const cached = urlCache.get(normalizedUrl);
    if (cached && (Date.now() - cached.timestamp < CACHE_EXPIRY)) {
        console.log('Cache hit for:', normalizedUrl);
        return { ...cached.data, fromCache: true };
    }
    
    // Gọi API
    console.log('Calling API for:', normalizedUrl);
    const result = await callDetectionAPI(normalizedUrl);
    
    // Lưu vào cache
    urlCache.set(normalizedUrl, {
        data: result,
        timestamp: Date.now()
    });
    
    // Giới hạn cache size (max 1000 entries)
    if (urlCache.size > 1000) {
        const firstKey = urlCache.keys().next().value;
        urlCache.delete(firstKey);
    }
    
    return { ...result, fromCache: false };
}

// Chuẩn hóa URL
function normalizeURL(url) {
    try {
        const urlObj = new URL(url);
        // Loại bỏ fragment và normalize
        return urlObj.origin + urlObj.pathname + urlObj.search;
    } catch (e) {
        return url;
    }
}

// Gọi API phát hiện URL
async function callDetectionAPI(url) {
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
        
        // Validate response data
        if (!data.result) {
            throw new Error('Invalid API response');
        }
        
        return {
            url: data.url || url,
            result: data.result, // 'SAFE' hoặc 'PHISHING'
            confidence: data.confidence || 0,
            prob: data.prob || 0,
            label: data.label
        };
        
    } catch (error) {
        console.error('API Error:', error);
        
        // Nếu API không khả dụng, trả về kết quả mặc định
        if (error.message.includes('fetch')) {
            return {
                url: url,
                result: 'ERROR',
                confidence: 0,
                prob: 0,
                error: 'API không khả dụng. Vui lòng kiểm tra server đang chạy.'
            };
        }
        
        throw error;
    }
}

// Dọn dẹp cache định kỳ (mỗi 1 giờ)
setInterval(() => {
    const now = Date.now();
    for (const [key, value] of urlCache.entries()) {
        if (now - value.timestamp > CACHE_EXPIRY) {
            urlCache.delete(key);
        }
    }
    console.log('Cache cleaned. Current size:', urlCache.size);
}, 1000 * 60 * 60); // 1 giờ

// Log khi extension được cài đặt hoặc cập nhật
chrome.runtime.onInstalled.addListener((details) => {
    console.log('URL Detection Extension installed/updated:', details.reason);
    
    if (details.reason === 'install') {
        console.log('First time installation!');
    } else if (details.reason === 'update') {
        console.log('Extension updated!');
        // Xóa cache khi update
        urlCache.clear();
    }
});

console.log('Background service worker loaded successfully!');

