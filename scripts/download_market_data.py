#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
市场数据下载脚本

该脚本从交易所下载市场数据（K线数据），并存储到InfluxDB中。
可以指定交易所、交易对、时间范围和时间周期。

用法示例:
    # 下载Binance的BTC/USDT过去30天的1小时K线数据
    python download_market_data.py --exchange binance --symbol BTC/USDT --timeframe 1h --days 30
    
    # 下载多个交易对，保存到指定数据库
    python download_market_data.py --exchange binance --symbol BTC/USDT,ETH/USDT --timeframe 1h,15m --days 7 --influxdb market_data
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta, timezone
import pandas as pd
import time
import ccxt
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.influxdb_storage import InfluxDBStorage
from src.utils.config_manager import config_manager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='下载交易所市场数据并存储到InfluxDB中')
    
    parser.add_argument('--exchange', type=str, default='binance',
                        help='交易所名称 (default: binance)')
    
    parser.add_argument('--symbol', type=str, default='BTC/USDT',
                        help='交易对，多个交易对用逗号分隔 (default: BTC/USDT)')
    
    parser.add_argument('--timeframe', type=str, default='1h',
                        help='时间周期，多个时间周期用逗号分隔 (default: 1h)')
    
    parser.add_argument('--days', type=int, default=7,
                        help='获取过去多少天的数据 (default: 7)')
    
    parser.add_argument('--start', type=str, default=None,
                        help='起始日期，格式：YYYY-MM-DD (default: None)')
    
    parser.add_argument('--end', type=str, default=None,
                        help='结束日期，格式：YYYY-MM-DD (default: None)')
    
    parser.add_argument('--influxdb-host', type=str, default=None,
                        help='InfluxDB主机 (default: 从配置文件获取)')
    
    parser.add_argument('--influxdb-port', type=int, default=None,
                        help='InfluxDB端口 (default: 从配置文件获取)')
    
    parser.add_argument('--influxdb-user', type=str, default=None,
                        help='InfluxDB用户名 (default: 从配置文件获取)')
    
    parser.add_argument('--influxdb-password', type=str, default=None,
                        help='InfluxDB密码 (default: 从配置文件获取)')
    
    parser.add_argument('--influxdb', type=str, default=None,
                        help='InfluxDB数据库名 (default: 从配置文件获取)')
    
    parser.add_argument('--no-store', action='store_true',
                        help='不存储数据，仅打印摘要')
    
    parser.add_argument('--verbose', action='store_true',
                        help='显示详细信息')
    
    return parser.parse_args()


def get_exchange_instance(exchange_id: str) -> ccxt.Exchange:
    """
    获取交易所实例
    
    参数:
        exchange_id: 交易所ID
        
    返回:
        ccxt.Exchange: 交易所实例
    """
    try:
        # 获取交易所类
        exchange_class = getattr(ccxt, exchange_id)
        
        # 创建交易所实例
        exchange = exchange_class({
            'enableRateLimit': True,  # 启用请求速率限制
            'timeout': 30000,         # 超时时间（毫秒）
        })
        
        logger.info(f"已创建交易所实例: {exchange_id}")
        return exchange
    
    except Exception as e:
        logger.error(f"创建交易所实例失败: {str(e)}")
        raise


def fetch_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str, 
                since: Optional[int] = None, limit: int = 1000) -> pd.DataFrame:
    """
    获取K线数据
    
    参数:
        exchange: 交易所实例
        symbol: 交易对
        timeframe: 时间周期
        since: 起始时间（毫秒时间戳）
        limit: 单次请求的数据量
        
    返回:
        pd.DataFrame: K线数据，索引为时间
    """
    try:
        # 检查交易所是否支持该交易对和时间周期
        exchange.load_markets()
        if symbol not in exchange.symbols:
            logger.error(f"交易所 {exchange.id} 不支持交易对 {symbol}")
            return pd.DataFrame()
        
        if timeframe not in exchange.timeframes:
            logger.error(f"交易所 {exchange.id} 不支持时间周期 {timeframe}")
            return pd.DataFrame()
        
        # 获取数据
        data = []
        current_since = since
        
        while True:
            try:
                # 获取一批数据
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=limit)
                
                if not ohlcv or len(ohlcv) == 0:
                    break
                
                # 添加数据
                data.extend(ohlcv)
                
                # 更新起始时间为最后一条数据的时间 + 1
                current_since = ohlcv[-1][0] + 1
                
                # 防止请求过快触发交易所限制
                time.sleep(exchange.rateLimit / 1000)
                
                logger.debug(f"已获取 {len(data)} 条数据，最新时间: {datetime.fromtimestamp(ohlcv[-1][0]/1000)}")
                
                # 如果获取的数据少于请求的数量，说明已经没有更多数据了
                if len(ohlcv) < limit:
                    break
            
            except Exception as e:
                logger.error(f"获取K线数据失败: {str(e)}")
                time.sleep(5)  # 出错后等待一段时间再重试
                continue
        
        if not data:
            logger.warning(f"未获取到 {symbol} {timeframe} 的K线数据")
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # 转换时间戳到UTC时区
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        
        # 设置时间索引
        df.set_index('timestamp', inplace=True)
        
        # 添加交易对列
        df['symbol'] = symbol
        
        # 去重
        df = df[~df.index.duplicated(keep='first')]
        
        # 按时间排序
        df.sort_index(inplace=True)
        
        logger.info(f"已获取 {len(df)} 条 {symbol} {timeframe} 的K线数据，时间范围: {df.index[0]} ~ {df.index[-1]}")
        return df
    
    except Exception as e:
        logger.error(f"获取K线数据失败: {str(e)}")
        return pd.DataFrame()


