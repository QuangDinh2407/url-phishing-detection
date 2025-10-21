// Content Script - Detect hover trên links và hiển thị tooltip

// Cấu hình
const CONFIG = {
    hoverDelay: 500,        // Delay trước khi gọi API (ms)
    tooltipOffset: 10,      // Khoảng cách tooltip với cursor (px)
    enabledDomains: 'all',  // 'all' hoặc array các domains
    checkInternalLinks: false, // Có kiểm tra links nội bộ không
};

// State
let currentHoveredLink = null;
let hoverTimer = null;
let tooltip = null;
let isCheckingURL = false;

// Khởi tạo
function init() {
    // Đảm bảo document.body sẵn sàng
    if (!document.body) {
        console.warn('document.body không sẵn sàng, retry sau 100ms');
        setTimeout(init, 100);
        return;
    }
    
    createTooltip();
    attachLinkListeners();
    console.log('URL Detection Content Script loaded successfully!');
}

// Tạo tooltip element
function createTooltip() {
    // Kiểm tra document.body tồn tại
    if (!document.body) {
        console.warn('document.body chưa sẵn sàng, đợi DOMContentLoaded');
        return;
    }
    
    // Kiểm tra tooltip đã tồn tại chưa
    if (tooltip) {
        console.log('Tooltip đã tồn tại');
        return;
    }
    
    tooltip = document.createElement('div');
    tooltip.id = 'url-detector-tooltip';
    tooltip.className = 'url-detector-tooltip hidden';
    document.body.appendChild(tooltip);
    console.log('Tooltip created successfully');
}

// Attach event listeners cho tất cả links
function attachLinkListeners() {
    // Sử dụng event delegation để handle dynamic links
    document.addEventListener('mouseover', handleMouseOver, true);
    document.addEventListener('mouseout', handleMouseOut, true);
    document.addEventListener('mousemove', handleMouseMove, true);
}

// Xử lý hover vào link
function handleMouseOver(e) {
    const link = e.target.closest('a[href]');
    
    if (!link || link === currentHoveredLink) {
        return;
    }
    
    // Lấy URL từ link
    const url = link.href;
    
    if (!url || !shouldCheckURL(url)) {
        return;
    }
    
    currentHoveredLink = link;
    
    // Highlight link đang hover
    if (link && link.classList) {
        link.classList.add('url-detector-checking');
    }
    
    // Set timer để gọi API sau delay
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => {
        checkURL(url, e.clientX, e.clientY);
    }, CONFIG.hoverDelay);
}

// Xử lý hover ra khỏi link
function handleMouseOut(e) {
    const link = e.target.closest('a[href]');
    
    if (link === currentHoveredLink) {
        clearTimeout(hoverTimer);
        
        // Kiểm tra link tồn tại trước khi remove class
        if (link && link.classList) {
            link.classList.remove('url-detector-checking');
        }
        
        currentHoveredLink = null;
        
        // Ẩn tooltip sau 1s
        setTimeout(() => {
            if (!currentHoveredLink) {
                hideTooltip();
            }
        }, 1000);
    }
}

// Xử lý di chuyển chuột
function handleMouseMove(e) {
    if (tooltip && !tooltip.classList.contains('hidden')) {
        positionTooltip(e.clientX, e.clientY);
    }
}

// Kiểm tra có nên check URL này không
function shouldCheckURL(url) {
    try {
        const urlObj = new URL(url);
        
        // Bỏ qua các protocol không phải http/https
        if (!['http:', 'https:'].includes(urlObj.protocol)) {
            return false;
        }
        
        // Bỏ qua links nội bộ nếu config tắt
        if (!CONFIG.checkInternalLinks && urlObj.hostname === window.location.hostname) {
            return false;
        }
        
        // Check enabled domains
        if (CONFIG.enabledDomains !== 'all') {
            return CONFIG.enabledDomains.some(domain => 
                urlObj.hostname.includes(domain)
            );
        }
        
        return true;
    } catch (e) {
        return false;
    }
}

