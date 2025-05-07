import unittest
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from unittest.mock import MagicMock, patch

from src.data.influxdb_storage import InfluxDBStorage


class TestInfluxDBStorage(unittest.TestCase):
    """InfluxDB存储测试类"""
    
    @patch('src.data.influxdb_storage.InfluxDBClient')
    def setUp(self, mock_client):
        """测试前的准备工作"""
        # 设置模拟的InfluxDB客户端
        self.mock_client = mock_client.return_value
        self.mock_client.get_list_database.return_value = [{'name': 'market_data'}]
        self.mock_client.query.return_value = MagicMock()
        
        # 创建存储实例
        self.storage = InfluxDBStorage(
            host='localhost',
            port=8086,
            username='user',
            password='pass',
            database='market_data'
        )
        
        # 创建测试数据
        self.create_test_data()
        
        # 重置mock调用历史
        self.mock_client.reset_mock()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建一个简单的DataFrame作为测试数据
        dates = pd.date_range(start=datetime.now(), periods=10, freq='H')
        self.test_data = pd.DataFrame({
            'close': np.random.randn(10),
            'volume': np.random.randint(100, 1000, 10),
            'symbol': ['BTC/USDT'] * 10
        }, index=dates)
        
        # 测试时使用的数据名称
        self.test_name = "test_data"
    
    def test_save_data(self):
        """测试保存数据"""
        # 设置mock返回值
        self.mock_client.write_points.return_value = True
        
        # 保存数据
        result = self.storage.save_data(self.test_data, self.test_name)
        
        # 验证结果
        self.assertTrue(result, "保存数据应该成功")
        
        # 验证mock方法调用
        self.mock_client.write_points.assert_called()
        
        # 获取传递给write_points的所有调用参数
        calls = self.mock_client.write_points.call_args_list
        
        # 至少应该有一次调用用于保存数据点，一次调用用于保存元数据
        self.assertGreaterEqual(len(calls), 2, "应至少有两次write_points调用")
    
    def test_load_data(self):
        """测试加载数据"""
        # 模拟查询结果
        mock_result = MagicMock()
        mock_result.get_points.return_value = [
            {
                'time': datetime.now().isoformat(),
                'close': 1.0,
                'volume': 100,
                'symbol': 'BTC/USDT'
            }
            for _ in range(10)
        ]
        self.mock_client.query.return_value = mock_result
        
        # 加载数据
        loaded_data = self.storage.load_data(self.test_name)
        
        # 验证结果
        self.assertFalse(loaded_data.empty, "加载的数据不应为空")
        
        # 验证mock方法调用
        self.mock_client.query.assert_called_once()
        
        # 验证查询语句
        query = self.mock_client.query.call_args[0][0]
        self.assertEqual(query, f'SELECT * FROM "{self.test_name}"', "查询语句应该正确")
    
    def test_delete_data(self):
        """测试删除数据"""
        # 设置mock返回值
        self.mock_client.query.return_value = MagicMock()
        
        # 删除数据
        result = self.storage.delete_data(self.test_name)
        
        # 验证结果
        self.assertTrue(result, "删除数据应该成功")
        
        # 验证mock方法调用
        self.assertEqual(self.mock_client.query.call_count, 2, "应该有两次query调用（删除数据和元数据）")
        
        # 验证第一次调用的查询语句（删除measurement）
        query1 = self.mock_client.query.call_args_list[0][0][0]
        self.assertEqual(query1, f'DROP MEASUREMENT "{self.test_name}"', "第一个查询应该是删除measurement")
    
    def test_list_data(self):
        """测试列出所有数据"""
        # 模拟查询结果
        mock_result = MagicMock()
        mock_result.get_points.return_value = [
            {'name': 'test_data'},
            {'name': 'another_test'},
            {'name': 'metadata'}  # 元数据measurement，应该被过滤掉
        ]
        self.mock_client.query.return_value = mock_result
        
        # 列出所有数据
        data_list = self.storage.list_data()
        
        # 验证结果
        self.assertEqual(len(data_list), 2, "应该有两个数据（不包括元数据）")
        self.assertTrue(self.test_name in data_list, "列表中应包含第一个测试数据")
        self.assertTrue("another_test" in data_list, "列表中应包含第二个测试数据")
        
        # 验证mock方法调用
        self.mock_client.query.assert_called_once_with("SHOW MEASUREMENTS")
    
    def test_get_metadata(self):
        """测试获取元数据"""
        # 模拟查询结果
        mock_result = MagicMock()
        mock_result.get_points.return_value = [{
            'metadata': "{'description': '测试数据', 'source': '单元测试', 'rows': 10, 'columns': ['close', 'volume', 'symbol']}"
        }]
        self.mock_client.query.return_value = mock_result
        
        # 获取元数据
        result = self.storage.get_metadata(self.test_name)
        
        # 验证结果
        self.assertIsNotNone(result, "应该返回元数据")
        self.assertEqual(result.get("description"), "测试数据", "元数据应包含描述")
        self.assertEqual(result.get("source"), "单元测试", "元数据应包含来源")
        self.assertEqual(result.get("rows"), 10, "元数据应包含行数")
        
        # 验证mock方法调用
        self.mock_client.query.assert_called_once()
        
        # 验证查询语句
        query = self.mock_client.query.call_args[0][0]
        self.assertTrue("metadata" in query, "查询语句应包含元数据measurement名称")
        self.assertTrue(self.test_name in query, "查询语句应包含数据名称")


if __name__ == '__main__':
    unittest.main() 