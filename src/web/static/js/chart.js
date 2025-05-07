/**
 * K线图表实现
 * 基于LightweightCharts提供专业交易视图
 */

// 全局变量
let chart = null;
let candleSeries = null;

/**
 * 初始化图表
 */
function initChart() {
    // 获取图表容器
    const chartContainer = document.getElementById('chart');
    if (!chartContainer) return;
    
    // 清除旧图表
    if (chart) {
        chart.remove();
        chart = null;
    }
    
    // 创建新图表
    chart = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
            backgroundColor: '#131722',
            textColor: '#000000',
        },
        grid: {
            vertLines: { color: '#f7f7f7' },
            horzLines: { color: '#f7f7f7' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'transparent',
            borderVisible: false,
            scaleMargins: { top: 0.05, bottom: 0.1 },
            textColor: '#000000',
        },
        timeScale: {
            borderColor: 'transparent',
            borderVisible: false,
            timeVisible: true,
            fixLeftEdge: true,
            fixRightEdge: true,
            scaleMargins: { right: 0.02, left: 0.02 },
            textColor: '#000000',
        },
    });
    
    // 创建K线系列
    candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderUpColor: '#26a69a',
        borderDownColor: '#ef5350',
        wickUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        priceScaleId: 'right',
        scaleMargins: { top: 0.05, bottom: 0.1 },
    });
    
    // 窗口调整大小时重绘图表
    window.addEventListener('resize', debounce(resizeChart, 250));
    
    // 监听拖拽结束自定义事件
    document.addEventListener('dragResizeEnd', debounce(resizeChart, 100));
    
    // 使用MutationObserver监听容器大小变化
    const resizeObserver = new ResizeObserver(debounce(() => {
        resizeChart();
    }, 100));
    resizeObserver.observe(chartContainer);
    
    return chart;
}

/**
 * 调整图表大小
 */
function resizeChart() {
    if (!chart) return;
    const chartContainer = document.getElementById('chart');
    if (!chartContainer) return;
    
    chart.applyOptions({
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
    });
    
    if (chart.timeScale()) {
        chart.timeScale().fitContent();
    }
}

/**
 * 加载市场数据
 * @param {string} symbol - 交易对 (例如: "BTC/USDT")
 * @param {string} market - 市场 (例如: "Binance")
 * @param {string} timeframe - 时间周期 (例如: "1h", "4h", "1d")
 */