// Gọi API kiểm tra URL
async function checkURL(url, mouseX, mouseY) {
    if (isCheckingURL) return;
    
    isCheckingURL = true;
    
    // Hiển thị tooltip đang loading
    showTooltip('loading', 'Đang kiểm tra...', '', mouseX, mouseY);
    
    try {
        // Kiểm tra chrome.runtime tồn tại
        if (!chrome || !chrome.runtime || !chrome.runtime.sendMessage) {
            throw new Error('Chrome runtime API không khả dụng');
        }
        
        // Gửi message đến background script
        const response = await chrome.runtime.sendMessage({
            action: 'checkURL',
            url: url
        });
        
        if (response.success) {
            const data = response.data;
            
            // Hiển thị kết quả
            if (data.result === 'SAFE') {
                showTooltip(
                    'safe',
                    '✓ URL an toàn',
                    `Độ tin cậy: ${(data.confidence * 100).toFixed(1)}%${data.fromCache ? ' (cache)' : ''}`,
                    mouseX,
                    mouseY
                );
                
                // Đánh dấu link là an toàn
                if (currentHoveredLink && currentHoveredLink.classList) {
                    currentHoveredLink.classList.add('url-detector-safe');
                    currentHoveredLink.classList.remove('url-detector-checking');
                }
                
            } else if (data.result === 'PHISHING') {
                showTooltip(
                    'danger',
                    '⚠ CẢNH BÁO: URL lừa đảo!',
                    `Độ tin cậy: ${(data.confidence * 100).toFixed(1)}%${data.fromCache ? ' (cache)' : ''}\nKHÔNG nên truy cập!`,
                    mouseX,
                    mouseY
                );
                
                // Đánh dấu link là nguy hiểm
                if (currentHoveredLink && currentHoveredLink.classList) {
                    currentHoveredLink.classList.add('url-detector-danger');
                    currentHoveredLink.classList.remove('url-detector-checking');
                    
                    // Thêm warning click handler
                    if (currentHoveredLink.addEventListener) {
                        currentHoveredLink.addEventListener('click', preventDangerousClick, { once: true });
                    }
                }
                
            } else if (data.result === 'ERROR') {
                showTooltip(
                    'warning',
                    'Không thể kiểm tra',
                    data.error || 'API không khả dụng',
                    mouseX,
                    mouseY
                );
            }
        } else {
            showTooltip(
                'warning',
                'Lỗi',
                response.error || 'Không thể kiểm tra URL',
                mouseX,
                mouseY
            );
        }
        
    } catch (error) {
        console.error('Error checking URL:', error);
        showTooltip(
            'warning',
            'Lỗi',
            'Không thể kết nối đến service',
            mouseX,
            mouseY
        );
    } finally {
        isCheckingURL = false;
    }
}

// Ngăn click vào link nguy hiểm
function preventDangerousClick(e) {
    if (!confirm('⚠️ CẢNH BÁO: Đây là URL lừa đảo!\n\nBạn có chắc chắn muốn tiếp tục?')) {
        e.preventDefault();
        e.stopPropagation();
    }
}

// Hiển thị tooltip
function showTooltip(type, title, details, x, y) {
    if (!tooltip) {
        console.warn('Tooltip chưa được khởi tạo, tạo mới...');
        createTooltip();
        if (!tooltip) return; // Vẫn không có tooltip thì thôi
    }
    
    // Lấy icon path từ extension
    const getIconPath = (iconType) => {
        const iconMap = {
            loading: chrome.runtime.getURL('icons/icon_detective_32.png'),
            safe: chrome.runtime.getURL('icons/icon_safe_64.png'),
            danger: chrome.runtime.getURL('icons/icon_danger_64.png'),
            warning: chrome.runtime.getURL('icons/icon_warning_64.png')
        };
        return iconMap[iconType] || chrome.runtime.getURL('icons/icon_detective_32.png');
    };
    
    tooltip.className = `url-detector-tooltip ${type}`;
    tooltip.innerHTML = `
        <div class="tooltip-header">
            <img src="${getIconPath(type)}" alt="${type}" class="tooltip-icon-img" />
            <span class="tooltip-title">${title}</span>
        </div>
        ${details ? `<div class="tooltip-details">${details}</div>` : ''}
    `;
    
    positionTooltip(x, y);
    tooltip.classList.remove('hidden');
}

// Ẩn tooltip
function hideTooltip() {
    if (tooltip) {
        tooltip.classList.add('hidden');
    }
}

// Định vị tooltip
function positionTooltip(x, y) {
    if (!tooltip) return;
    
    const rect = tooltip.getBoundingClientRect();
    const offset = CONFIG.tooltipOffset;
    
    let left = x + offset;
    let top = y + offset;
    
    // Đảm bảo tooltip không ra ngoài màn hình
    if (left + rect.width > window.innerWidth) {
        left = x - rect.width - offset;
    }
    
    if (top + rect.height > window.innerHeight) {
        top = y - rect.height - offset;
    }
    
    tooltip.style.left = `${left + window.scrollX}px`;
    tooltip.style.top = `${top + window.scrollY}px`;
}

// Khởi tạo khi DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Cleanup khi unload
window.addEventListener('beforeunload', () => {
    clearTimeout(hoverTimer);
    if (tooltip && tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
    }
});

