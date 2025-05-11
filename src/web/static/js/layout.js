// ========== 极简拖拽分割条功能 ========== //
document.addEventListener('DOMContentLoaded', function() {
    // ========== 初始化function-section高度，保证chart-section最小1/2屏，初始高度使用CSS默认值 ==========
    (function() {
        const functionSection = document.querySelector('.function-section');
        const chartSection = document.querySelector('.chart-section');
        const leftPanel = document.getElementById('leftPanel');
        if (!functionSection || !chartSection || !leftPanel) return;
        
        // 直接使用CSS中设置的高度，不再动态计算初始高度
        // const panelHeight = leftPanel.offsetHeight || (window.innerHeight - 56);
        // const minChartHeight = Math.floor(window.innerHeight * 0.5); // 最小1/2屏
        // const initChartHeight = Math.floor(window.innerHeight * 0.25); // 初始1/4屏
        // let initFunctionHeight = panelHeight - initChartHeight;
        
        // // 添加最大值限制，防止高度闪变
        // const maxFunctionHeight = 220; // 与CSS中设置一致
        // if (initFunctionHeight < 100) initFunctionHeight = 100;
        // if (initFunctionHeight > maxFunctionHeight) initFunctionHeight = maxFunctionHeight;
        
        // functionSection.style.height = initFunctionHeight + 'px';
        
        // 只设置chart-section的高度，确保填充剩余空间
        const panelHeight = leftPanel.offsetHeight || (window.innerHeight - 56);
        const functionHeight = functionSection.offsetHeight || 220; // 默认使用CSS设置的高度
        chartSection.style.flexBasis = (panelHeight - functionHeight - 4) + 'px';
    })();

    // ========== 上下分割线拖拽 ==========
    (function() {
        const functionSection = document.querySelector('.function-section');
        const chartSection = document.querySelector('.chart-section');
        const leftPanel = document.getElementById('leftPanel');
        if (!functionSection || !chartSection || !leftPanel) return;
        let isDragging = false;
        let startY = 0;
        let startFunctionHeight = 0;
        let startPanelHeight = 0;
        functionSection.addEventListener('mousedown', function(e) {
            const rect = functionSection.getBoundingClientRect();
            if (e.button !== 0 || e.clientY - rect.top > 8) return;
            isDragging = true;
            functionSection.classList.add('dragging');
            document.body.style.cursor = 'ns-resize';
            document.body.style.userSelect = 'none';
            startY = e.clientY;
            startFunctionHeight = functionSection.offsetHeight;
            startPanelHeight = leftPanel.offsetHeight;
            
            // 拖拽时移除transition，确保流畅拖拽
            const prevFunctionTransition = functionSection.style.transition;
            const prevChartTransition = chartSection.style.transition;
            functionSection.style.transition = 'none';
            chartSection.style.transition = 'none';
            
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', function onMouseUpWithTransition(e) {
                onMouseUp();
                // 拖拽结束后恢复transition
                functionSection.style.transition = prevFunctionTransition || '';
                chartSection.style.transition = prevChartTransition || '';
                
                // 触发自定义事件，通知图表调整大小
                document.dispatchEvent(new CustomEvent('dragResizeEnd'));
                
                window.removeEventListener('mouseup', onMouseUpWithTransition);
            });
        });
        function onMouseMove(e) {
            if (!isDragging) return;
            const dy = e.clientY - startY;
            let newFunctionHeight = startFunctionHeight - dy;
            let minFunctionHeight = 100;
            let maxFunctionHeight = startPanelHeight - Math.floor(window.innerHeight * 0.5); // chart-section最小1/2屏
            if (newFunctionHeight < minFunctionHeight) newFunctionHeight = minFunctionHeight;
            if (newFunctionHeight > maxFunctionHeight) newFunctionHeight = maxFunctionHeight;
            functionSection.style.height = newFunctionHeight + 'px';
            chartSection.style.flexBasis = (startPanelHeight - newFunctionHeight - 4) + 'px';
            
            // 实时触发图表调整事件
            document.dispatchEvent(new CustomEvent('dragResizeEnd'));
        }
        function onMouseUp() {
            isDragging = false;
            functionSection.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            window.removeEventListener('mousemove', onMouseMove);
        }
        // 监听窗口resize，动态调整最小高度
        window.addEventListener('resize', function() {
            const panelHeight = leftPanel.offsetHeight || (window.innerHeight - 56);
            let functionHeight = functionSection.offsetHeight;
            let minFunctionHeight = 100;
            let maxFunctionHeight = panelHeight - Math.floor(window.innerHeight * 0.5);
            if (functionHeight < minFunctionHeight) functionHeight = minFunctionHeight;
            if (functionHeight > maxFunctionHeight) functionHeight = maxFunctionHeight;
            functionSection.style.height = functionHeight + 'px';
            chartSection.style.flexBasis = (panelHeight - functionHeight - 4) + 'px';
        });
    })();

    // ========== 左右分割线拖拽（right-panel的border-left） ==========
    (function() {
                const rightPanel = document.getElementById('rightPanel');
                    const mainContent = document.querySelector('.main-content');
            const leftPanel = document.getElementById('leftPanel');
        if (!rightPanel || !mainContent || !leftPanel) return;
        let isDragging = false;
        let startX = 0;
        let startWidth = 0;
        let startLeftWidth = 0;
        let prevTransition = '';
        rightPanel.addEventListener('mousedown', function(e) {
            // 仅允许在左侧4px区域拖拽
            const rect = rightPanel.getBoundingClientRect();
            if (e.button !== 0 || e.clientX - rect.left > 8) return;
            isDragging = true;
            rightPanel.classList.add('dragging');
            document.body.style.cursor = 'ew-resize';
            document.body.style.userSelect = 'none';
            startX = e.clientX;
            startWidth = rightPanel.offsetWidth;
            startLeftWidth = leftPanel.offsetWidth;
            prevTransition = rightPanel.style.transition;
            rightPanel.style.transition = 'none';
            leftPanel.style.transition = 'none';
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
        });
        function onMouseMove(e) {
            if (!isDragging) return;
            let dx = startX - e.clientX;
            let newWidth = startWidth + dx;
            if (newWidth < 220) newWidth = 220;
            if (newWidth > window.innerWidth * 0.5) newWidth = window.innerWidth * 0.5;
            rightPanel.style.width = newWidth + 'px';
            leftPanel.style.flexBasis = (window.innerWidth - newWidth) + 'px';
            
            // 实时触发图表调整事件
            document.dispatchEvent(new CustomEvent('dragResizeEnd'));
        }
        function onMouseUp() {
            isDragging = false;
            rightPanel.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            rightPanel.style.transition = prevTransition || '';
            leftPanel.style.transition = '';
            leftPanel.style.flexBasis = '';
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
            
            // 触发自定义事件，通知图表调整大小
            document.dispatchEvent(new CustomEvent('dragResizeEnd'));
        }
    })();

    // ========== 左侧功能区选项卡切换 ==========
    const tabBtns = document.querySelectorAll('.function-tabs .tab-btn');
    const tabPanels = document.querySelectorAll('.function-tab-content .tab-panel');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            tabPanels.forEach(panel => {
                if(panel.getAttribute('data-tab-panel') === tab) {
                    panel.classList.add('active');
                    panel.style.display = '';
                } else {
                    panel.classList.remove('active');
                    panel.style.display = 'none';
                }
            });
        });
    });

    // ========== 币值对选择模态框逻辑 ==========
    const openPairModalBtn = document.getElementById('openPairModalBtn');
    const pairModal = document.getElementById('pairModal');
    const closePairModalBtn = document.getElementById('closePairModalBtn');
    const confirmPairBtn = document.getElementById('confirmPairBtn');
    const pairListContainer = document.getElementById('pairListContainer');
    let selectedPair = null;
    // 币对数据
    const pairListData = [
        { symbol: 'BTC/USDT', market: 'Binance', icon: `<span style='display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='18' height='18' viewBox='0 0 20 20' style='height:100%;'><circle cx='10' cy='10' r='10' fill='#f7931a'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#fff' font-family='Arial' dy='.3em'>₿</text></svg></span>`, marketLogo: `<span style='display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='16' height='16' viewBox='0 0 20 20' style='height:100%;'><rect width='20' height='20' rx='5' fill='#f3ba2f'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#222' font-family='Arial' dy='.3em'>B</text></svg></span>`, type: 'spot' },
        { symbol: 'ETH/USDT', market: 'Binance', icon: `<span style='display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='18' height='18' viewBox='0 0 20 20' style='height:100%;'><circle cx='10' cy='10' r='10' fill='#627eea'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#fff' font-family='Arial' dy='.3em'>Ξ</text></svg></span>`, marketLogo: `<span style='display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='16' height='16' viewBox='0 0 20 20' style='height:100%;'><rect width='20' height='20' rx='5' fill='#f3ba2f'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#222' font-family='Arial' dy='.3em'>B</text></svg></span>`, type: 'spot' },
        { symbol: 'BTC/USDT', market: 'OKX', icon: `<span style='display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='18' height='18' viewBox='0 0 20 20' style='height:100%;'><rect width='20' height='20' rx='5' fill='#000'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#fff' font-family='Arial' dy='.3em'>OK</text></svg></span>`, marketLogo: `<span style='display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='16' height='16' viewBox='0 0 20 20' style='height:100%;'><rect width='20' height='20' rx='5' fill='#000'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#fff' font-family='Arial' dy='.3em'>OK</text></svg></span>`, type: 'spot' },
        { symbol: 'ETH/USDT', market: 'OKX', icon: `<span style='display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='18' height='18' viewBox='0 0 20 20' style='height:100%;'><rect width='20' height='20' rx='5' fill='#000'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#fff' font-family='Arial' dy='.3em'>OK</text></svg></span>`, marketLogo: `<span style='display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#f7f7fa;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,0.04);'><svg width='16' height='16' viewBox='0 0 20 20' style='height:100%;'><rect width='20' height='20' rx='5' fill='#000'/><text x='50%' y='55%' text-anchor='middle' font-size='10' fill='#fff' font-family='Arial' dy='.3em'>OK</text></svg></span>`, type: 'spot' }
    ];
    // 选择币对后自动切换K线并更新按钮文本
    function setPairBtnText(symbol) {
        if (openPairModalBtn) openPairModalBtn.textContent = symbol;
    }
    // 渲染币对列表，支持搜索过滤
    function renderPairList(filter = '') {
        if (!pairListContainer) return;
        let html = '<ul class="pair-list">';
        const filterLower = filter.trim().toLowerCase();
        const filtered = pairListData.filter(item =>
            item.symbol.toLowerCase().includes(filterLower) ||
            item.market.toLowerCase().includes(filterLower)
        );
        filtered.forEach((item, idx) => {
            html += `<li class="pair-list-item" data-symbol="${item.symbol}" data-market="${item.market}">
                <span class="pair-icon">${item.icon}</span>
                <div class="pair-info">
                    <span class="pair-symbol">${item.symbol}</span>
                    <span class="pair-market">${item.market}</span>
                </div>
                <div class="pair-right">
                    <span class="pair-market-logo">${item.marketLogo}</span>
                    <span class="pair-market">${item.market}</span>
                </div>
            </li>`;
        });
        html += '</ul>';
        pairListContainer.innerHTML = html;
        // 绑定点击事件
        const items = pairListContainer.querySelectorAll('.pair-list-item');
        items.forEach(item => {
            item.addEventListener('click', function() {
                items.forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                const symbol = item.getAttribute('data-symbol');
                const market = item.getAttribute('data-market');
                setPairBtnText(symbol);
                if (window.loadMarketDataBySymbol) {
                    window.loadMarketDataBySymbol(symbol, market);
                } else {
                    console.log('选择币对:', {symbol, market});
                }
                pairModal.style.display = 'none';
            });
        });
    }
    // 搜索框事件
    const pairSearchInput = document.getElementById('pairSearchInput');
    const pairSearchClearBtn = document.getElementById('pairSearchClearBtn');
    if (pairSearchInput) {
        pairSearchInput.addEventListener('input', function() {
            renderPairList(pairSearchInput.value);
            if (pairSearchInput.value) {
                pairSearchClearBtn && (pairSearchClearBtn.style.display = 'flex');
            } else {
                pairSearchClearBtn && (pairSearchClearBtn.style.display = 'none');
            }
        });
    }
    if (pairSearchClearBtn && pairSearchInput) {
        pairSearchClearBtn.addEventListener('click', function(e) {
            pairSearchInput.value = '';
            pairSearchInput.focus();
            pairSearchClearBtn.style.display = 'none';
            renderPairList('');
        });
    }
    // 打开模态框时渲染
    if (openPairModalBtn && pairModal) {
        openPairModalBtn.addEventListener('click', function() {
            renderPairList();
            pairModal.style.display = 'flex';
            if (pairSearchInput) pairSearchInput.value = '';
        });
    }
    // 关闭模态框
    if (closePairModalBtn && pairModal) {
        closePairModalBtn.addEventListener('click', function() {
            pairModal.style.display = 'none';
        });
    }
    // 点击遮罩关闭
    if (pairModal) {
        pairModal.addEventListener('click', function(e) {
            if (e.target === pairModal) {
                pairModal.style.display = 'none';
            }
        });
    }
    // 确认选择
    if (confirmPairBtn && pairModal) {
        confirmPairBtn.addEventListener('click', function() {
            if (!selectedPair) return;
            pairModal.style.display = 'none';
            // 切换K线数据
            if (window.loadMarketDataBySymbol) {
                window.loadMarketDataBySymbol(selectedPair.symbol, selectedPair.market);
            } else {
                // 兼容旧逻辑
                console.log('选择币对:', selectedPair);
            }
        });
    }
    // 页面加载时默认显示第一个币对
    if (openPairModalBtn && pairListData.length > 0) {
        setPairBtnText(pairListData[0].symbol);
    }

    // ========== 时间周期选择模态框逻辑 ==========
    const openTimeframeModalBtn = document.getElementById('openTimeframeModalBtn');
    const timeframeModal = document.getElementById('timeframeModal');
    const closeTimeframeModalBtn = document.getElementById('closeTimeframeModalBtn');
    const timeframeListContainer = document.getElementById('timeframeListContainer');
    let currentTimeframe = '1h'; // 默认时间周期
    
    // 获取时间周期数据，优先使用chart.js中定义的全局数据
    const timeframeListData = window.timeframeListData || [
        { value: '5m', text: '5分钟', icon: '<i class="ri-timer-line"></i>' },
        { value: '10m', text: '10分钟', icon: '<i class="ri-timer-line"></i>' },
        { value: '15m', text: '15分钟', icon: '<i class="ri-timer-line"></i>' },
        { value: '30m', text: '30分钟', icon: '<i class="ri-timer-line"></i>' },
        { value: '45m', text: '45分钟', icon: '<i class="ri-timer-line"></i>' },
        { value: '1h', text: '1小时', icon: '<i class="ri-time-line"></i>' },
        { value: '2h', text: '2小时', icon: '<i class="ri-time-line"></i>' },
        { value: '4h', text: '4小时', icon: '<i class="ri-time-line"></i>' },
        { value: '1d', text: '1日', icon: '<i class="ri-calendar-line"></i>' },
        { value: '1w', text: '1周', icon: '<i class="ri-calendar-line"></i>' },
        { value: '1M', text: '1月', icon: '<i class="ri-calendar-line"></i>' }
    ];
    
    // 设置时间周期按钮文本
    function setTimeframeBtnText(timeframe) {
        if (openTimeframeModalBtn) {
            const item = timeframeListData.find(item => item.value === timeframe);
            // 使用翻译函数获取翻译文本
            if (window.t && item) {
                openTimeframeModalBtn.textContent = window.t(item.text);
            } else {
                openTimeframeModalBtn.textContent = item ? item.text : timeframe;
            }
        }
        currentTimeframe = timeframe;
    }
    
    // 渲染时间周期列表
    function renderTimeframeList() {
        if (!timeframeListContainer) return;
        
        // 根据周期类型对时间周期进行分组
        const groups = {
            minute: timeframeListData.filter(item => item.value.endsWith('m')),
            hour: timeframeListData.filter(item => item.value.endsWith('h')),
            day: timeframeListData.filter(item => item.value.endsWith('d')),
            week: timeframeListData.filter(item => item.value.endsWith('w')),
            month: timeframeListData.filter(item => item.value.endsWith('M'))
        };
        
        let html = '<div class="timeframe-groups">';
        
        // 使用翻译函数获取分组标题
        const hasTranslateFunc = typeof window.t === 'function';
        
        // 分钟组
        if (groups.minute.length > 0) {
            html += '<div class="timeframe-group">';
            const minutesTitle = hasTranslateFunc ? window.t('分钟') : '分钟';
            html += `<div class="timeframe-group-header">${minutesTitle}</div>`;
            html += '<ul class="pair-list timeframe-list">';
            groups.minute.forEach(item => {
                const isActive = item.value === currentTimeframe ? 'selected' : '';
                const itemText = hasTranslateFunc ? window.t(item.text) : item.text;
                html += `<li class="pair-list-item timeframe-item ${isActive}" data-timeframe="${item.value}">
                    <span class="timeframe-icon">${item.icon}</span>
                    <div class="pair-info">
                        <span class="timeframe-text">${itemText}</span>
                    </div>
                </li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        // 小时组
        if (groups.hour.length > 0) {
            html += '<div class="timeframe-group">';
            const hoursTitle = hasTranslateFunc ? window.t('小时') : '小时';
            html += `<div class="timeframe-group-header">${hoursTitle}</div>`;
            html += '<ul class="pair-list timeframe-list">';
            groups.hour.forEach(item => {
                const isActive = item.value === currentTimeframe ? 'selected' : '';
                const itemText = hasTranslateFunc ? window.t(item.text) : item.text;
                html += `<li class="pair-list-item timeframe-item ${isActive}" data-timeframe="${item.value}">
                    <span class="timeframe-icon">${item.icon}</span>
                    <div class="pair-info">
                        <span class="timeframe-text">${itemText}</span>
                    </div>
                </li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        // 天和周组
        if (groups.day.length > 0 || groups.week.length > 0) {
            html += '<div class="timeframe-group">';
            const dayWeekTitle = hasTranslateFunc ? window.t('天/周') : '天/周';
            html += `<div class="timeframe-group-header">${dayWeekTitle}</div>`;
            html += '<ul class="pair-list timeframe-list">';
            [...groups.day, ...groups.week].forEach(item => {
                const isActive = item.value === currentTimeframe ? 'selected' : '';
                const itemText = hasTranslateFunc ? window.t(item.text) : item.text;
                html += `<li class="pair-list-item timeframe-item ${isActive}" data-timeframe="${item.value}">
                    <span class="timeframe-icon">${item.icon}</span>
                    <div class="pair-info">
                        <span class="timeframe-text">${itemText}</span>
                    </div>
                </li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        // 月组
        if (groups.month.length > 0) {
            html += '<div class="timeframe-group">';
            const monthTitle = hasTranslateFunc ? window.t('月') : '月';
            html += `<div class="timeframe-group-header">${monthTitle}</div>`;
            html += '<ul class="pair-list timeframe-list">';
            groups.month.forEach(item => {
                const isActive = item.value === currentTimeframe ? 'selected' : '';
                const itemText = hasTranslateFunc ? window.t(item.text) : item.text;
                html += `<li class="pair-list-item timeframe-item ${isActive}" data-timeframe="${item.value}">
                    <span class="timeframe-icon">${item.icon}</span>
                    <div class="pair-info">
                        <span class="timeframe-text">${itemText}</span>
                    </div>
                </li>`;
            });
            html += '</ul>';
            html += '</div>';
        }
        
        html += '</div>';
        
        timeframeListContainer.innerHTML = html;
        
        // 绑定点击事件
        const items = timeframeListContainer.querySelectorAll('.timeframe-item');
        items.forEach(item => {
            item.addEventListener('click', function() {
                items.forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
                
                const timeframe = item.getAttribute('data-timeframe');
                setTimeframeBtnText(timeframe);
                
                // 加载选定时间周期的数据
                const currentSymbol = openPairModalBtn ? openPairModalBtn.textContent : 'BTC/USDT';
                if (window.loadMarketDataByTimeframe) {
                    window.loadMarketDataByTimeframe(currentSymbol, null, timeframe);
                } else if (window.loadMarketDataBySymbol) {
                    // 兼容现有方法，将timeframe作为第三个参数传递
                    const market = 'Binance';  // 默认使用Binance
                    window.loadMarketDataBySymbol(currentSymbol, market, timeframe);
                } else {
                    console.log('选择时间周期:', timeframe);
                }
                
                timeframeModal.style.display = 'none';
            });
        });
    }
    
    // 打开时间周期模态框
    if (openTimeframeModalBtn && timeframeModal) {
        openTimeframeModalBtn.addEventListener('click', function() {
            renderTimeframeList();
            timeframeModal.style.display = 'flex';
        });
    }
    
    // 关闭时间周期模态框
    if (closeTimeframeModalBtn && timeframeModal) {
        closeTimeframeModalBtn.addEventListener('click', function() {
            timeframeModal.style.display = 'none';
        });
    }
    
    // 点击遮罩关闭时间周期模态框
    if (timeframeModal) {
        timeframeModal.addEventListener('click', function(e) {
            if (e.target === timeframeModal) {
                timeframeModal.style.display = 'none';
            }
        });
    }
    
    // 页面加载时设置默认时间周期
    setTimeframeBtnText(currentTimeframe);
});