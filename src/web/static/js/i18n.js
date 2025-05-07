/**
 * 国际化(i18n)支持
 * 提供中英文切换功能
 */

// 语言包定义
const translations = {
    'zh-CN': {
        // 页面标题
        'page_title': 'AIGO量化平台 - TradingView图表',
        
        // 市场数据设置
        'market_data_settings': '市场数据设置',
        'exchange': '交易所',
        'symbol': '交易对',
        'timeframe': '时间帧',
        'data_points': '数据点数量',
        'fetch_data': '获取数据',
        
        // 时间帧选项
        'tf_1m': '1分钟',
        'tf_5m': '5分钟',
        'tf_15m': '15分钟',
        'tf_1h': '1小时',
        'tf_4h': '4小时',
        'tf_1d': '1天',
        'tf_1w': '1周',
        
        // 技术指标
        'indicators': '技术指标',
        'show_ma': '显示移动平均线',
        'show_bollinger': '显示布林带',
        'period': '周期',
        'std_dev': '标准差',
        'apply_indicators': '应用指标',
        
        // 图表区域
        'chart_title': 'TradingView风格图表',
        'data_preview': '数据预览',
        'time': '时间',
        'open': '开盘价',
        'high': '最高价',
        'low': '最低价',
        'close': '收盘价',
        'volume': '成交量',
        
        // 消息提示
        'loading_data': '正在获取数据，请稍候...',
        'data_loaded': '数据加载成功！您可以添加技术指标或调整图表显示。',
        'select_data': '请选择交易所和交易对，然后点击"获取数据"按钮获取数据。',
        'data_error': '获取数据失败，请检查交易所和交易对是否正确。',
        'empty_data': '获取的数据为空，请尝试其他交易对或时间范围。',
        'connection_error': '获取数据失败，请稍后重试或检查网络连接。',
        'rendering_error': '图表渲染错误: ',
        
        // 语言切换
        'language': '语言',
        'lang_en': 'English',
        'lang_zh': '中文',
        'switch_to_english': '当前：中文 - 点击切换到英文',
        'switch_to_chinese': '切换到中文',
        'language_changed_to': '语言已切换为',
        'chinese': '中文',
        'english': '英文',
        
        // 布局相关
        'full_screen': '全屏',
        'settings': '设置',
        'toggle_panel': '折叠/展开面板',
        'show': '显示',
        'hide': '隐藏',
        'apply': '应用',
        'cancel': '取消',
        'confirm': '确认',
        'close': '关闭',
        'dock_panel': '锚定面板',
        
        // 功能区标签
        'strategy_test': '策略测试',
        'playback_board': '回放看板',
        'trading_panel': '交易面板',
        
        // 系统消息
        'settings_saved': '设置已保存',
        'indicators_applied': '技术指标已应用',
        'indicators_panel_not_ready': '技术指标面板功能未就绪',
        'indicators_function_not_ready': '应用指标功能未就绪',
        'panel_docked': '面板已锚定到原始位置',
        
        // 新增语言包
        '平台名称': 'AIGO TradeView',
        '行情': '行情',
        '策略': '策略',
        '回测': '回测',
        '交易': '交易',
        '币种信息': '币种信息',
        '深度': '深度',
        '新闻': '新闻',
        '功能区': '功能区',
        '信息面板': '信息面板',
        '全屏': '全屏',
        '设置': '设置',
        '中英文切换': '中/EN',
    },
    'en-US': {
        // Page title
        'page_title': 'AIGO Quantitative Trading Platform - TradingView Chart',
        
        // Market data settings
        'market_data_settings': 'Market Data Settings',
        'exchange': 'Exchange',
        'symbol': 'Symbol',
        'timeframe': 'Timeframe',
        'data_points': 'Data Points',
        'fetch_data': 'Fetch Data',
        
        // Timeframe options
        'tf_1m': '1 Minute',
        'tf_5m': '5 Minutes',
        'tf_15m': '15 Minutes',
        'tf_1h': '1 Hour',
        'tf_4h': '4 Hours',
        'tf_1d': '1 Day',
        'tf_1w': '1 Week',
        
        // Technical indicators
        'indicators': 'Technical Indicators',
        'show_ma': 'Show Moving Averages',
        'show_bollinger': 'Show Bollinger Bands',
        'period': 'Period',
        'std_dev': 'Standard Deviation',
        'apply_indicators': 'Apply Indicators',
        
        // Chart area
        'chart_title': 'TradingView Style Chart',
        'data_preview': 'Data Preview',
        'time': 'Time',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        
        // Messages
        'loading_data': 'Loading data, please wait...',
        'data_loaded': 'Data loaded successfully! You can add technical indicators or adjust the chart display.',
        'select_data': 'Please select an exchange and symbol, then click "Fetch Data" button to get data.',
        'data_error': 'Failed to get data, please check if the exchange and symbol are correct.',
        'empty_data': 'The data returned is empty, please try another symbol or time range.',
        'connection_error': 'Failed to get data, please try again later or check your network connection.',
        'rendering_error': 'Chart rendering error: ',
        
        // Language toggle
        'language': 'Language',
        'lang_en': 'English',
        'lang_zh': '中文',
        'switch_to_english': 'Switch to English',
        'switch_to_chinese': 'Current: English - Click to switch to Chinese',
        'language_changed_to': 'Language changed to',
        'chinese': 'Chinese',
        'english': 'English',
        
        // Layout related
        'full_screen': 'Full Screen',
        'settings': 'Settings',
        'toggle_panel': 'Toggle Panel',
        'show': 'Show',
        'hide': 'Hide',
        'apply': 'Apply',
        'cancel': 'Cancel',
        'confirm': 'Confirm',
        'close': 'Close',
        'dock_panel': 'Dock Panel',
        
        // Function panel tabs
        'strategy_test': 'Strategy Test',
        'playback_board': 'Playback Board',
        'trading_panel': 'Trading Panel',
        
        // System messages
        'settings_saved': 'Settings saved',
        'indicators_applied': 'Technical indicators applied',
        'indicators_panel_not_ready': 'Technical indicators panel is not ready',
        'indicators_function_not_ready': 'Apply indicators function is not ready',
        'panel_docked': 'Panel docked to original position',
        
        // 新增语言包
        '平台名称': 'AIGO TradeView',
        '行情': 'Market',
        '策略': 'Strategy',
        '回测': 'Backtest',
        '交易': 'Trade',
        '币种信息': 'Coin Info',
        '深度': 'Depth',
        '新闻': 'News',
        '功能区': 'Panel',
        '信息面板': 'Info Panel',
        '全屏': 'Fullscreen',
        '设置': 'Settings',
        '中英文切换': 'EN/中',
    }
};

