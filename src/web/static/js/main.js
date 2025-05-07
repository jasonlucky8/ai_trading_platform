// main.js - 入口初始化

document.addEventListener('DOMContentLoaded', function() {
    // 拖拽与布局
    if (window.initLayout) window.initLayout();
    // 全屏功能
    if (window.initFullscreen) window.initFullscreen();
    // 国际化
    if (window.initI18n) window.initI18n();
    // 信息看板Tab等
    if (window.initInfoPanel) window.initInfoPanel();
    // 其他初始化可扩展
}); 