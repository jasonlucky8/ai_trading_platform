import ccxt
import pandas as pd
from typing import Dict, Optional, Union, List
import time
from datetime import datetime
import logging

from src.data.data_provider import DataProvider

logger = logging.getLogger(__name__)


class CCXTDataProvider(DataProvider):
    """
    使用CCXT库实现的数据提供者，用于从加密货币交易所获取市场数据
    """

    def __init__(self, exchange: str, api_key: str = None, api_secret: str = None, params: Dict = None):
        """
        初始化CCXT数据提供者
        
        参数:
            exchange: 交易所名称，如'binance', 'coinbase', 'huobi'等
            api_key: API密钥（可选）
            api_secret: API密钥对应的密码（可选）
            params: 其他参数，如{'enableRateLimit': True}
        """
        self.exchange_name = exchange
        
        # 设置默认参数
        self.params = {
            'enableRateLimit': True,
            'timeout': 30000
        }
        
        # 更新自定义参数
        if params:
            self.params.update(params)
        
        # 创建交易所实例
        try:
            exchange_class = getattr(ccxt, exchange)
            self.exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                **self.params
            })
            logger.info(f"成功初始化 {exchange} 交易所连接")
        except Exception as e:
            logger.error(f"初始化 {exchange} 交易所失败: {str(e)}")
            raise
    
    def get_historical_data(self, symbol: str, timeframe: str, since: Union[str, int], limit: Optional[int] = None) -> pd.DataFrame:
        """
        获取历史市场数据
        
        参数:
            symbol: 交易对符号，如'BTC/USDT'
            timeframe: 时间帧，如'1m', '1h', '1d'
            since: 起始时间，可以是ISO 8601日期字符串或毫秒级时间戳
            limit: 数据点数量限制
            
        返回:
            DataFrame: 包含市场数据的DataFrame
        """
        try:
            # 确保交易所支持获取历史数据
            if not self.exchange.has['fetchOHLCV']:
                raise Exception(f"{self.exchange_name} 不支持获取历史OHLCV数据")
            
            # 如果since是字符串日期，转换为时间戳
            if isinstance(since, str):
                since = int(datetime.fromisoformat(since.replace('Z', '+00:00')).timestamp() * 1000)
            
            # 获取数据
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 转换时间戳列为datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # 设置索引
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            logger.error(f"获取历史数据失败: {str(e)}")
            raise
    
    def get_live_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        获取实时市场数据
        
        参数:
            symbol: 交易对符号
            timeframe: 时间帧
            
        返回:
            DataFrame: 包含最新市场数据的DataFrame
        """
        try:
            # 获取最新数据（通常取最近的一些数据点）
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=1)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 转换时间戳列为datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # 设置索引
            df.set_index('timestamp', inplace=True)
            
            return df
        
        except Exception as e:
            logger.error(f"获取实时数据失败: {str(e)}")
            raise
    
    def get_orderbook(self, symbol: str, limit: Optional[int] = None) -> Dict:
        """
        获取订单簿数据
        
        参数:
            symbol: 交易对符号
            limit: 订单数量限制
            
        返回:
            Dict: 包含买单和卖单的字典
        """
        try:
            # 确保交易所支持获取订单簿
            if not self.exchange.has['fetchOrderBook']:
                raise Exception(f"{self.exchange_name} 不支持获取订单簿")
            
            # 获取订单簿
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            
            return orderbook
        
        except Exception as e:
            logger.error(f"获取订单簿失败: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        获取交易对当前行情摘要
        
        参数:
            symbol: 交易对符号
            
        返回:
            Dict: 包含行情摘要的字典
        """
        try:
            # 确保交易所支持获取ticker
            if not self.exchange.has['fetchTicker']:
                raise Exception(f"{self.exchange_name} 不支持获取ticker")
            
            # 获取ticker
            ticker = self.exchange.fetch_ticker(symbol)
            
            return ticker
        
        except Exception as e:
            logger.error(f"获取ticker失败: {str(e)}")
            raise
    
    def get_symbols(self) -> List[str]:
        """
        获取支持的交易对列表
        
        返回:
            List[str]: 支持的交易对符号列表
        """
        try:
            # 加载市场
            self.exchange.load_markets()
            
            # 获取所有交易对符号
            symbols = list(self.exchange.markets.keys())
            
            return symbols
        
        except Exception as e:
            logger.error(f"获取交易对列表失败: {str(e)}")
            raise
    
    def get_exchange_info(self) -> Dict:
        """
        获取交易所信息
        
        返回:
            Dict: 包含交易所信息的字典
        """
        return {
            'name': self.exchange_name,
            'has': self.exchange.has,
            'timeframes': self.exchange.timeframes if hasattr(self.exchange, 'timeframes') else None,
            'currencies': list(self.exchange.currencies.keys()) if hasattr(self.exchange, 'currencies') else None
        } 