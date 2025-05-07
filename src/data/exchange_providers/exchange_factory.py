from typing import Optional
from .binance_provider import BinanceProvider
from .okx_provider import OKXProvider
from .base_provider import BaseExchangeProvider

class ExchangeFactory:
    """交易所数据提供者工厂"""
    
    @staticmethod
    def create_provider(exchange_name: str) -> Optional[BaseExchangeProvider]:
        """根据交易所名称创建对应的数据提供者
        
        Args:
            exchange_name: 交易所名称(小写)，如'binance'或'okx'
            
        Returns:
            对应的交易所数据提供者实例，如果交易所不支持则返回None
        """
        exchange_name = exchange_name.lower()
        if exchange_name == 'binance':
            return BinanceProvider()
        elif exchange_name == 'okx':
            return OKXProvider()
        return None
