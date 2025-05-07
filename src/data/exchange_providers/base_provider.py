from abc import ABC, abstractmethod
from typing import Dict, List

class BaseExchangeProvider(ABC):
    """交易所数据提供者基类"""
    
    @abstractmethod
    def get_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_time: int = None, 
        end_time: int = None
    ) -> List[Dict]:
        """获取历史K线数据"""
        pass
        
    @abstractmethod
    def get_realtime_data(self, symbol: str) -> Dict:
        """获取实时行情数据"""
        pass
        
    @abstractmethod
    def get_exchange_info(self) -> Dict:
        """获取交易所信息"""
        pass
