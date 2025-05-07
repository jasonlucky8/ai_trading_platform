#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
交易策略基类

该模块定义了所有交易策略的基类和接口。策略接收市场数据并返回交易信号。
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """交易信号类型"""
    BUY = 1  # 买入信号
    SELL = 2  # 卖出信号
    HOLD = 0  # 持仓不变


class Signal:
    """交易信号类"""
    
    def __init__(self, 
                 symbol: str,
                 signal_type: SignalType,
                 timestamp: pd.Timestamp,
                 price: float,
                 volume: Optional[float] = None,
                 strength: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        初始化交易信号
        
        参数:
            symbol: 交易对符号（如 BTC/USDT）
            signal_type: 信号类型（买入、卖出、持仓）
            timestamp: 信号生成时间
            price: 信号生成时的价格
            volume: 建议交易量（可选）
            strength: 信号强度，0-1之间的数值（可选）
            metadata: 信号的其他元数据（可选）
        """
        self.symbol = symbol
        self.signal_type = signal_type
        self.timestamp = timestamp
        self.price = price
        self.volume = volume
        self.strength = strength or 1.0  # 默认最大强度
        self.metadata = metadata or {}
    
    def __str__(self):
        """字符串表示"""
        return (f"Signal({self.symbol}, {self.signal_type.name}, "
                f"time: {self.timestamp}, price: {self.price}, "
                f"strength: {self.strength:.2f})")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type.name,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "volume": self.volume,
            "strength": self.strength,
            "metadata": self.metadata
        }


class Strategy(ABC):
    """
    交易策略基类
    
    所有交易策略都应继承自此类，并实现必要的方法。
    """
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        """
        初始化策略
        
        参数:
            name: 策略名称
            params: 策略参数
        """
        self.name = name
        self.params = params or {}
        logger.info(f"初始化策略: {self.name}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """
        生成交易信号
        
        参数:
            data: 市场数据
            
        返回:
            List[Signal]: 交易信号列表
        """
        pass
    
    def validate_parameters(self) -> Tuple[bool, str]:
        """
        验证策略参数
        
        返回:
            Tuple[bool, str]: 是否有效，错误消息（如果无效）
        """
        return True, ""
    
    def update_parameters(self, params: Dict[str, Any]) -> bool:
        """
        更新策略参数
        
        参数:
            params: 新的策略参数
            
        返回:
            bool: 是否更新成功
        """
        try:
            self.params.update(params)
            valid, msg = self.validate_parameters()
            if not valid:
                logger.error(f"策略参数无效: {msg}")
                return False
            
            logger.info(f"策略 {self.name} 参数已更新: {params}")
            return True
        except Exception as e:
            logger.error(f"更新策略参数失败: {str(e)}")
            return False
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        返回:
            Dict[str, Any]: 策略参数
        """
        return self.params.copy()
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取策略信息
        
        返回:
            Dict[str, Any]: 策略信息
        """
        return {
            "name": self.name,
            "params": self.get_parameters()
        } 