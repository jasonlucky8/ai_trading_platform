import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional, Union
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    数据处理器，用于市场数据的清洗、标准化和转换
    """

    def __init__(self, fill_method: str = 'ffill'):
        """
        初始化数据处理器
        
        参数:
            fill_method: 填充缺失值的方法，可选值包括 'ffill' (前向填充)，
                        'bfill' (后向填充)，'interpolate' (插值)
        """
        self.fill_method = fill_method
        self.scalers = {}  # 用于存储特征缩放器
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据，处理缺失值和异常值
        
        参数:
            data: 原始市场数据
            
        返回:
            DataFrame: 清洗后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 检查缺失值
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            logger.info(f"数据中存在缺失值: {missing_values}")
            
            # 根据指定方法填充缺失值
            if self.fill_method == 'ffill':
                df.fillna(method='ffill', inplace=True)
                df.fillna(method='bfill', inplace=True)  # 处理开头的缺失值
            elif self.fill_method == 'bfill':
                df.fillna(method='bfill', inplace=True)
                df.fillna(method='ffill', inplace=True)  # 处理结尾的缺失值
            elif self.fill_method == 'interpolate':
                df.interpolate(method='linear', inplace=True)
                df.fillna(method='ffill', inplace=True)  # 处理开头的缺失值
                df.fillna(method='bfill', inplace=True)  # 处理结尾的缺失值
            else:
                raise ValueError(f"不支持的填充方法: {self.fill_method}")
        
        # 检测异常值（这里使用Z-score方法）
        if 'close' in df.columns:
            z_scores = np.abs((df['close'] - df['close'].mean()) / df['close'].std())
            outliers = z_scores > 3  # 超过3个标准差的值视为异常值
            if outliers.sum() > 0:
                logger.info(f"检测到 {outliers.sum()} 个异常值")
                
                # 可以选择替换异常值，这里用移动平均替换
                outlier_indices = df.index[outliers]
                window_size = 5
                for idx in outlier_indices:
                    window = df.loc[:idx].tail(window_size)['close']
                    if not window.empty:
                        df.loc[idx, 'close'] = window.mean()
        
        return df
    
    def normalize_data(self, data: pd.DataFrame, method: str = 'minmax', feature_range: Tuple[float, float] = (0, 1)) -> pd.DataFrame:
        """
        标准化数据
        
        参数:
            data: 市场数据
            method: 标准化方法，'minmax' 或 'standard'
            feature_range: 特征范围，仅当method='minmax'时使用
            
        返回:
            DataFrame: 标准化后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 创建数据副本，避免修改原始数据
        df = data.copy()
        
        # 对数值列进行标准化
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        # 创建缩放器
        for col in numeric_cols:
            if method == 'minmax':
                scaler = MinMaxScaler(feature_range=feature_range)
                df[col] = scaler.fit_transform(df[[col]])
            elif method == 'standard':
                scaler = StandardScaler()
                df[col] = scaler.fit_transform(df[[col]])
            else:
                raise ValueError(f"不支持的标准化方法: {method}")
            
            # 存储缩放器，用于后续转换
            self.scalers[col] = scaler
        
        return df
    
    def resample_data(self, data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        重采样数据，改变时间帧
        
        参数:
            data: 市场数据
            timeframe: 目标时间帧，例如 '1H', '4H', '1D'
            
        返回:
            DataFrame: 重采样后的数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data
        
        # 确保索引是日期时间类型
        if not isinstance(data.index, pd.DatetimeIndex):
            logger.warning("数据索引不是DatetimeIndex，尝试转换")
            data.index = pd.to_datetime(data.index)
        
        # 定义重采样规则
        resampled = data.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        
        # 删除包含缺失值的行
        resampled.dropna(inplace=True)
        
        return resampled
    
    def split_data(self, data: pd.DataFrame, test_size: float = 0.2, validation_size: float = 0.0) -> Tuple:
        """
        划分训练集、验证集和测试集
        
        参数:
            data: 市场数据
            test_size: 测试集比例
            validation_size: 验证集比例
            
        返回:
            Tuple: 包含划分后的数据集
        """
        if data.empty:
            logger.warning("输入数据为空")
            return data, data, data
        
        # 计算划分点
        n = len(data)
        test_split = int(n * (1 - test_size))
        
        if validation_size > 0:
            validation_split = int(n * (1 - test_size - validation_size))
            train_data = data.iloc[:validation_split]
            validation_data = data.iloc[validation_split:test_split]
            test_data = data.iloc[test_split:]
            return train_data, validation_data, test_data
        else:
            train_data = data.iloc[:test_split]
            test_data = data.iloc[test_split:]
            return train_data, test_data
    
    def prepare_training_data(self, data: pd.DataFrame, features: List[str], target: str, 
                             window_size: int = 24, horizon: int = 1, test_size: float = 0.2, 
                             validation_size: float = 0.0) -> Tuple:
        """
        准备模型训练数据，创建时间窗口特征
        
        参数:
            data: 市场数据
            features: 特征列名列表
            target: 目标列名
            window_size: 时间窗口大小
            horizon: 预测时间跨度
            test_size: 测试集比例
            validation_size: 验证集比例
            
        返回:
            Tuple: 包含准备好的特征和目标数据
        """
        if data.empty:
            logger.warning("输入数据为空")
            return None
        
        # 确保所有特征都在数据中
        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            raise ValueError(f"数据中缺少以下特征: {missing_features}")
        
        if target not in data.columns:
            raise ValueError(f"目标列 '{target}' 不在数据中")
        
        # 提取特征和目标
        df = data[features + [target]].copy()
        
        # 创建时间窗口特征
        X, y = [], []
        for i in range(window_size, len(df) - horizon + 1):
            X.append(df.iloc[i - window_size:i][features].values)
            y.append(df.iloc[i + horizon - 1][target])
        
        X = np.array(X)
        y = np.array(y)
        
        # 划分训练集和测试集
        split_idx = int(len(X) * (1 - test_size))
        
        if validation_size > 0:
            val_idx = int(len(X) * (1 - test_size - validation_size))
            X_train, X_val, X_test = X[:val_idx], X[val_idx:split_idx], X[split_idx:]
            y_train, y_val, y_test = y[:val_idx], y[val_idx:split_idx], y[split_idx:]
            return X_train, X_val, X_test, y_train, y_val, y_test
        else:
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            return X_train, X_test, y_train, y_test 