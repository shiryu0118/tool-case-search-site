/**
 * ツール活用事例検索サイト - メインJavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // ページトップへ戻るボタン
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        // スクロール位置に応じて表示/非表示
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        // クリック時の動作
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // 外部リンクの処理
    document.querySelectorAll('a[target="_blank"]').forEach(link => {
        // rel属性の追加（セキュリティ対策）
        if (!link.getAttribute('rel')) {
            link.setAttribute('rel', 'noopener noreferrer');
        }
        
        // クリック分析用のイベント（将来的な拡張用）
        link.addEventListener('click', function() {
            const url = this.getAttribute('href');
            const title = this.textContent.trim();
            
            // 分析用のログ（実際の実装では分析サービスに送信）
            console.log('External link clicked:', {
                url: url,
                title: title,
                timestamp: new Date().toISOString()
            });
        });
    });
    
    // ツールチップの初期化（Bootstrapの機能）
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 検索フォームのバリデーション
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const toolNameInput = document.getElementById('tool_name');
            if (!toolNameInput || !toolNameInput.value.trim()) {
                e.preventDefault();
                
                // エラー表示
                toolNameInput.classList.add('is-invalid');
                
                // フォーカス
                toolNameInput.focus();
            }
        });
    }
    
    // 検索履歴ページの機能
    if (window.location.pathname.includes('/history')) {
        // 検索履歴の空状態チェック
        const historyList = document.getElementById('historyList');
        const emptyState = document.querySelector('.empty-history-state');
        
        if (historyList && emptyState) {
            if (historyList.children.length === 0) {
                emptyState.style.display = 'block';
            } else {
                emptyState.style.display = 'none';
            }
        }
    }
    
    // 検索結果ページの機能
    if (window.location.pathname.includes('/search') || document.querySelector('.search-result-item')) {
        // 結果がない場合のメッセージ表示
        const resultsList = document.getElementById('articlesList');
        const noResultsMessage = document.querySelector('.no-results-message');
        
        if (resultsList && noResultsMessage) {
            if (resultsList.children.length === 0) {
                noResultsMessage.style.display = 'block';
            } else {
                noResultsMessage.style.display = 'none';
            }
        }
    }
});

// ユーティリティ関数

/**
 * 日付をフォーマット
 * @param {Date|string} date - 日付オブジェクトまたはISO形式の日付文字列
 * @param {string} format - フォーマット ('short'|'medium'|'long')
 * @returns {string} フォーマットされた日付文字列
 */
function formatDate(date, format = 'medium') {
    if (!date) return '日付なし';
    
    const d = typeof date === 'string' ? new Date(date) : date;
    
    // 無効な日付
    if (isNaN(d.getTime())) return '無効な日付';
    
    const year = d.getFullYear();
    const month = d.getMonth() + 1;
    const day = d.getDate();
    const hours = d.getHours();
    const minutes = d.getMinutes();
    
    // パディング
    const pad = num => num.toString().padStart(2, '0');
    
    switch (format) {
        case 'short':
            return `${year}/${pad(month)}/${pad(day)}`;
        case 'long':
            return `${year}年${month}月${day}日 ${pad(hours)}:${pad(minutes)}`;
        case 'medium':
        default:
            return `${year}年${month}月${day}日`;
    }
}

/**
 * テキストの省略
 * @param {string} text - 元のテキスト
 * @param {number} maxLength - 最大長
 * @returns {string} 省略されたテキスト
 */
function truncateText(text, maxLength = 100) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}