function loadMarketDataBySymbol(symbol, market = 'Binance', timeframe = '1h') {
    if (!chart || !candleSeries) {
        initChart();
    }
    
    const exchange = market.toLowerCase();
    const limit = 500;
    
    // 更新UI元素
    updateUIElements(symbol, timeframe);
    
    // 显示加载状态
    showLoading(true);
    
    // 使用后端API获取真实交易所数据
    fetch(`/api/marketdata?exchanges=${exchange}&symbol=${symbol}&timeframe=${timeframe}&limit=${limit}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(`交易所数据错误: ${data.error}`);
            }
            
            if (!data.data || data.data.length === 0) {
                throw new Error('未获取到交易数据');
            }
            
            console.log(`成功从${exchange}获取${symbol}的${timeframe}数据，数据点数: ${data.data.length}`);
            renderChartData(data.data);
        })
        .catch(error => {
            console.error('加载数据失败:', error);
            alert(`无法获取${market}的${symbol}(${timeframe})数据，请检查网络连接或选择其他交易对。`);
            // 不再自动切换到模拟数据
        })
        .finally(() => {
            showLoading(false);
        });
}

/**
 * 更新UI元素
 * @param {string} symbol - 交易对
 * @param {string} timeframe - 时间周期
 */
function updateUIElements(symbol, timeframe = '1h') {
    // 更新页面标题
    document.title = `${symbol} | AI交易平台`;
    
    // 更新选择币对按钮文本
    const pairBtn = document.getElementById('openPairModalBtn');
    if (pairBtn) pairBtn.textContent = symbol;
    
    // 更新时间周期按钮文本
    const timeframeBtn = document.getElementById('openTimeframeModalBtn');
    if (timeframeBtn) {
        // 找到对应的时间周期显示文本
        let timeframeText = timeframe;
        if (window.timeframeListData) {
            const item = window.timeframeListData.find(item => item.value === timeframe);
            if (item) timeframeText = item.text;
        } else {
            // 简单转换
            switch(timeframe) {
                case '5m': timeframeText = '5分钟'; break;
                case '10m': timeframeText = '10分钟'; break;
                case '15m': timeframeText = '15分钟'; break;
                case '30m': timeframeText = '30分钟'; break;
                case '45m': timeframeText = '45分钟'; break;
                case '1h': timeframeText = '1小时'; break;
                case '2h': timeframeText = '2小时'; break;
                case '4h': timeframeText = '4小时'; break;
                case '1d': timeframeText = '1日'; break;
                case '1w': timeframeText = '1周'; break;
                case '1M': timeframeText = '1月'; break;
            }
        }
        timeframeBtn.textContent = timeframeText;
    }
    
    // 更新右侧面板信息
    const pairElement = document.querySelector('.coin-pair-main');
    if (pairElement) pairElement.textContent = symbol.replace('/', '');
}

/**
 * 渲染图表数据
 */
function renderChartData(data) {
    if (!candleSeries || !data || !Array.isArray(data) || data.length === 0) return;
    
    // 格式化数据
    const formattedData = data.map(item => {
        // 判断时间格式：如果是数字（UTC时间戳），则直接处理；如果是字符串，则转换
        const timeValue = typeof item.time === 'number' 
            ? item.time / 1000  // 将毫秒转为秒
            : convertTimeToTimestamp(item.time);
            
        return {
            time: timeValue,
            open: parseFloat(item.open),
            high: parseFloat(item.high),
            low: parseFloat(item.low),
            close: parseFloat(item.close)
        };
    }).filter(item => !isNaN(item.open) && !isNaN(item.high) && 
                      !isNaN(item.low) && !isNaN(item.close));
    
    console.log('第一个数据点:', formattedData[0]);
    
    // 设置数据
    candleSeries.setData(formattedData);
    
    // 更新最新价格
    if (formattedData.length > 0) {
        updatePriceInfo(formattedData[formattedData.length - 1]);
    }
    
    // 使整个数据范围可见，并提供适当的边距
    if (chart && chart.timeScale()) {
        chart.timeScale().fitContent();
        
        // 添加适当的可见边距
        setTimeout(() => {
            chart.applyOptions({
                timeScale: {
                    rightOffset: 12,  // 右侧留出空间
                    barSpacing: 6,    // 蜡烛图间距
                }
            });
        }, 100);
    }
}

/**
 * 更新价格信息
 */
function updatePriceInfo(lastCandle) {
    if (!lastCandle) return;
    
    // 计算涨跌幅
    const change = lastCandle.close - lastCandle.open;
    const changePercent = (change / lastCandle.open * 100).toFixed(2);
    
    // 更新价格显示
    const priceElement = document.querySelector('.coin-price-main');
    if (priceElement) priceElement.textContent = lastCandle.close.toFixed(2);
    
    // 更新涨跌幅
    const changeElement = document.querySelector('.coin-change-main');
    if (changeElement) {
        const sign = change >= 0 ? '+' : '';
        changeElement.textContent = `${sign}${changePercent}%`;
        changeElement.className = `coin-change-main ${change >= 0 ? 'up' : 'down'}`;
    }
}

/**
 * 转换时间为时间戳
 */
function convertTimeToTimestamp(timeStr) {
    if (!timeStr) return Math.floor(Date.now() / 1000);
    
    try {
        // 确保使用UTC时间解析
        if (typeof timeStr === 'string') {
            // 处理标准ISO格式
            if (timeStr.includes('T') && timeStr.includes('Z')) {
                const date = new Date(timeStr);
                return Math.floor(date.getTime() / 1000);
            }
            // 处理其他日期格式，明确指定为UTC
            const parts = timeStr.split(/[- :]/);
            if (parts.length >= 3) {
                // 年月日
                const year = parseInt(parts[0], 10);
                const month = parseInt(parts[1], 10) - 1; // 月份从0开始
                const day = parseInt(parts[2], 10);
                
                // 时分秒
                const hour = parts.length > 3 ? parseInt(parts[3], 10) : 0;
                const minute = parts.length > 4 ? parseInt(parts[4], 10) : 0;
                const second = parts.length > 5 ? parseInt(parts[5], 10) : 0;
                
                // 使用UTC构造Date对象
                const date = new Date(Date.UTC(year, month, day, hour, minute, second));
                return Math.floor(date.getTime() / 1000);
            }
        } else if (typeof timeStr === 'number') {
            // 如果已经是数字，检查是否为毫秒级时间戳
            return timeStr > 10000000000 ? Math.floor(timeStr / 1000) : timeStr;
        }
        
        // 兜底方案：尝试直接解析
        const date = new Date(timeStr);
        return Math.floor(date.getTime() / 1000);
    } catch (e) {
        console.error('时间转换错误:', e, timeStr);
        return Math.floor(Date.now() / 1000);
    }
}

/**
 * 生成模拟数据
 */
function generateDemoData(symbol) {
    const data = [];
    const now = new Date();
    
    // 基于实际市场的起始价格
    let basePrice;
    if (symbol.includes('BTC')) {
        basePrice = 51200;  // BTC当前价格范围
    } else if (symbol.includes('ETH')) {
        basePrice = 2450;   // ETH当前价格范围
    } else if (symbol.includes('SOL')) {
        basePrice = 145;    // SOL当前价格范围
    } else if (symbol.includes('XRP')) {
        basePrice = 0.52;   // XRP当前价格范围
    } else {
        basePrice = 100;    // 默认价格
    }
    
    let price = basePrice * (0.95 + Math.random() * 0.1); // 起始价格在基准价格±5%范围内随机
    
    // 生成近似真实的历史数据
    for (let i = 0; i < 500; i++) {
        // 每个小时数据
        const time = new Date(now.getTime() - (500 - i) * 60 * 60 * 1000);
        
        // 模拟真实市场波动 - 大部分时间小幅波动，偶尔有较大波动
        const volatilityFactor = Math.random() < 0.1 ? 0.03 : 0.01; // 10%概率有较大波动
        const trendBias = Math.random() < 0.55 ? 0.0005 : -0.0005;  // 轻微上涨趋势偏向
        const change = ((Math.random() - 0.5 + trendBias) * price * volatilityFactor);
        
        const open = price;
        const close = Math.max(0.1, open + change); // 确保价格为正
        
        // 生成合理的高低点
        const rangeMultiplier = volatilityFactor * (0.5 + Math.random());
        const high = Math.max(open, close) * (1 + rangeMultiplier * Math.random());
        const low = Math.min(open, close) * (1 - rangeMultiplier * Math.random());
        
        // 成交量与价格变化成正比
        const volume = Math.abs(change) * basePrice * (5 + Math.random() * 15);
        
        data.push({
            time: time.toISOString(),
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume: parseFloat(volume.toFixed(2))
        });
        
        price = close; // 下一个周期的开盘价等于当前周期的收盘价
    }
    
    return data;
}

/**
 * 显示/隐藏加载状态
 */
function showLoading(show) {
    const chartContainer = document.getElementById('chart');
    if (!chartContainer) return;
    
    let loader = document.getElementById('chart-loader');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'chart-loader';
            loader.innerHTML = '<div class="loader-spinner"></div>';
            loader.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(19,23,34,0.7);display:flex;align-items:center;justify-content:center;z-index:10;';
            
            const spinner = loader.querySelector('.loader-spinner');
            spinner.style.cssText = 'width:40px;height:40px;border:3px solid rgba(255,255,255,0.2);border-top-color:#2962FF;border-radius:50%;animation:spin 1s linear infinite;';
            
            const style = document.createElement('style');
            style.textContent = '@keyframes spin{to{transform:rotate(360deg)}}';
            document.head.appendChild(style);
            
            chartContainer.appendChild(loader);
        } else {
            loader.style.display = 'flex';
        }
    } else if (loader) {
        loader.style.display = 'none';
    }
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表
    initChart();
    
    // 加载默认数据
    loadMarketDataBySymbol('BTC/USDT', 'Binance', '1h');
});

// 暴露函数和数据到全局
window.loadMarketDataBySymbol = loadMarketDataBySymbol;
window.resizeChart = resizeChart;

// 时间周期数据，供布局脚本使用
window.timeframeListData = [
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