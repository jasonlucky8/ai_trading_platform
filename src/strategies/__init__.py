#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
交易策略包

该包包含各种交易策略的实现，包括：
- 策略基类（strategy_base）
- 移动平均线交叉策略（moving_average）
- RSI策略（rsi_strategy）
- 策略工厂（strategy_factory）
"""

from src.strategies.strategy_base import Strategy, Signal, SignalType
from src.strategies.moving_average import MovingAverageStrategy
from src.strategies.rsi_strategy import RSIStrategy
from src.strategies.strategy_factory import StrategyFactory

__all__ = [
    'Strategy',
    'Signal',
    'SignalType',
    'MovingAverageStrategy',
    'RSIStrategy',
    'StrategyFactory'
]
