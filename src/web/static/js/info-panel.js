// info-panel.js - 信息看板Tab切换与内容切换
window.initInfoPanel = function() {
    const tabGroup = document.querySelector('.tab-group');
    if (!tabGroup) return;
    tabGroup.addEventListener('click', function(e) {
        const btn = e.target.closest('.tab-btn');
        if (!btn) return;
        // 切换Tab按钮激活态
        tabGroup.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // 切换内容面板
        const tab = btn.getAttribute('data-tab');
        document.querySelectorAll('.tab-panel').forEach(panel => {
            if (panel.getAttribute('data-tab-panel') === tab) {
                panel.classList.add('active');
                panel.style.display = 'block';
            } else {
                panel.classList.remove('active');
                panel.style.display = 'none';
            }
        });
    });
}; 