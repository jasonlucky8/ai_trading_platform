import unittest
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
import logging
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.influxdb_storage import InfluxDBStorage

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestInfluxDBRealConnection(unittest.TestCase):
    """InfluxDB真实连接测试类"""
    
    @classmethod
    def setUpClass(cls):
        """在所有测试之前运行一次"""
        # 从环境变量获取测试数据库配置
        cls.host = os.environ.get('TEST_INFLUXDB_HOST', 'localhost')
        cls.port = int(os.environ.get('TEST_INFLUXDB_PORT', '8086'))
        cls.username = os.environ.get('TEST_INFLUXDB_USER', 'admin')
        cls.password = os.environ.get('TEST_INFLUXDB_PASSWORD', 'admin123')
        cls.database = os.environ.get('TEST_INFLUXDB_DATABASE', 'test_market_data')
        
        # 创建测试数据库连接
        cls.storage = None
        try:
            cls.storage = InfluxDBStorage(
                host=cls.host,
                port=cls.port,
                username=cls.username,
                password=cls.password,
                database=cls.database,
                ssl=False
            )
            logger.info(f"成功连接到测试InfluxDB: {cls.host}:{cls.port}/{cls.database}")
        except Exception as e:
            logger.error(f"连接测试InfluxDB失败: {str(e)}")
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
                # 关闭连接
                cls.storage.close()
                logger.info("测试完成，已清理测试数据和关闭连接")
            except Exception as e:
                logger.error(f"清理测试数据失败: {str(e)}")
    
    @classmethod
    def create_test_data(cls):
        """创建测试数据"""
        # 创建一个包含OHLCV数据的DataFrame
        cls.test_name = "test_market_data"
        cls.symbol = "BTC/USDT"
        
        # 生成最近24小时的分钟级数据
        end_time = datetime.utcnow().replace(second=0, microsecond=0)
        start_time = end_time - timedelta(hours=24)
        
        # 生成时间索引
        dates = pd.date_range(start=start_time, end=end_time, freq='1min')
        
        # 生成价格数据（模拟真实价格波动）
        base_price = 40000.0  # 基础价格
        price_volatility = 200.0  # 价格波动幅度
        
        # 随机游走生成价格
        np.random.seed(42)  # 设置随机种子以便重现结果
        random_walk = np.random.normal(0, 1, size=len(dates))
        cumulative_walk = np.cumsum(random_walk)
        
        # 标准化到合理的价格范围
        normalized_walk = (cumulative_walk - np.min(cumulative_walk)) / (np.max(cumulative_walk) - np.min(cumulative_walk))
        prices = base_price + (normalized_walk * price_volatility * 2) - price_volatility
        
        # 生成OHLCV数据
        n = len(dates)
        cls.test_data = pd.DataFrame({
            'open': prices,
            'high': [p + np.random.uniform(5, 15) for p in prices],
            'low': [p - np.random.uniform(5, 15) for p in prices],
            'close': [p + np.random.uniform(-10, 10) for p in prices],
            'volume': np.random.uniform(0.5, 10, n) * 10,
            'symbol': [cls.symbol] * n
        }, index=dates)
    
    def test_real_connection(self):
        """测试真实连接是否正常工作"""
        self.assertIsNotNone(self.storage, "存储实例应该已创建")
    
    def test_save_and_load_data(self):
        """测试保存和加载数据"""
        # 保存数据
        result = self.storage.save_data(self.test_data, self.test_name)
        self.assertTrue(result, "保存数据应该成功")
        
        # 加载数据
        loaded_data = self.storage.load_data(self.test_name)
        
        # 验证数据
        self.assertFalse(loaded_data.empty, "加载的数据不应为空")
        self.assertTrue('open' in loaded_data.columns, "加载的数据应包含open列")
        self.assertTrue('high' in loaded_data.columns, "加载的数据应包含high列")
        self.assertTrue('low' in loaded_data.columns, "加载的数据应包含low列")
        self.assertTrue('close' in loaded_data.columns, "加载的数据应包含close列")
        self.assertTrue('volume' in loaded_data.columns, "加载的数据应包含volume列")
        
        # 验证数据量级（可能由于数据库存储和时间精度问题，行数可能不完全相同）
        self.assertGreaterEqual(len(loaded_data), len(self.test_data) * 0.9, 
                              "加载的数据行数应至少为原始数据的90%")
    
    def test_get_metadata(self):
        """测试获取元数据"""
        # 设置元数据
        metadata = {
            "description": "BTC/USDT 1分钟K线数据",
            "source": "集成测试",
            "time_frame": "1m",
            "start_time": self.test_data.index[0].isoformat(),
            "end_time": self.test_data.index[-1].isoformat()
        }
        
        # 保存带元数据的数据
        result = self.storage.save_data(self.test_data, self.test_name, metadata)
        self.assertTrue(result, "保存带元数据的数据应该成功")
        
        # 获取元数据
        retrieved_metadata = self.storage.get_metadata(self.test_name)
        
        # 验证元数据
        self.assertIsNotNone(retrieved_metadata, "应该返回元数据")
        self.assertEqual(retrieved_metadata.get("description"), "BTC/USDT 1分钟K线数据", "元数据应包含描述")
        self.assertEqual(retrieved_metadata.get("source"), "集成测试", "元数据应包含来源")
        self.assertEqual(retrieved_metadata.get("time_frame"), "1m", "元数据应包含时间帧")
    
    def test_list_data(self):
        """测试列出所有数据"""
        # 保存测试数据
        self.storage.save_data(self.test_data, self.test_name)
        
        # 保存另一个测试数据集
        another_name = "another_test_data"
        self.storage.save_data(self.test_data.head(10), another_name)
        
        try:
            # 列出所有数据
            data_list = self.storage.list_data()
            
            # 验证结果
            self.assertGreaterEqual(len(data_list), 2, "应该至少有两个数据集")
            self.assertTrue(self.test_name in data_list, "列表中应包含第一个测试数据")
            self.assertTrue(another_name in data_list, "列表中应包含第二个测试数据")
        
        finally:
            # 清理额外的测试数据
            self.storage.delete_data(another_name)


if __name__ == '__main__':
    # 只有在明确指定要运行真实数据库测试时才运行
    if os.environ.get('RUN_REAL_DB_TESTS') == 'true':
        unittest.main()
    else:
        print("跳过真实数据库测试。要运行测试，请设置环境变量 RUN_REAL_DB_TESTS=true") 