from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Optional, Union


class DataProvider(ABC):
    """
    数据提供者接口，用于从不同数据源获取市场数据
    """

    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: str, since: Union[str, int], limit: Optional[int] = None) -> pd.DataFrame:
        """
        获取历史市场数据
        
        参数:
            symbol: 交易对符号，如'BTC/USDT'
            timeframe: 时间帧，如'1m', '1h', '1d'
            since: 起始时间，可以是ISO 8601日期字符串或毫秒级时间戳
            limit: 数据点数量限制
            
        返回:
            DataFrame: 包含市场数据的DataFrame，通常包含以下列：
                      - timestamp: 时间戳
                      - open: 开盘价
                      - high: 最高价
                      - low: 最低价
                      - close: 收盘价
                      - volume: 交易量
        """
        pass
    
    @abstractmethod
    def get_live_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        获取实时市场数据
        
        参数:
            symbol: 交易对符号
            timeframe: 时间帧
            
        返回:
            DataFrame: 包含最新市场数据的DataFrame
        """
        pass
    
    @abstractmethod
    def get_orderbook(self, symbol: str, limit: Optional[int] = None) -> Dict:
        """
        获取订单簿数据
        
        参数:
            symbol: 交易对符号
            limit: 订单数量限制
            
        返回:
            Dict: 包含买单和卖单的字典，格式如：
                 {
                     'bids': [[price, amount], ...],  # 买单
                     'asks': [[price, amount], ...],  # 卖单
                     'timestamp': timestamp,          # 时间戳
                     'datetime': datetime,            # ISO 8601 格式的日期时间
                     'nonce': nonce                   # 序列号（如有）
                 }
        """
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict:
        """
        获取交易对当前行情摘要
        
        参数:
            symbol: 交易对符号
            
        返回:
            Dict: 包含行情摘要的字典，格式如：
                 {
                     'symbol': symbol,                # 交易对符号
                     'timestamp': timestamp,          # 时间戳
                     'datetime': datetime,            # ISO 8601 格式的日期时间
                     'high': high,                    # 24小时最高价
                     'low': low,                      # 24小时最低价
                     'bid': bid,                      # 当前最高买价
                     'ask': ask,                      # 当前最低卖价
                     'last': last,                    # 最新成交价
                     'close': close,                  # 同最新成交价
                     'previousClose': previousClose,  # 前一日收盘价
                     'change': change,                # 价格变动
                     'percentage': percentage,        # 价格变动百分比
                     'average': average,              # 平均价格
                     'baseVolume': baseVolume,        # 基础货币交易量
                     'quoteVolume': quoteVolume       # 报价货币交易量
                 }
        """
        pass
    
    @abstractmethod
    def get_symbols(self) -> list:
        """
        获取支持的交易对列表
        
        返回:
            List[str]: 支持的交易对符号列表
        """
        pass 