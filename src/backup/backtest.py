#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
回测工具模块

该模块提供了回测交易策略的功能，计算各种性能指标如收益率、最大回撤等。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

from src.strategies.strategy_base import Strategy, Signal, SignalType

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """交易记录类"""
    entry_time: datetime
    exit_time: Optional[datetime]
    symbol: str
    direction: str  # "long" 或 "short"
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    profit_loss: Optional[float]
    profit_loss_pct: Optional[float]
    status: str  # "open" 或 "closed"
    entry_signal: Signal
    exit_signal: Optional[Signal]


class BacktestResult:
    """回测结果类"""
    
    def __init__(self, 
                 trades: List[TradeRecord],
                 equity_curve: pd.Series,
                 initial_capital: float,
                 strategy_name: str,
                 symbol: str,
                 timeframe: str,
                 start_date: datetime,
                 end_date: datetime,
                 params: Dict[str, Any]):
        """
        初始化回测结果
        
        参数:
            trades: 交易记录列表
            equity_curve: 资金曲线
            initial_capital: 初始资金
            strategy_name: 策略名称
            symbol: 交易对
            timeframe: 时间周期
            start_date: 回测开始日期
            end_date: 回测结束日期
            params: 策略参数
        """
        self.trades = trades
        self.equity_curve = equity_curve
        self.initial_capital = initial_capital
        self.strategy_name = strategy_name
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.params = params
        
        # 计算性能指标
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """计算回测性能指标"""
        if len(self.trades) == 0:
            logger.warning("没有交易记录，无法计算性能指标")
            self.metrics = {
                "total_return": 0,
                "total_return_pct": 0,
                "annualized_return": 0,
                "max_drawdown": 0,
                "max_drawdown_pct": 0,
                "sharpe_ratio": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "avg_profit_pct": 0,
                "avg_loss_pct": 0,
                "avg_trade_duration": 0
            }
            return
        
        # 计算基本指标
        closed_trades = [t for t in self.trades if t.status == "closed"]
        total_trades = len(closed_trades)
        winning_trades = [t for t in closed_trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in closed_trades if t.profit_loss and t.profit_loss <= 0]
        
        # 收益和回撤
        final_equity = self.equity_curve.iloc[-1]
        total_return = final_equity - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # 计算最大回撤
        max_drawdown, max_drawdown_pct = self.calculate_max_drawdown()
        
        # 计算年化收益率
        days = (self.end_date - self.start_date).days
        if days > 0:
            annualized_return = (1 + total_return_pct / 100) ** (365 / days) - 1
        else:
            annualized_return = 0
        
        # 计算夏普比率 (假设无风险利率为0)
        if len(self.equity_curve) > 1:
            daily_returns = self.equity_curve.pct_change().dropna()
            sharpe_ratio = np.sqrt(365) * daily_returns.mean() / daily_returns.std() if daily_returns.std() != 0 else 0
        else:
            sharpe_ratio = 0
        
        # 胜率和盈亏比
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        gross_profit = sum(t.profit_loss for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.profit_loss for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0 if gross_profit == 0 else float('inf')
        
        # 平均盈利和亏损
        avg_profit = gross_profit / len(winning_trades) if winning_trades else 0
        avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
        
        avg_profit_pct = sum(t.profit_loss_pct for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss_pct = sum(t.profit_loss_pct for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # 平均交易持续时间
        durations = [(t.exit_time - t.entry_time).total_seconds() / (60 * 60 * 24) for t in closed_trades if t.exit_time]
        avg_trade_duration = sum(durations) / len(durations) if durations else 0
        
        self.metrics = {
            "total_return": total_return,
            "total_return_pct": total_return_pct,
            "annualized_return": annualized_return * 100,  # 转换为百分比
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe_ratio,
            "win_rate": win_rate * 100,  # 转换为百分比
            "profit_factor": profit_factor,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "avg_profit_pct": avg_profit_pct,
            "avg_loss_pct": avg_loss_pct,
            "avg_trade_duration": avg_trade_duration
        }
    
    def calculate_max_drawdown(self) -> Tuple[float, float]:
        """
        计算最大回撤
        
        返回:
            Tuple[float, float]: (最大回撤金额, 最大回撤百分比)
        """
        # 计算累计最大值
        equity = self.equity_curve.values
        max_equity = np.maximum.accumulate(equity)
        
        # 计算回撤
        drawdown = max_equity - equity
        drawdown_pct = drawdown / max_equity * 100
        
        # 最大回撤
        max_drawdown = drawdown.max()
        max_drawdown_pct = drawdown_pct.max()
        
        return max_drawdown, max_drawdown_pct
    
    def plot_results(self):
        """绘制回测结果图表"""
        plt.figure(figsize=(15, 10))
        
        # 使用Seaborn改善图表外观
        sns.set_style("whitegrid")
        
        # 绘制资金曲线
        plt.subplot(2, 1, 1)
        plt.plot(self.equity_curve.index, self.equity_curve.values, label='资金曲线', color='blue')
        plt.title(f'{self.strategy_name} - 回测结果 ({self.symbol} {self.timeframe})')
        plt.ylabel('资金')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # 标记交易点
        buy_trades = [t for t in self.trades if t.direction == "long"]
        sell_trades = [t for t in self.trades if t.direction == "short"]
        
        # 标记买入点
        if buy_trades:
            entry_times = [t.entry_time for t in buy_trades]
            entry_values = [self.equity_curve.loc[t.entry_time] if t.entry_time in self.equity_curve.index else None for t in buy_trades]
            entry_values = [v for v in entry_values if v is not None]
            
            if entry_values:
                plt.scatter(entry_times[:len(entry_values)], entry_values, marker='^', color='green', s=100, label='买入')
        
        # 标记卖出点
        if sell_trades:
            entry_times = [t.entry_time for t in sell_trades]
            entry_values = [self.equity_curve.loc[t.entry_time] if t.entry_time in self.equity_curve.index else None for t in sell_trades]
            entry_values = [v for v in entry_values if v is not None]
            
            if entry_values:
                plt.scatter(entry_times[:len(entry_values)], entry_values, marker='v', color='red', s=100, label='卖出')
        
        # 绘制回撤曲线
        plt.subplot(2, 1, 2)
        equity = self.equity_curve.values
        max_equity = np.maximum.accumulate(equity)
        drawdown_pct = (max_equity - equity) / max_equity * 100
        
        plt.plot(self.equity_curve.index, drawdown_pct, label='回撤百分比', color='red')
        plt.fill_between(self.equity_curve.index, drawdown_pct, 0, color='red', alpha=0.3)
        plt.title('回撤曲线')
        plt.ylabel('回撤百分比 (%)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        return plt.gcf()
    
    def print_report(self):
        """打印回测报告"""
        print("\n" + "="*50)
        print(f"回测报告: {self.strategy_name}")
        print("="*50)
        print(f"交易对: {self.symbol}")
        print(f"时间周期: {self.timeframe}")
        print(f"回测期间: {self.start_date} 至 {self.end_date}")
        print(f"初始资金: {self.initial_capital:.2f}")
        print(f"策略参数: {self.params}")
        print("-"*50)
        print("性能指标:")
        print(f"总收益: {self.metrics['total_return']:.2f} ({self.metrics['total_return_pct']:.2f}%)")
        print(f"年化收益率: {self.metrics['annualized_return']:.2f}%")
        print(f"最大回撤: {self.metrics['max_drawdown']:.2f} ({self.metrics['max_drawdown_pct']:.2f}%)")
        print(f"夏普比率: {self.metrics['sharpe_ratio']:.2f}")
        print(f"胜率: {self.metrics['win_rate']:.2f}%")
        print(f"盈亏比: {self.metrics['profit_factor']:.2f}")
        print("-"*50)
        print("交易统计:")
        print(f"总交易次数: {self.metrics['total_trades']}")
        print(f"盈利交易: {self.metrics['winning_trades']}")
        print(f"亏损交易: {self.metrics['losing_trades']}")
        print(f"平均盈利: {self.metrics['avg_profit']:.2f} ({self.metrics['avg_profit_pct']:.2f}%)")
        print(f"平均亏损: {self.metrics['avg_loss']:.2f} ({self.metrics['avg_loss_pct']:.2f}%)")
        print(f"平均持仓时间: {self.metrics['avg_trade_duration']:.2f} 天")
        print("="*50)


class Backtest:
    """回测类"""
    
    def __init__(self, 
                 strategy: Strategy,
                 data: pd.DataFrame,
                 initial_capital: float = 10000,
                 fee_rate: float = 0.001,
                 slippage: float = 0.0005,
                 position_size: float = 0.1):
        """
        初始化回测
        
        参数:
            strategy: 交易策略
            data: 市场数据
            initial_capital: 初始资金
            fee_rate: 交易手续费率
            slippage: 滑点
            position_size: 仓位大小（占总资金的比例）
        """
        self.strategy = strategy
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.slippage = slippage
        self.position_size = position_size
        
        # 确保数据按时间排序
        if isinstance(data.index, pd.DatetimeIndex):
            self.data = self.data.sort_index()
        
        # 回测状态
        self.capital = initial_capital  # 当前资金
        self.equity = initial_capital   # 总权益（资金+持仓价值）
        self.position = 0               # 当前持仓数量
        self.position_value = 0         # 当前持仓价值
        self.trades = []                # 交易记录
        self.equity_curve = []          # 资金曲线
        
        # 当前未平仓的交易
        self.open_trade = None
    
    def run(self) -> BacktestResult:
        """
        运行回测
        
        返回:
            BacktestResult: 回测结果
        """
        # 生成交易信号
        signals = self.strategy.generate_signals(self.data)
        
        if not signals:
            logger.warning("没有生成任何交易信号")
            return self._create_result()
        
        # 按时间排序信号
        signals = sorted(signals, key=lambda x: x.timestamp)
        
        # 遍历数据，模拟交易
        for index, row in self.data.iterrows():
            # 记录当前权益
            self.equity = self.capital + self.position_value
            self.equity_curve.append((index, self.equity))
            
            # 更新持仓价值
            current_price = row['close']
            self.position_value = self.position * current_price
            
            # 检查是否有当前时间的信号
            current_signals = [s for s in signals if s.timestamp == index]
            
            for signal in current_signals:
                if signal.signal_type == SignalType.BUY:
                    self._execute_buy(signal, current_price)
                elif signal.signal_type == SignalType.SELL:
                    self._execute_sell(signal, current_price)
        
        # 平掉最后的持仓
        if self.position != 0 and len(self.data) > 0:
            last_price = self.data.iloc[-1]['close']
            last_time = self.data.index[-1]
            
            # 创建平仓信号
            close_signal = Signal(
                symbol=self.data['symbol'].iloc[0] if 'symbol' in self.data.columns else "UNKNOWN",
                signal_type=SignalType.SELL if self.position > 0 else SignalType.BUY,
                timestamp=last_time,
                price=last_price,
                metadata={"type": "close_position"}
            )
            
            if self.position > 0:
                self._execute_sell(close_signal, last_price)
            else:
                self._execute_buy(close_signal, last_price)
        
        # 创建回测结果
        return self._create_result()
    
    def _execute_buy(self, signal: Signal, price: float):
        """
        执行买入操作
        
        参数:
            signal: 买入信号
            price: 当前价格
        """
        # 如果有空头持仓，先平仓
        if self.position < 0:
            # 计算平仓数量
            cover_quantity = abs(self.position)
            
            # 执行平仓（考虑滑点和手续费）
            price_with_slippage = price * (1 + self.slippage)
            cost = cover_quantity * price_with_slippage
            fee = cost * self.fee_rate
            
            # 更新资金和持仓
            self.capital -= (cost + fee)
            self.position = 0
            self.position_value = 0
            
            # 更新未平仓交易记录
            if self.open_trade:
                self.open_trade.exit_time = signal.timestamp
                self.open_trade.exit_price = price_with_slippage
                self.open_trade.profit_loss = (self.open_trade.entry_price - price_with_slippage) * cover_quantity - fee
                self.open_trade.profit_loss_pct = (self.open_trade.entry_price - price_with_slippage) / self.open_trade.entry_price * 100
                self.open_trade.status = "closed"
                self.open_trade.exit_signal = signal
                
                # 添加到交易记录
                self.trades.append(self.open_trade)
                self.open_trade = None
        
        # 开多头仓位
        if self.position == 0:
            # 计算买入数量（使用资金的position_size比例）
            buy_amount = self.capital * self.position_size
            price_with_slippage = price * (1 + self.slippage)
            quantity = buy_amount / price_with_slippage
            cost = quantity * price_with_slippage
            fee = cost * self.fee_rate
            
            # 确保有足够的资金
            if cost + fee <= self.capital:
                # 更新资金和持仓
                self.capital -= (cost + fee)
                self.position = quantity
                self.position_value = quantity * price
                
                # 创建交易记录
                self.open_trade = TradeRecord(
                    entry_time=signal.timestamp,
                    exit_time=None,
                    symbol=signal.symbol,
                    direction="long",
                    entry_price=price_with_slippage,
                    exit_price=None,
                    quantity=quantity,
                    profit_loss=None,
                    profit_loss_pct=None,
                    status="open",
                    entry_signal=signal,
                    exit_signal=None
                )
            else:
                logger.warning(f"资金不足，无法开仓: {signal}")
    
    def _execute_sell(self, signal: Signal, price: float):
        """
        执行卖出操作
        
        参数:
            signal: 卖出信号
            price: 当前价格
        """
        # 如果有多头持仓，先平仓
        if self.position > 0:
            # 计算平仓数量
            sell_quantity = self.position
            
            # 执行平仓（考虑滑点和手续费）
            price_with_slippage = price * (1 - self.slippage)
            proceeds = sell_quantity * price_with_slippage
            fee = proceeds * self.fee_rate
            
            # 更新资金和持仓
            self.capital += (proceeds - fee)
            self.position = 0
            self.position_value = 0
            
            # 更新未平仓交易记录
            if self.open_trade:
                self.open_trade.exit_time = signal.timestamp
                self.open_trade.exit_price = price_with_slippage
                self.open_trade.profit_loss = (price_with_slippage - self.open_trade.entry_price) * sell_quantity - fee
                self.open_trade.profit_loss_pct = (price_with_slippage - self.open_trade.entry_price) / self.open_trade.entry_price * 100
                self.open_trade.status = "closed"
                self.open_trade.exit_signal = signal
                
                # 添加到交易记录
                self.trades.append(self.open_trade)
                self.open_trade = None
        
        # 开空头仓位
        if self.position == 0:
            # 计算卖出数量（使用资金的position_size比例）
            sell_amount = self.capital * self.position_size
            price_with_slippage = price * (1 - self.slippage)
            quantity = sell_amount / price_with_slippage
            proceeds = quantity * price_with_slippage
            fee = proceeds * self.fee_rate
            
            # 更新资金和持仓
            self.capital += (proceeds - fee)
            self.position = -quantity  # 负数表示空头持仓
            self.position_value = quantity * price
            
            # 创建交易记录
            self.open_trade = TradeRecord(
                entry_time=signal.timestamp,
                exit_time=None,
                symbol=signal.symbol,
                direction="short",
                entry_price=price_with_slippage,
                exit_price=None,
                quantity=quantity,
                profit_loss=None,
                profit_loss_pct=None,
                status="open",
                entry_signal=signal,
                exit_signal=None
            )
    
    def _create_result(self) -> BacktestResult:
        """
        创建回测结果
        
        返回:
            BacktestResult: 回测结果
        """
        # 创建资金曲线
        if self.equity_curve:
            times, values = zip(*self.equity_curve)
            equity_series = pd.Series(values, index=times)
        else:
            equity_series = pd.Series([self.initial_capital], index=[self.data.index[0]] if not self.data.empty else [pd.Timestamp.now()])
        
        # 获取回测时间范围
        start_date = self.data.index[0] if not self.data.empty else pd.Timestamp.now()
        end_date = self.data.index[-1] if not self.data.empty else pd.Timestamp.now()
        
        # 获取交易对和时间周期信息
        symbol = self.data['symbol'].iloc[0] if 'symbol' in self.data.columns else "UNKNOWN"
        timeframe = "unknown"
        
        # 创建回测结果
        result = BacktestResult(
            trades=self.trades,
            equity_curve=equity_series,
            initial_capital=self.initial_capital,
            strategy_name=self.strategy.name,
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            params=self.strategy.get_parameters()
        )
        
        return result 