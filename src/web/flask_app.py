#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于Flask的交易平台Web服务器

支持中英文界面切换。
"""

import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入数据提供者
from src.data.ccxt_data_provider import CCXTDataProvider

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(
    __name__, 
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)

# 设置会话密钥（用于存储用户会话数据）
app.secret_key = 'ai_trading_platform_secret_key'

# 时间帧选项（中英文）
TIMEFRAME_OPTIONS = {
    'zh-CN': {
        "1分钟": "1m",
        "5分钟": "5m",
        "15分钟": "15m",
        "30分钟": "30m",
        "1小时": "1h",
        "2小时": "2h",
        "4小时": "4h",
        "1天": "1d",
        "1周": "1w",
    },
    'en-US': {
        "1 Minute": "1m",
        "5 Minutes": "5m",
        "15 Minutes": "15m",
        "30 Minutes": "30m",
        "1 Hour": "1h",
        "2 Hours": "2h",
        "4 Hours": "4h",
        "1 Day": "1d",
        "1 Week": "1w",
    }
}


@app.route('/')
def index():
    """首页路由"""
    # 获取用户语言偏好，默认为中文
    lang = request.args.get('lang', session.get('lang', 'zh-CN'))
    session['lang'] = lang
    
    # 获取支持的交易所列表
    exchange_options = ["okx", "binance", "huobi", "coinbase"]
    
    # 获取可用的时间帧
    timeframe_options = TIMEFRAME_OPTIONS.get(lang, TIMEFRAME_OPTIONS['zh-CN'])
    
    return render_template(
        'index.html',
        exchange_options=exchange_options,
        timeframe_options=timeframe_options,
        lang=lang
    )


@app.route('/api/switchlang')
def switch_language():
    """切换语言API"""
    lang = request.args.get('lang', 'zh-CN')
    
    # 验证语言是否支持
    if lang not in ['zh-CN', 'en-US']:
        lang = 'zh-CN'
    
    # 保存语言选择到会话
    session['lang'] = lang
    
    # 获取引用URL或默认回到首页
    referrer = request.referrer or url_for('index')
    
    return redirect(referrer)


@app.route('/api/marketdata')
def get_market_data():
    """获取市场数据API"""
    try:
        # 获取请求参数
        exchanges = request.args.get('exchanges', 'okx').split(',')  # 支持多个交易所，用逗号分隔
        symbol = request.args.get('symbol', 'BTC/USDT')
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 200))
        
        logger.info(f"收到市场数据请求: 交易所={exchanges}, 交易对={symbol}, 时间帧={timeframe}, 数据点数={limit}")
        
        # 设置起始时间（默认30天前）
        since = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        
        # 获取多个交易所的数据
        all_data = []
        for exchange in exchanges:
            try:
                data_provider = CCXTDataProvider(exchange=exchange.strip())
                logger.info(f"尝试从{exchange}获取{symbol}的{timeframe}数据")
                
                data = data_provider.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=limit
                )
                
                if isinstance(data, pd.DataFrame):
                    data['exchange'] = exchange
                    all_data.append(data)
                else:
                    logger.warning(f"从{exchange}获取的数据格式不正确")
            except Exception as e:
                logger.error(f"从{exchange}获取数据失败: {str(e)}", exc_info=True)
                continue
        
        if not all_data:
            return jsonify({'error': '无法从任何交易所获取数据'})
        
        # 转换数据为JSON格式
        data_json = []
        for df in all_data:
            exchange = df['exchange'].iloc[0]
            for idx, row in df.iterrows():
                # 使用UTC时间戳，不进行本地时区转换
                timestamp_utc = int(idx.timestamp() * 1000)  # 毫秒级UTC时间戳
                data_json.append({
                    'exchange': exchange,
                    'time': timestamp_utc,  # 使用数字时间戳而不是字符串
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume'])
                })
        
        # 返回JSON响应
        resp = {
            'symbol': symbol,
            'timeframe': timeframe,
            'exchanges': exchanges,
            'data': data_json
        }
        logger.info(f"返回数据成功，总数据点数: {len(data_json)}")
        
        return jsonify(resp)
    
    except Exception as e:
        logger.error(f"获取市场数据错误: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)})


@app.route('/api/indicators', methods=['GET', 'POST'])
def calculate_indicators():
    """计算技术指标API"""
    return jsonify({'error': '技术指标功能已被移除'}), 400


@app.route('/api/available_pairs')
def get_available_pairs():
    """获取可用的币值对列表"""
    try:
        # 常用币值对列表
        common_pairs = [
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT", "DOT/USDT",
            "XRP/USDT", "SOL/USDT", "DOGE/USDT", "AVAX/USDT", "MATIC/USDT"
        ]
        
        # 获取每个交易所支持的币值对
        exchange_pairs = {}
        exchanges = ["okx", "binance", "huobi"]
        
        for exchange in exchanges:
            try:
                data_provider = CCXTDataProvider(exchange=exchange)
                # 获取交易所支持的币值对
                available_pairs = data_provider.get_symbols()
                # 过滤出常用币值对
                supported_pairs = [pair for pair in common_pairs if pair in available_pairs]
                exchange_pairs[exchange] = supported_pairs
                
            except Exception as e:
                logger.error(f"获取{exchange}可用币值对失败: {str(e)}")
                exchange_pairs[exchange] = []
        
        return jsonify(exchange_pairs)
        
    except Exception as e:
        logger.error(f"获取可用币值对失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # 确保目录存在
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)