#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略工厂模块

该模块提供了创建和管理交易策略的工厂类。
"""

import logging
from typing import Dict, Any, List, Type, Optional

from src.strategies.strategy_base import Strategy
from src.strategies.moving_average import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy

logger = logging.getLogger(__name__)


class StrategyFactory:
    """
    策略工厂类
    
    负责注册、创建和管理交易策略。
    """
    
    # 策略类型映射
    _strategy_classes: Dict[str, Type[Strategy]] = {
        'moving_average': MovingAverageStrategy,
        'rsi': RSIStrategy
        # 可以添加更多策略
    }
    
    @classmethod
    def register_strategy(cls, strategy_type: str, strategy_class: Type[Strategy]) -> None:
        """
        注册一个新的策略类型
        
        参数:
            strategy_type: 策略类型标识符
            strategy_class: 策略类
        """
        if strategy_type in cls._strategy_classes:
            logger.warning(f"策略类型 '{strategy_type}' 已经存在，将被覆盖")
        
        cls._strategy_classes[strategy_type] = strategy_class
        logger.info(f"注册策略类型: {strategy_type}")
    
    @classmethod
    def create_strategy(cls, strategy_type: str, name: str = None, params: Dict[str, Any] = None) -> Optional[Strategy]:
        """
        创建策略实例
        
        参数:
            strategy_type: 策略类型标识符
            name: 策略名称（可选）
            params: 策略参数（可选）
            
        返回:
            Strategy: 策略实例，如果类型不存在则返回None
        """
        try:
            if strategy_type not in cls._strategy_classes:
                logger.error(f"未知策略类型: {strategy_type}")
                return None
            
            strategy_class = cls._strategy_classes[strategy_type]
            
            # 如果没有提供名称，使用默认名称
            if name is None:
                name = f"{strategy_type.capitalize()}策略"
            
            # 创建策略实例
            strategy = strategy_class(name=name, params=params)
            logger.info(f"创建策略: {name} (类型: {strategy_type})")
            
            return strategy
        
        except Exception as e:
            logger.error(f"创建策略失败: {str(e)}")
            return None
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """
        获取所有可用的策略类型
        
        返回:
            List[str]: 策略类型列表
        """
        return list(cls._strategy_classes.keys())
    
    @classmethod
    def get_strategy_class(cls, strategy_type: str) -> Optional[Type[Strategy]]:
        """
        获取策略类
        
        参数:
            strategy_type: 策略类型标识符
            
        返回:
            Type[Strategy]: 策略类，如果类型不存在则返回None
        """
        return cls._strategy_classes.get(strategy_type) 