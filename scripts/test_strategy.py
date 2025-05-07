#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略测试脚本

该脚本用于从数据库加载市场数据，并在其上运行交易策略，以评估策略生成的信号。
"""

import os
import sys
import argparse
import logging
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.influxdb_storage import InfluxDBStorage
from src.strategies.strategy_factory import StrategyFactory
from src.strategies.strategy_base import Signal, SignalType
from src.utils.config_manager import config_manager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='测试交易策略')
    
    parser.add_argument('--exchange', type=str, default='okx',
                        help='交易所名称 (default: okx)')
    
    parser.add_argument('--symbol', type=str, default='BTC/USDT',
                        help='交易对 (default: BTC/USDT)')
    
    parser.add_argument('--timeframe', type=str, default='1h',
                        help='时间周期 (default: 1h)')
    
    parser.add_argument('--days', type=int, default=30,
                        help='获取过去多少天的数据 (default: 30)')
    
    parser.add_argument('--strategy', type=str, default='moving_average',
                        help='策略类型 (default: moving_average)')
    
    parser.add_argument('--params', type=str, default=None,
                        help='策略参数，格式为key1=value1,key2=value2 (default: None)')
    
    parser.add_argument('--plot', action='store_true',
                        help='是否绘制图表')
    
    parser.add_argument('--verbose', action='store_true',
                        help='显示详细信息')
    
    return parser.parse_args()


def load_market_data(storage: InfluxDBStorage, data_name: str, days: int = 30) -> pd.DataFrame:
    """
    加载市场数据
    
    参数:
        storage: 存储实例
        data_name: 数据名称
        days: 获取过去多少天的数据
        
    返回:
        pd.DataFrame: 市场数据
    """
    try:
        # 加载数据
        df = storage.load_data(data_name)
        
        if df.empty:
            logger.error(f"未找到数据: {data_name}")
            return pd.DataFrame()
        
        # 确保时间索引具有时区信息
        if df.index.tzinfo is None:
            df.index = df.index.tz_localize('UTC')
        
        # 过滤最近几天的数据
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        if df.empty:
            logger.warning(f"过滤后的数据为空: {data_name}")
            return pd.DataFrame()
        
        logger.info(f"成功加载数据: {data_name}, 行数: {len(df)}")
        return df
    
    except Exception as e:
        logger.error(f"加载市场数据失败: {str(e)}")
        return pd.DataFrame()


def parse_strategy_params(params_str: Optional[str]) -> Dict[str, Any]:
    """
    解析策略参数字符串
    
    参数:
        params_str: 策略参数字符串，格式为key1=value1,key2=value2
        
    返回:
        Dict[str, Any]: 策略参数字典
    """
    if not params_str:
        return {}
    
    params = {}
    pairs = params_str.split(',')
    
    for pair in pairs:
        if '=' not in pair:
            continue
        
        key, value = pair.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # 尝试转换值的类型
        try:
            # 尝试转换为整数
            if value.isdigit():
                value = int(value)
            # 尝试转换为浮点数
            elif '.' in value and all(c.isdigit() or c == '.' for c in value):
                value = float(value)
            # 布尔值
            elif value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
        except:
            # 保持为字符串
            pass
        
        params[key] = value
    
    return params


def plot_signals(df: pd.DataFrame, signals: List[Signal], strategy_name: str):
    """
    绘制策略信号图表
    
    参数:
        df: 市场数据
        signals: 信号列表
        strategy_name: 策略名称
    """
    plt.figure(figsize=(12, 8))
    
    # 绘制价格图表
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['close'], label='价格', color='black', alpha=0.7)
    
    # 绘制短期和长期移动平均线（如果存在）
    if 'short_ma' in df.columns and 'long_ma' in df.columns:
        plt.plot(df.index, df['short_ma'], label='短期MA', color='blue', alpha=0.7)
        plt.plot(df.index, df['long_ma'], label='长期MA', color='red', alpha=0.7)
    
    # 绘制RSI（如果存在）
    if 'rsi' in df.columns:
        plt.subplot(2, 1, 2)
        plt.plot(df.index, df['rsi'], label='RSI', color='purple')
        plt.axhline(y=70, color='red', linestyle='--', alpha=0.5)
        plt.axhline(y=30, color='green', linestyle='--', alpha=0.5)
        plt.ylabel('RSI')
        plt.legend()
    
    # 在价格图表上标记信号
    plt.subplot(2, 1, 1)
    
    buy_signals = [s for s in signals if s.signal_type == SignalType.BUY]
    sell_signals = [s for s in signals if s.signal_type == SignalType.SELL]
    
    # 标记买入信号
    if buy_signals:
        buy_times = [s.timestamp for s in buy_signals]
        buy_prices = [s.price for s in buy_signals]
        plt.scatter(buy_times, buy_prices, marker='^', color='green', s=100, label='买入信号')
    
    # 标记卖出信号
    if sell_signals:
        sell_times = [s.timestamp for s in sell_signals]
        sell_prices = [s.price for s in sell_signals]
        plt.scatter(sell_times, sell_prices, marker='v', color='red', s=100, label='卖出信号')
    
    plt.title(f"{strategy_name} - 策略信号")
    plt.ylabel('价格')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.show()


def main():
    """主函数"""
    args = parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 获取存储配置
        db_config = config_manager.get_database_config('market_data')
        
        # 创建存储实例
        storage = InfluxDBStorage(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 8086),
            username=db_config.get('username'),
            password=db_config.get('password'),
            database=db_config.get('database', 'market_data'),
            ssl=db_config.get('ssl', False)
        )
        
        # 构建数据名称
        symbol_str = args.symbol.replace('/', '_')
        data_name = f"{args.exchange}_{symbol_str}_{args.timeframe}"
        
        # 加载市场数据
        df = load_market_data(storage, data_name, args.days)
        
        if df.empty:
            logger.error(f"无法加载市场数据: {data_name}")
            return
        
        # 解析策略参数
        strategy_params = parse_strategy_params(args.params)
        
        # 创建策略实例
        strategy = StrategyFactory.create_strategy(
            strategy_type=args.strategy,
            params=strategy_params
        )
        
        if not strategy:
            logger.error(f"无法创建策略: {args.strategy}")
            return
        
        # 生成交易信号
        signals = strategy.generate_signals(df)
        
        # 打印信号
        print(f"\n策略: {strategy.name}")
        print(f"参数: {strategy.get_parameters()}")
        print(f"数据: {data_name}")
        print(f"时间范围: {df.index[0]} ~ {df.index[-1]}")
        print(f"数据点数: {len(df)}")
        print(f"生成了 {len(signals)} 个交易信号\n")
        
        if signals:
            print("信号摘要:")
            for i, signal in enumerate(signals[:10], 1):  # 打印前10个信号
                print(f"{i}. {signal}")
            
            if len(signals) > 10:
                print(f"... 还有 {len(signals) - 10} 个信号")
        
        # 绘制图表
        if args.plot:
            plot_signals(df, signals, strategy.name)
        
        # 关闭存储连接
        storage.close()
    
    except Exception as e:
        logger.error(f"运行过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 