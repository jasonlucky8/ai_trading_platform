import unittest
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
from unittest.mock import MagicMock, patch

from src.data.mongodb_storage import MongoDBStorage


class TestMongoDBStorage(unittest.TestCase):
    """MongoDB存储测试类"""
    
    @patch('src.data.mongodb_storage.pymongo.MongoClient')
    def setUp(self, mock_client):
        """测试前的准备工作"""
        # 设置模拟的MongoDB客户端
        self.mock_client = mock_client.return_value
        self.mock_db = MagicMock()
        self.mock_client.__getitem__.return_value = self.mock_db
        
        # 设置mock集合
        self.mock_collection = MagicMock()
        self.mock_metadata_collection = MagicMock()
        self.mock_db.__getitem__.side_effect = lambda x: self.mock_metadata_collection if x == 'metadata' else self.mock_collection
        
        # 模拟服务器信息调用
        self.mock_client.server_info.return_value = {'version': '4.0.0'}
        
        # 创建存储实例
        self.storage = MongoDBStorage(
            host='localhost',
            port=27017,
            username='user',
            password='pass',
            database='trading_platform'
        )
        
        # 创建测试数据
        self.create_test_data()
        
        # 重置mock调用历史
        self.mock_client.reset_mock()
        self.mock_db.reset_mock()
        self.mock_collection.reset_mock()
        self.mock_metadata_collection.reset_mock()
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建一个简单的DataFrame作为测试数据
        dates = pd.date_range(start=datetime.now(), periods=10, freq='H')
        self.test_data = pd.DataFrame({
            'timestamp': dates,
            'close': np.random.randn(10),
            'volume': np.random.randint(100, 1000, 10),
            'symbol': ['BTC/USDT'] * 10
        })
        
        # 测试时使用的数据名称
        self.test_name = "test_data"
    
    def test_save_data(self):
        """测试保存数据"""
        # 设置mock返回值
        self.mock_collection.insert_many.return_value = MagicMock()
        self.mock_collection.delete_many.return_value = MagicMock()
        self.mock_metadata_collection.update_one.return_value = MagicMock()
        
        # 保存数据
        result = self.storage.save_data(self.test_data, self.test_name)
        
        # 验证结果
        self.assertTrue(result, "保存数据应该成功")
        
        # 验证mock方法调用
        self.mock_collection.delete_many.assert_called_once()
        self.mock_collection.insert_many.assert_called_once()
        self.mock_metadata_collection.update_one.assert_called_once()
        
        # 验证插入的数据数量
        inserted_records = self.mock_collection.insert_many.call_args[0][0]
        self.assertEqual(len(inserted_records), len(self.test_data), "插入的记录数量应与原始数据相同")
    
    def test_load_data(self):
        """测试加载数据"""
        # 模拟list_collection_names返回值
        self.mock_db.list_collection_names.return_value = [self.test_name, 'metadata']
        
        # 模拟find返回值
        mock_cursor = MagicMock()
        mock_cursor.__iter__.return_value = [
            {
                'timestamp': datetime.now(),
                'close': 1.0,
                'volume': 100,
                'symbol': 'BTC/USDT'
            }
            for _ in range(10)
        ]
        self.mock_collection.find.return_value = mock_cursor
        
        # 加载数据
        loaded_data = self.storage.load_data(self.test_name)
        
        # 验证结果
        self.assertFalse(loaded_data.empty, "加载的数据不应为空")
        
        # 验证mock方法调用
        self.mock_db.list_collection_names.assert_called_once()
        self.mock_collection.find.assert_called_once()
        
        # 验证查询参数
        query = self.mock_collection.find.call_args[0][0]
        projection = self.mock_collection.find.call_args[0][1]
        self.assertEqual(query, {}, "查询应该是空字典")
        self.assertEqual(projection['_id'], 0, "应该排除_id字段")
    
    def test_delete_data(self):
        """测试删除数据"""
        # 模拟list_collection_names返回值
        self.mock_db.list_collection_names.return_value = [self.test_name, 'metadata']
        
        # 模拟drop_collection返回值
        self.mock_db.drop_collection.return_value = MagicMock()
        
        # 模拟delete_one返回值
        self.mock_metadata_collection.delete_one.return_value = MagicMock()
        
        # 删除数据
        result = self.storage.delete_data(self.test_name)
        
        # 验证结果
        self.assertTrue(result, "删除数据应该成功")
        
        # 验证mock方法调用
        self.mock_db.list_collection_names.assert_called_once()
        self.mock_db.drop_collection.assert_called_once_with(self.test_name)
        self.mock_metadata_collection.delete_one.assert_called_once()
        
        # 验证删除元数据的条件
        delete_query = self.mock_metadata_collection.delete_one.call_args[0][0]
        self.assertEqual(delete_query, {"name": self.test_name}, "删除元数据的条件应该正确")
    
    def test_list_data(self):
        """测试列出所有数据"""
        # 模拟list_collection_names返回值
        self.mock_db.list_collection_names.return_value = [self.test_name, 'another_test', 'metadata', 'system.indexes']
        
        # 列出所有数据
        data_list = self.storage.list_data()
        
        # 验证结果
        self.assertEqual(len(data_list), 2, "应该有两个数据集合（排除metadata和系统集合）")
        self.assertTrue(self.test_name in data_list, "列表中应包含第一个测试数据")
        self.assertTrue('another_test' in data_list, "列表中应包含第二个测试数据")
        
        # 验证mock方法调用
        self.mock_db.list_collection_names.assert_called_once()
    
    def test_get_metadata(self):
        """测试获取元数据"""
        # 模拟find_one返回值
        self.mock_metadata_collection.find_one.return_value = {
            'name': self.test_name,
            'metadata': {
                'description': '测试数据',
                'source': '单元测试',
                'rows': 10,
                'columns': ['timestamp', 'close', 'volume', 'symbol']
            },
            'updated_at': datetime.now()
        }
        
        # 获取元数据
        result = self.storage.get_metadata(self.test_name)
        
        # 验证结果
        self.assertIsNotNone(result, "应该返回元数据")
        self.assertEqual(result.get('description'), '测试数据', "元数据应包含描述")
        self.assertEqual(result.get('source'), '单元测试', "元数据应包含来源")
        self.assertEqual(result.get('rows'), 10, "元数据应包含行数")
        
        # 验证mock方法调用
        self.mock_metadata_collection.find_one.assert_called_once()
        
        # 验证查询条件
        query = self.mock_metadata_collection.find_one.call_args[0][0]
        self.assertEqual(query, {"name": self.test_name}, "查询条件应该正确")


if __name__ == '__main__':
    unittest.main() 