// 当前语言
let currentLang = localStorage.getItem('tradingPlatformLang') || 'zh-CN';

// 获取翻译文本
function t(key) {
    if (translations[currentLang] && translations[currentLang][key]) {
        return translations[currentLang][key];
    }
    // 如果找不到翻译，返回键名
    return key;
}

// 切换语言
function switchLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem('tradingPlatformLang', lang);
        updatePageTexts();
        return true;
    }
    return false;
}

// 获取当前语言
function getCurrentLanguage() {
    return currentLang;
}

// 更新页面上的所有文本
function updatePageTexts() {
    // 更新页面标题
    document.title = t('page_title');
    
    // 更新所有带有data-i18n属性的元素
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (key) {
            if (el.tagName === 'INPUT' && (el.type === 'text' || el.type === 'search')) {
                el.placeholder = t(key);
            } else if (el.tagName === 'INPUT' && el.type === 'button') {
                el.value = t(key);
            } else {
                el.textContent = t(key);
            }
        }
    });
    
    // 更新按钮提示文本
    const tippedElements = document.querySelectorAll('[data-i18n-title]');
    tippedElements.forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (key) {
            el.title = t(key);
        }
    });
    
    // 特殊处理一些动态内容
    if (document.getElementById('infoMessage')) {
        const infoMessage = document.getElementById('infoMessage');
        if (infoMessage.classList.contains('alert-info') && !infoMessage.classList.contains('alert-danger')) {
            if (window.chartData && window.chartData.length > 0) {
                infoMessage.textContent = t('data_loaded');
            } else {
                infoMessage.textContent = t('select_data');
            }
        }
    }
    
    // 更新语言按钮状态
    const languageToggleBtn = document.getElementById('languageToggleBtn');
    if (languageToggleBtn) {
        const currentLang = getCurrentLanguage();
        if (currentLang === 'zh-CN') {
            languageToggleBtn.setAttribute('title', t('switch_to_english'));
        } else {
            languageToggleBtn.setAttribute('title', t('switch_to_chinese'));
        }
    }
    
    // 更新按钮文本
    if (document.getElementById('fetchDataBtn')) {
        document.getElementById('fetchDataBtn').textContent = t('fetch_data');
    }
    if (document.getElementById('applyIndicatorsBtn')) {
        document.getElementById('applyIndicatorsBtn').textContent = t('apply_indicators');
    }
    
    // 触发自定义事件，通知其他组件语言已更改
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: currentLang } }));
}

// 初始化语言
function initLanguage() {
    updatePageTexts();
    
    // 添加语言切换监听器 - 注释掉这部分，因为我们已经在jQuery ready中添加了事件监听器
    /*
    document.addEventListener('DOMContentLoaded', () => {
        const langToggle = document.getElementById('languageToggle');
        if (langToggle) {
            langToggle.addEventListener('click', () => {
                const newLang = currentLang === 'zh-CN' ? 'en-US' : 'zh-CN';
                switchLanguage(newLang);
            });
        }
    });
    */
}

// 导出函数到全局作用域
window.i18n = {
    t,
    switchLanguage,
    getCurrentLanguage,
    updatePageTexts,
    initLanguage
};

// 自动初始化
document.addEventListener('DOMContentLoaded', initLanguage);

document.addEventListener('DOMContentLoaded', function() {
    const btn = document.getElementById('langSwitchBtn');
    const icon = btn ? btn.querySelector('.ri-translate-2') : null;
    function updateLangIcon() {
        if (!icon) return;
        if (currentLang === 'zh-CN' || currentLang === 'zh') {
            icon.style.color = '';
            icon.style.transform = 'rotate(0deg)';
        } else {
            icon.style.color = '#2563eb'; // 英文时高亮蓝色
            icon.style.transform = 'rotate(180deg)';
        }
    }
    updateLangIcon();
    if (!btn) return;
    btn.addEventListener('click', function() {
        const newLang = (currentLang === 'zh-CN' || currentLang === 'zh') ? 'en-US' : 'zh-CN';
        switchLanguage(newLang);
        updateLangIcon();
    });
}); 