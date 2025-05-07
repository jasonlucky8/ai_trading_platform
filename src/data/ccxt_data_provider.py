"""
基于CCXT的交易所数据提供者

使用CCXT库连接各大交易所，获取市场数据
"""

import ccxt # 导入ccxt库
import pandas as pd
import numpy as np
from typing import Dict, Optional, Union, List, Any
import time
from datetime import datetime, timedelta
import logging

from src.data.data_provider import DataProvider

logger = logging.getLogger(__name__)


class CCXTDataProvider(DataProvider):
    """
    基于CCXT库的数据提供者，支持多家交易所
    
    注意：实际环境中需要安装ccxt并真实调用API
    但在开发阶段，我们使用模拟数据进行测试
    """

    def __init__(self, exchange: str = 'binance', **kwargs):
        """
        初始化CCXT数据提供者
        
        Args:
            exchange: 交易所名称，例如 'binance', 'okex'
            **kwargs: 传递给ccxt交易所实例的其他参数
        """
        self.exchange_id = exchange
        self.exchange_params = kwargs
        try:
            # 初始化CCXT交易所实例
            exchange_class = getattr(ccxt, exchange)
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'timeout': 30000,
                **kwargs
            })
            logger.info(f"已成功连接到{exchange}交易所")
        except Exception as e:
            logger.error(f"连接到{exchange}交易所失败: {str(e)}")
            self.exchange = None
        
    def get_historical_data(self, 
                          symbol: str, 
                          timeframe: str, 
                          since: Optional[int] = None, 
                          limit: Optional[int] = 200, 
                          **kwargs) -> pd.DataFrame:
        """
        获取历史K线数据
        
        Args:
            symbol: 交易对符号，例如 'BTC/USDT'
            timeframe: 时间周期，例如 '1m', '5m', '1h', '1d'
            since: 开始时间戳（毫秒）
            limit: 返回的最大数据条数
            **kwargs: 额外参数
            
        Returns:
            包含OHLCV数据的DataFrame，索引为时间戳，列为['open', 'high', 'low', 'close', 'volume']
        """
        logger.info(f"获取{self.exchange_id}交易所的{symbol} {timeframe}数据，数量: {limit}")
        
        try:
            if not self.exchange:
                raise Exception("交易所实例未初始化成功")
            
            # 调用CCXT API获取数据
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            # 转换为DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            # 将时间戳转换为UTC日期时间对象
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"成功获取到{len(df)}条数据")
            return df
            
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")
            # 获取失败时，使用模拟数据作为回退方案
            logger.warning("使用模拟数据作为回退")
            return self._generate_mock_data(symbol, timeframe, since, limit)
    
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        获取最新价格
        
        Args:
            symbol: 交易对符号，例如 'BTC/USDT'
            
        Returns:
            包含最新价格信息的字典
        """
        try:
            if not self.exchange:
                raise Exception("交易所实例未初始化成功")
                
            # 调用CCXT API获取最新价格
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"获取最新价格失败: {str(e)}")
            # 获取失败时，使用模拟数据作为回退方案
            return self._generate_mock_ticker(symbol)
    
    def _generate_mock_ticker(self, symbol: str) -> Dict[str, Any]:
        """生成模拟价格数据作为回退"""
        base, quote = symbol.split('/')
        
        # 根据不同币种生成接近真实的价格
        if base == 'BTC':
            mock_price = 51200 + np.random.normal(0, 500)
        elif base == 'ETH':
            mock_price = 2450 + np.random.normal(0, 50)
        elif base == 'SOL':
            mock_price = 145 + np.random.normal(0, 5)
        else:
            mock_price = 100 + np.random.normal(0, 10)
        
        return {
            'symbol': symbol,
            'last': mock_price,
            'bid': mock_price - 5,
            'ask': mock_price + 5,
            'high': mock_price + 1000,
            'low': mock_price - 1000,
            'volume': np.random.uniform(1000, 5000),
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
    
    def _generate_mock_data(self, 
                          symbol: str, 
                          timeframe: str, 
                          since: Optional[int] = None,
                          limit: Optional[int] = 200) -> pd.DataFrame:
        """
        生成模拟市场数据用于开发测试
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            since: 开始时间戳（毫秒）
            limit: 数据条数
            
        Returns:
            模拟的市场数据DataFrame
        """
        # 解析交易对
        base, quote = symbol.split('/')
        
        # 确定时间间隔（秒）
        tf_seconds = self._timeframe_to_seconds(timeframe)
        
        # 确定起始时间
        if since is None:
            # 默认从30天前开始
            end_time = datetime.now(pd.UTC)  # 使用UTC时间
            start_time = end_time - timedelta(seconds=tf_seconds * limit)
        else:
            # 使用指定的起始时间
            start_time = datetime.fromtimestamp(since / 1000, tz=pd.UTC)
            end_time = start_time + timedelta(seconds=tf_seconds * limit)
        
        # 生成时间序列
        date_range = pd.date_range(start=start_time, end=end_time, periods=limit, tz=pd.UTC)
        
        # 确定基准价格（根据货币对不同设置不同基准价格）
        if base == 'BTC':
            base_price = 29000
        elif base == 'ETH':
            base_price = 1800
        else:
            base_price = 100
        
        # 使用随机游走生成价格序列
        np.random.seed(42)  # 设置随机种子，确保可重复性
        
        # 生成随机价格变动
        price_changes = np.random.normal(0, base_price * 0.01, limit)
        
        # 计算价格序列
        close_prices = base_price + np.cumsum(price_changes)
        close_prices = np.maximum(1, close_prices)  # 确保价格为正
        
        # 生成其他价格数据
        high_prices = close_prices * (1 + np.random.uniform(0, 0.03, limit))
        low_prices = close_prices * (1 - np.random.uniform(0, 0.03, limit))
        open_prices = close_prices * (1 + np.random.uniform(-0.02, 0.02, limit))
        
        # 确保开高低收的逻辑关系正确
        for i in range(limit):
            max_val = max(open_prices[i], close_prices[i])
            min_val = min(open_prices[i], close_prices[i])
            high_prices[i] = max(high_prices[i], max_val)
            low_prices[i] = min(low_prices[i], min_val)
        
        # 生成成交量
        volumes = np.random.uniform(base_price * 10, base_price * 50, limit)
        
        # 创建DataFrame
        df = pd.DataFrame({
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        }, index=date_range)
        
        return df
    
    def _timeframe_to_seconds(self, timeframe: str) -> int:
        """
        将时间周期字符串转换为对应的秒数
        
        Args:
            timeframe: 时间周期字符串，例如 '1m', '5m', '1h', '1d'
            
        Returns:
            对应的秒数
        """
        unit = timeframe[-1]
        value = int(timeframe[:-1])
        
        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 60 * 60
        elif unit == 'd':
            return value * 24 * 60 * 60
        elif unit == 'w':
            return value * 7 * 24 * 60 * 60
        else:
            raise ValueError(f"不支持的时间周期单位: {unit}")
    
    def get_live_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        获取实时数据（模拟实现）
        
        Args:
            symbol: 交易对符号
            timeframe: 时间周期
            
        Returns:
            最新的市场数据
        """
        # 在开发阶段，我们简单返回一小段历史数据作为"实时"数据
        return self._generate_mock_data(symbol, timeframe, limit=10)
    
    def get_orderbook(self, symbol: str, limit: Optional[int] = None) -> Dict:
        """
        获取订单簿数据（模拟实现）
        
        Args:
            symbol: 交易对符号
            limit: 返回的订单条数
            
        Returns:
            订单簿数据字典
        """
        # 在开发阶段使用模拟数据
        base_price = 29000
        
        # 生成模拟买单
        bids = []
        for i in range(20):
            price = base_price * (1 - 0.001 * i)
            size = np.random.uniform(0.1, 2.0)
            bids.append([price, size])
        
        # 生成模拟卖单
        asks = []
        for i in range(20):
            price = base_price * (1 + 0.001 * i)
            size = np.random.uniform(0.1, 2.0)
            asks.append([price, size])
        
        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'datetime': datetime.now().isoformat()
        }
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        获取ticker数据（模拟实现）
        
        Args:
            symbol: 交易对符号
            
        Returns:
            ticker数据字典
        """
        # 在开发阶段使用模拟数据
        return self.get_latest_price(symbol)
    
    def get_exchange_info(self) -> Dict:
        """
        获取交易所信息（模拟实现）
        
        Returns:
            交易所信息字典
        """
        return {
            'name': self.exchange_id,
            'timeframes': {
                '1m': '1分钟',
                '5m': '5分钟',
                '15m': '15分钟',
                '30m': '30分钟',
                '1h': '1小时',
                '2h': '2小时',
                '4h': '4小时',
                '1d': '1天',
                '1w': '1周'
            },
            'supported_symbols': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
        }
    
    def get_symbols(self) -> list:
        """
        获取交易所支持的交易对列表（模拟实现）
        
        Returns:
            交易对符号列表
        """
        # 在开发阶段返回模拟的交易对列表
        return [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 
            'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'DOT/USDT',
            'MATIC/USDT', 'LINK/USDT', 'LTC/USDT', 'AVAX/USDT'
        ]
    
    def get_available_symbols(self):
        """获取交易所支持的币值对列表"""
        try:
            # 加载市场
            self.exchange.load_markets()
            # 返回所有可用的交易对
            return list(self.exchange.markets.keys())
        except Exception as e:
            logger.error(f"获取{self.exchange.id}可用币值对失败: {str(e)}")
            return [] 