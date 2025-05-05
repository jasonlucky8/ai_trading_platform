import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union
import logging
import talib
from talib import abstract

logger = logging.getLogger(__name__)


class FeatureEngineering:
    """
    特征工程类，用于计算各种技术指标
    """

    def __init__(self):
        """
        初始化特征工程类
        """
        # 支持的技术指标映射
        self.available_indicators = {
            'sma': self.add_sma,
            'ema': self.add_ema,
            'macd': self.add_macd,
            'rsi': self.add_rsi,
            'bollinger': self.add_bollinger_bands,
            'atr': self.add_atr,
            'adx': self.add_adx,
            'obv': self.add_obv,
            'cci': self.add_cci,
            'stoch': self.add_stochastic,
            'willr': self.add_willr,
            'mom': self.add_momentum,
            'roc': self.add_roc,
            'ppo': self.add_ppo,
            'mfi': self.add_mfi
        }
    
    def add_moving_averages(self, data: pd.DataFrame, windows: List[int] = [5, 10, 20, 50, 200], col: str = 'close', ma_type: str = 'sma') -> pd.DataFrame:
        """
        添加移动平均线
        
        参数:
            data: 市场数据
            windows: 移动平均窗口大小列表
            col: 用于计算移动平均的列名
            ma_type: 移动平均类型，'sma'（简单移动平均）或'ema'（指数移动平均）
            
        返回:
            DataFrame: 添加移动平均线后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        for window in windows:
            if ma_type.lower() == 'sma':
                df[f'sma_{window}'] = talib.SMA(df[col].values, timeperiod=window)
            elif ma_type.lower() == 'ema':
                df[f'ema_{window}'] = talib.EMA(df[col].values, timeperiod=window)
            else:
                raise ValueError(f"不支持的移动平均类型: {ma_type}")
        
        return df
    
    def add_sma(self, data: pd.DataFrame, windows: List[int] = [5, 10, 20, 50, 200], col: str = 'close') -> pd.DataFrame:
        """
        添加简单移动平均线
        
        参数:
            data: 市场数据
            windows: 移动平均窗口大小列表
            col: 用于计算移动平均的列名
            
        返回:
            DataFrame: 添加简单移动平均线后的数据
        """
        return self.add_moving_averages(data, windows, col, 'sma')
    
    def add_ema(self, data: pd.DataFrame, windows: List[int] = [5, 10, 20, 50, 200], col: str = 'close') -> pd.DataFrame:
        """
        添加指数移动平均线
        
        参数:
            data: 市场数据
            windows: 移动平均窗口大小列表
            col: 用于计算移动平均的列名
            
        返回:
            DataFrame: 添加指数移动平均线后的数据
        """
        return self.add_moving_averages(data, windows, col, 'ema')
    
    def add_macd(self, data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, col: str = 'close') -> pd.DataFrame:
        """
        添加MACD指标
        
        参数:
            data: 市场数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            col: 用于计算MACD的列名
            
        返回:
            DataFrame: 添加MACD指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 计算MACD
        macd, macdsignal, macdhist = talib.MACD(
            df[col].values, 
            fastperiod=fast_period, 
            slowperiod=slow_period, 
            signalperiod=signal_period
        )
        
        df['macd'] = macd
        df['macd_signal'] = macdsignal
        df['macd_hist'] = macdhist
        
        return df
    
    def add_rsi(self, data: pd.DataFrame, periods: List[int] = [14], col: str = 'close') -> pd.DataFrame:
        """
        添加RSI指标
        
        参数:
            data: 市场数据
            periods: RSI周期列表
            col: 用于计算RSI的列名
            
        返回:
            DataFrame: 添加RSI指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        for period in periods:
            df[f'rsi_{period}'] = talib.RSI(df[col].values, timeperiod=period)
        
        return df
    
    def add_bollinger_bands(self, data: pd.DataFrame, period: int = 20, nbdevup: float = 2.0, nbdevdn: float = 2.0, col: str = 'close') -> pd.DataFrame:
        """
        添加布林带指标
        
        参数:
            data: 市场数据
            period: 周期
            nbdevup: 上轨标准差倍数
            nbdevdn: 下轨标准差倍数
            col: 用于计算布林带的列名
            
        返回:
            DataFrame: 添加布林带指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 计算布林带
        upper, middle, lower = talib.BBANDS(
            df[col].values, 
            timeperiod=period, 
            nbdevup=nbdevup, 
            nbdevdn=nbdevdn
        )
        
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower
        
        # 添加相对位置指标
        df['bb_width'] = (upper - lower) / middle
        df['bb_position'] = (df[col] - lower) / (upper - lower)
        
        return df
    
    def add_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加平均真实范围(ATR)指标
        
        参数:
            data: 市场数据
            period: 周期
            
        返回:
            DataFrame: 添加ATR指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算ATR
        df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        
        return df
    
    def add_adx(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加平均方向指数(ADX)指标
        
        参数:
            data: 市场数据
            period: 周期
            
        返回:
            DataFrame: 添加ADX指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算ADX
        df['adx'] = talib.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        df['pdi'] = talib.PLUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        df['mdi'] = talib.MINUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        
        return df
    
    def add_obv(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        添加能量潮(OBV)指标
        
        参数:
            data: 市场数据
            
        返回:
            DataFrame: 添加OBV指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算OBV
        df['obv'] = talib.OBV(df['close'].values, df['volume'].values)
        
        return df
    
    def add_cci(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加顺势指标(CCI)
        
        参数:
            data: 市场数据
            period: 周期
            
        返回:
            DataFrame: 添加CCI指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算CCI
        df['cci'] = talib.CCI(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        
        return df
    
    def add_stochastic(self, data: pd.DataFrame, fastk_period: int = 5, slowk_period: int = 3, slowd_period: int = 3) -> pd.DataFrame:
        """
        添加随机指标(KDJ)
        
        参数:
            data: 市场数据
            fastk_period: 快速%K周期
            slowk_period: 慢速%K周期
            slowd_period: 慢速%D周期
            
        返回:
            DataFrame: 添加随机指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算随机指标
        slowk, slowd = talib.STOCH(
            df['high'].values, 
            df['low'].values, 
            df['close'].values, 
            fastk_period=fastk_period, 
            slowk_period=slowk_period, 
            slowk_matype=0, 
            slowd_period=slowd_period, 
            slowd_matype=0
        )
        
        df['slowk'] = slowk
        df['slowd'] = slowd
        
        # 计算J线 (3*K-2*D)
        df['slowj'] = 3 * slowk - 2 * slowd
        
        return df
    
    def add_willr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加威廉指标(%R)
        
        参数:
            data: 市场数据
            period: 周期
            
        返回:
            DataFrame: 添加威廉指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算威廉指标
        df['willr'] = talib.WILLR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
        
        return df
    
    def add_momentum(self, data: pd.DataFrame, period: int = 10, col: str = 'close') -> pd.DataFrame:
        """
        添加动量指标
        
        参数:
            data: 市场数据
            period: 周期
            col: 用于计算动量的列名
            
        返回:
            DataFrame: 添加动量指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 计算动量
        df[f'mom_{period}'] = talib.MOM(df[col].values, timeperiod=period)
        
        return df
    
    def add_roc(self, data: pd.DataFrame, period: int = 10, col: str = 'close') -> pd.DataFrame:
        """
        添加变动率指标(ROC)
        
        参数:
            data: 市场数据
            period: 周期
            col: 用于计算ROC的列名
            
        返回:
            DataFrame: 添加ROC指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 计算ROC
        df[f'roc_{period}'] = talib.ROC(df[col].values, timeperiod=period)
        
        return df
    
    def add_ppo(self, data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, matype: int = 0, col: str = 'close') -> pd.DataFrame:
        """
        添加百分比价格震荡指标(PPO)
        
        参数:
            data: 市场数据
            fast_period: 快线周期
            slow_period: 慢线周期
            matype: 移动平均类型
            col: 用于计算PPO的列名
            
        返回:
            DataFrame: 添加PPO指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 计算PPO
        df['ppo'] = talib.PPO(df[col].values, fastperiod=fast_period, slowperiod=slow_period, matype=matype)
        
        return df
    
    def add_mfi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        添加资金流量指标(MFI)
        
        参数:
            data: 市场数据
            period: 周期
            
        返回:
            DataFrame: 添加MFI指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 确保数据包含必要的列
        required_cols = ['high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据缺少以下列: {missing_cols}")
        
        # 计算MFI
        df['mfi'] = talib.MFI(df['high'].values, df['low'].values, df['close'].values, df['volume'].values, timeperiod=period)
        
        return df
    
    def add_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        添加所有可用技术指标
        
        参数:
            data: 市场数据
            
        返回:
            DataFrame: 添加所有技术指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        try:
            # 添加移动平均线
            df = self.add_sma(df)
            df = self.add_ema(df)
            
            # 添加MACD
            df = self.add_macd(df)
            
            # 添加RSI
            df = self.add_rsi(df)
            
            # 添加布林带
            df = self.add_bollinger_bands(df)
            
            # 添加其他指标
            df = self.add_atr(df)
            df = self.add_adx(df)
            df = self.add_obv(df)
            df = self.add_cci(df)
            df = self.add_stochastic(df)
            df = self.add_willr(df)
            df = self.add_momentum(df)
            df = self.add_roc(df)
            df = self.add_ppo(df)
            df = self.add_mfi(df)
            
            return df
        
        except Exception as e:
            logger.error(f"添加技术指标时出错: {str(e)}")
            raise
    
    def add_features(self, data: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """
        添加指定的技术指标
        
        参数:
            data: 市场数据
            features: 要添加的技术指标列表
            
        返回:
            DataFrame: 添加指定技术指标后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        for feature in features:
            feature_lower = feature.lower()
            if feature_lower in self.available_indicators:
                df = self.available_indicators[feature_lower](df)
            else:
                logger.warning(f"不支持的技术指标: {feature}")
        
        return df 