def get_influxdb_storage(args) -> InfluxDBStorage:
    """
    获取InfluxDB存储实例
    
    参数:
        args: 命令行参数
        
    返回:
        InfluxDBStorage: InfluxDB存储实例
    """
    try:
        # 优先使用命令行参数
        if args.influxdb_host or args.influxdb_port or args.influxdb_user or args.influxdb_password or args.influxdb:
            # 使用命令行参数创建存储实例
            return InfluxDBStorage(
                host=args.influxdb_host or 'localhost',
                port=args.influxdb_port or 8086,
                username=args.influxdb_user,
                password=args.influxdb_password,
                database=args.influxdb or 'market_data',
                ssl=False
            )
        
        # 否则从配置文件获取
        db_config = config_manager.get_database_config('market_data')
        
        if db_config.get('type') != 'influxdb':
            logger.warning(f"配置的市场数据存储类型不是InfluxDB: {db_config.get('type')}")
            logger.info("使用默认的InfluxDB配置")
            
            return InfluxDBStorage(
                host='localhost',
                port=8086,
                username='admin',
                password='admin123',
                database='market_data',
                ssl=False
            )
        
        # 使用配置文件创建存储实例
        return InfluxDBStorage(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 8086),
            username=db_config.get('username'),
            password=db_config.get('password'),
            database=db_config.get('database', 'market_data'),
            ssl=db_config.get('ssl', False)
        )
    
    except Exception as e:
        logger.error(f"创建InfluxDB存储实例失败: {str(e)}")
        raise


def main():
    """主函数"""
    args = parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建交易所实例
        exchange = get_exchange_instance(args.exchange)
        
        # 解析交易对列表
        symbols = [s.strip() for s in args.symbol.split(',')]
        
        # 解析时间周期列表
        timeframes = [tf.strip() for tf in args.timeframe.split(',')]
        
        # 计算时间范围
        if args.start:
            start_date = datetime.strptime(args.start, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        else:
            start_date = datetime.now(timezone.utc) - timedelta(days=args.days)
        
        if args.end:
            end_date = datetime.strptime(args.end, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        else:
            end_date = datetime.now(timezone.utc)
        
        # 转换为毫秒时间戳
        since = int(start_date.timestamp() * 1000)
        
        # 创建InfluxDB存储实例
        if not args.no_store:
            storage = get_influxdb_storage(args)
        
        # 下载并存储数据
        for symbol in symbols:
            for timeframe in timeframes:
                # 下载数据
                df = fetch_ohlcv(exchange, symbol, timeframe, since)
                
                if df.empty:
                    continue
                
                # 过滤时间范围
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                
                if df.empty:
                    logger.warning(f"过滤后的数据为空: {symbol} {timeframe}")
                    continue
                
                # 打印数据摘要
                print(f"\n{symbol} {timeframe} 数据摘要:")
                print(f"时间范围: {df.index[0]} ~ {df.index[-1]}")
                print(f"数据条数: {len(df)}")
                print(f"最新价格: {df['close'].iloc[-1]}")
                print(f"最高价格: {df['high'].max()}")
                print(f"最低价格: {df['low'].min()}")
                print(f"24小时交易量: {df['volume'][-24:].sum() if timeframe == '1h' else 'N/A'}")
                
                # 存储数据
                if not args.no_store:
                    # 构建数据名称
                    data_name = f"{args.exchange}_{symbol.replace('/', '_')}_{timeframe}"
                    
                    # 构建元数据
                    metadata = {
                        "symbol": symbol,
                        "exchange": args.exchange,
                        "timeframe": timeframe,
                        "start_time": df.index[0].isoformat(),
                        "end_time": df.index[-1].isoformat(),
                        "rows": len(df),
                        "source": "ccxt"
                    }
                    
                    # 存储数据
                    result = storage.save_data(df, data_name, metadata)
                    
                    if result:
                        logger.info(f"成功保存数据: {data_name}, 行数: {len(df)}")
                    else:
                        logger.error(f"保存数据失败: {data_name}")
        
        # 关闭存储连接
        if not args.no_store:
            storage.close()
        
        logger.info("数据下载和存储完成")
    
    except Exception as e:
        logger.error(f"运行过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 