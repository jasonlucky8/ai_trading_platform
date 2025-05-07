from typing import Dict, List
import ccxt
from .base_provider import BaseExchangeProvider

class OKXProvider(BaseExchangeProvider):
    """OKX交易所数据提供者"""
    
    def __init__(self):
        self.exchange = ccxt.okx({
            'enableRateLimit': True,
            'timeout': 30000
        })
        
    def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        start_time: int = None,
        end_time: int = None
    ) -> List[Dict]:
        """获取OKX历史K线数据"""
        return self.exchange.fetch_ohlcv(
            symbol,
            timeframe,
            since=start_time,
            limit=1000
        )
        
    def get_realtime_data(self, symbol: str) -> Dict:
        """获取OKX实时行情数据"""
        return self.exchange.fetch_ticker(symbol)
        
    def get_exchange_info(self) -> Dict:
        """获取OKX交易所信息"""
        return self.exchange.load_markets()
