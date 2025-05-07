"""
市场数据提供者抽象基类
定义所有数据提供者必须实现的接口
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any


class DataProvider(ABC):
    """
    数据提供者抽象基类，定义获取市场数据的通用接口
    
    所有具体的数据提供者（交易所API、CSV文件、数据库等）都应该继承此类
    并实现其抽象方法
    """
    
    @abstractmethod
    def get_historical_data(self, 
                          symbol: str, 
                          timeframe: str, 
                          since: Optional[int] = None, 
                          limit: Optional[int] = None, 
                          **kwargs) -> pd.DataFrame:
        """
        获取历史市场数据
        
        Args:
            symbol: 交易对符号，例如 'BTC/USDT'
            timeframe: 时间周期，例如 '1m', '5m', '1h', '1d'
            since: 开始时间戳（毫秒）
            limit: 返回的最大数据条数
            **kwargs: 额外参数
            
        Returns:
            包含OHLCV数据的DataFrame，索引为时间戳，列为['open', 'high', 'low', 'close', 'volume']
        """
        pass
    
    @abstractmethod
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        获取最新价格
        
        Args:
            symbol: 交易对符号，例如 'BTC/USDT'
            
        Returns:
            包含最新价格信息的字典
        """
        pass 