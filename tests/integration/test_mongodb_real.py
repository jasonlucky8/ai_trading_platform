import unittest
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.mongodb_storage import MongoDBStorage

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestMongoDBRealConnection(unittest.TestCase):
    """MongoDB真实连接测试类"""
    
    @classmethod
    def setUpClass(cls):
        """在所有测试之前运行一次"""
        # 从环境变量获取测试数据库配置
        cls.host = os.environ.get('TEST_MONGODB_HOST', 'localhost')
        cls.port = int(os.environ.get('TEST_MONGODB_PORT', '27017'))
        cls.username = os.environ.get('TEST_MONGODB_USER', 'admin')
        cls.password = os.environ.get('TEST_MONGODB_PASSWORD', 'admin123')
        cls.database = os.environ.get('TEST_MONGODB_DATABASE', 'test_trading_platform')
        
        # 创建测试数据库连接
        cls.storage = None
        try:
            cls.storage = MongoDBStorage(
                host=cls.host,
                port=cls.port,
                username=cls.username,
                password=cls.password,
                database=cls.database,
                collection_prefix='test_'
            )
            logger.info(f"成功连接到测试MongoDB: {cls.host}:{cls.port}/{cls.database}")
        except Exception as e:
            logger.error(f"连接测试MongoDB失败: {str(e)}")
            raise
        
        # 创建测试数据
        cls.create_test_data()
    
    @classmethod
    def tearDownClass(cls):
        """在所有测试之后运行一次"""
        # 清理测试数据
        if cls.storage:
            try:
                # 删除测试数据
                cls.storage.delete_data(cls.test_name)
                cls.storage.delete_data(cls.strategy_name)
                # 关闭连接
                cls.storage.close()
                logger.info("测试完成，已清理测试数据和关闭连接")
            except Exception as e:
                logger.error(f"清理测试数据失败: {str(e)}")
    
    @classmethod
    def create_test_data(cls):
        """创建测试数据"""
        # 1. 创建一个交易信号数据集
        cls.test_name = "trade_signals"
        
        # 生成最近7天的日级信号数据
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=7)
        
        # 生成日期序列
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 生成信号数据
        signals = []
        for timestamp in dates:
            # 随机生成买入或卖出信号
            signal_type = np.random.choice(['BUY', 'SELL'])
            confidence = round(np.random.uniform(0.6, 0.95), 2)
            price = round(np.random.uniform(39000, 41000), 2)
            
            signals.append({
                'timestamp': timestamp,
                'symbol': 'BTC/USDT',
                'signal_type': signal_type,
                'confidence': confidence,
                'price': price,
                'volume': round(np.random.uniform(0.1, 2.0), 3)
            })
        
        cls.test_data = pd.DataFrame(signals)
        
        # 2. 创建一个策略配置数据
        cls.strategy_name = "strategy_config"
        
        # 模拟策略配置
        cls.strategy_config = {
            "strategy_name": "MovingAverageCrossover",
            "version": "1.0",
            "description": "经典的双均线交叉策略",
            "created_at": datetime.now().isoformat(),
            "parameters": {
                "short_window": 10,
                "long_window": 30,
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "timeframe": "1h",
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.15
            },
            "performance": {
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.25,
                "win_rate": 0.62
            },
            "status": "active"
        }
        
        # 将策略配置转换为DataFrame
        cls.strategy_df = pd.DataFrame([cls.strategy_config])
    
    def test_real_connection(self):
        """测试真实连接是否正常工作"""
        self.assertIsNotNone(self.storage, "存储实例应该已创建")
    
    def test_save_and_load_data(self):
        """测试保存和加载数据"""
        # 保存交易信号数据
        result = self.storage.save_data(self.test_data, self.test_name)
        self.assertTrue(result, "保存数据应该成功")
        
        # 加载数据
        loaded_data = self.storage.load_data(self.test_name)
        
        # 验证数据
        self.assertFalse(loaded_data.empty, "加载的数据不应为空")
        self.assertEqual(len(loaded_data), len(self.test_data), "加载的数据行数应与原始数据相同")
        self.assertTrue('signal_type' in loaded_data.columns, "加载的数据应包含signal_type列")
        self.assertTrue('confidence' in loaded_data.columns, "加载的数据应包含confidence列")
    
    def test_save_and_load_complex_data(self):
        """测试保存和加载复杂数据（如策略配置）"""
        # 保存策略配置
        result = self.storage.save_data(self.strategy_df, self.strategy_name)
        self.assertTrue(result, "保存复杂数据应该成功")
        
        # 加载数据
        loaded_data = self.storage.load_data(self.strategy_name)
        
        # 验证数据
        self.assertFalse(loaded_data.empty, "加载的数据不应为空")
        
        # 检查复杂嵌套结构是否保留
        first_row = loaded_data.iloc[0].to_dict()
        self.assertTrue('parameters' in first_row, "加载的数据应包含parameters字段")
        self.assertTrue('performance' in first_row, "加载的数据应包含performance字段")
        
        # 验证嵌套字段的内容
        # MongoDB可能将嵌套字典转换为字符串，需要检查并转换回来
        parameters = first_row['parameters']
        if isinstance(parameters, str):
            parameters = json.loads(parameters.replace("'", "\""))
        
        self.assertTrue('short_window' in parameters, "parameters应包含short_window")
        self.assertTrue('symbols' in parameters, "parameters应包含symbols")
    
    def test_get_metadata(self):
        """测试获取元数据"""
        # 设置元数据
        metadata = {
            "description": "交易信号数据",
            "source": "集成测试",
            "version": "1.0",
            "last_updated": datetime.now().isoformat()
        }
        
        # 保存带元数据的数据
        result = self.storage.save_data(self.test_data, self.test_name, metadata)
        self.assertTrue(result, "保存带元数据的数据应该成功")
        
        # 获取元数据
        retrieved_metadata = self.storage.get_metadata(self.test_name)
        
        # 验证元数据
        self.assertIsNotNone(retrieved_metadata, "应该返回元数据")
        self.assertEqual(retrieved_metadata.get("description"), "交易信号数据", "元数据应包含描述")
        self.assertEqual(retrieved_metadata.get("source"), "集成测试", "元数据应包含来源")
        self.assertEqual(retrieved_metadata.get("version"), "1.0", "元数据应包含版本号")
    
    def test_list_data(self):
        """测试列出所有数据"""
        # 保存测试数据
        self.storage.save_data(self.test_data, self.test_name)
        self.storage.save_data(self.strategy_df, self.strategy_name)
        
        # 列出所有数据
        data_list = self.storage.list_data()
        
        # 验证结果
        self.assertGreaterEqual(len(data_list), 2, "应该至少有两个数据集")
        self.assertTrue(self.test_name in data_list, "列表中应包含交易信号数据")
        self.assertTrue(self.strategy_name in data_list, "列表中应包含策略配置数据")


if __name__ == '__main__':
    # 只有在明确指定要运行真实数据库测试时才运行
    if os.environ.get('RUN_REAL_DB_TESTS') == 'true':
        unittest.main()
    else:
        print("跳过真实数据库测试。要运行测试，请设置环境变量 RUN_REAL_DB_TESTS=true") 