import unittest
import pandas as pd
import os
import shutil
from datetime import datetime, timedelta
import numpy as np
import sqlite3

from src.data.sqlite_storage import SQLiteStorage


class TestSQLiteStorage(unittest.TestCase):
    """SQLite存储测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录用于测试
        self.test_dir = "tests/temp_data/sqlite"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # 设置测试数据库路径
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # 创建存储实例
        self.storage = SQLiteStorage(database_path=self.db_path)
        
        # 创建测试数据
        self.create_test_data()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 关闭数据库连接
        del self.storage
        
        # 删除临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
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
    
    def test_save_and_load_data(self):
        """测试保存和加载数据"""
        # 保存数据
        result = self.storage.save_data(self.test_data, self.test_name)
        self.assertTrue(result, "保存数据应该成功")
        
        # 检查数据库文件是否存在
        self.assertTrue(os.path.exists(self.db_path), "SQLite数据库文件应该已创建")
        
        # 检查表是否存在
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.test_name,))
        table_exists = cursor.fetchone() is not None
        conn.close()
        
        self.assertTrue(table_exists, "数据表应该已创建")
        
        # 加载数据
        loaded_data = self.storage.load_data(self.test_name)
        
        # 验证数据
        self.assertFalse(loaded_data.empty, "加载的数据不应为空")
        self.assertEqual(len(loaded_data), len(self.test_data), "加载的数据行数应与原始数据相同")
        self.assertTrue(all(col in loaded_data.columns for col in self.test_data.columns), 
                       "加载的数据应包含所有原始列")
    
    def test_delete_data(self):
        """测试删除数据"""
        # 先保存数据
        self.storage.save_data(self.test_data, self.test_name)
        
        # 删除数据
        result = self.storage.delete_data(self.test_name)
        self.assertTrue(result, "删除数据应该成功")
        
        # 检查表是否已删除
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.test_name,))
        table_exists = cursor.fetchone() is not None
        conn.close()
        
        self.assertFalse(table_exists, "数据表应该已删除")
    
    def test_list_data(self):
        """测试列出所有数据"""
        # 保存多个数据表
        self.storage.save_data(self.test_data, self.test_name)
        self.storage.save_data(self.test_data, "another_test")
        
        # 列出所有数据
        data_list = self.storage.list_data()
        
        # 验证结果
        self.assertEqual(len(data_list), 2, "应该有两个数据表")
        self.assertTrue(self.test_name in data_list, "列表中应包含第一个测试数据")
        self.assertTrue("another_test" in data_list, "列表中应包含第二个测试数据")
    
    def test_get_metadata(self):
        """测试获取元数据"""
        # 设置元数据
        metadata = {"description": "测试数据", "source": "单元测试"}
        
        # 保存带元数据的数据
        self.storage.save_data(self.test_data, self.test_name, metadata)
        
        # 获取元数据
        result = self.storage.get_metadata(self.test_name)
        
        # 验证元数据
        self.assertIsNotNone(result, "应该返回元数据")
        self.assertEqual(result.get("description"), "测试数据", "元数据应包含描述")
        self.assertEqual(result.get("source"), "单元测试", "元数据应包含来源")
        self.assertTrue("rows" in result, "元数据应包含行数")
        self.assertTrue("columns" in result, "元数据应包含列名")


if __name__ == '__main__':
    unittest.main() 