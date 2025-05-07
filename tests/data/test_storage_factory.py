import unittest
import os
import shutil
from unittest.mock import patch, MagicMock

from src.data.storage_factory import StorageFactory
from src.data.csv_storage import CSVStorage
from src.data.sqlite_storage import SQLiteStorage
from src.data.influxdb_storage import InfluxDBStorage
from src.data.mongodb_storage import MongoDBStorage
from src.data.pickle_storage import PickleStorage


class TestStorageFactory(unittest.TestCase):
    """StorageFactory测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录
        self.test_dir = "tests/temp_data/factory"
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_csv_storage(self):
        """测试创建CSV存储"""
        config = {
            "type": "csv",
            "path": self.test_dir
        }
        
        storage = StorageFactory.create_storage(config)
        
        self.assertIsInstance(storage, CSVStorage, "应该创建CSVStorage实例")
        self.assertEqual(storage.base_path, self.test_dir, "base_path应该正确设置")
    
    def test_create_sqlite_storage(self):
        """测试创建SQLite存储"""
        db_path = os.path.join(self.test_dir, "test.db")
        config = {
            "type": "sqlite",
            "database_url": f"sqlite:///{db_path}"
        }
        
        storage = StorageFactory.create_storage(config)
        
        self.assertIsInstance(storage, SQLiteStorage, "应该创建SQLiteStorage实例")
        self.assertEqual(storage.database_path, db_path, "database_path应该正确设置")
    
    @patch('src.data.storage_factory.InfluxDBStorage')
    def test_create_influxdb_storage(self, mock_influxdb):
        """测试创建InfluxDB存储"""
        # 设置mock
        mock_instance = MagicMock()
        mock_influxdb.return_value = mock_instance
        
        config = {
            "type": "influxdb",
            "host": "test-host",
            "port": 8086,
            "username": "test-user",
            "password": "test-pass",
            "database": "test-db",
            "ssl": True
        }
        
        storage = StorageFactory.create_storage(config)
        
        # 验证mock调用
        mock_influxdb.assert_called_once_with(
            host="test-host",
            port=8086,
            username="test-user",
            password="test-pass",
            database="test-db",
            ssl=True
        )
        
        self.assertEqual(storage, mock_instance, "应该返回InfluxDBStorage实例")
    
    @patch('src.data.storage_factory.MongoDBStorage')
    def test_create_mongodb_storage(self, mock_mongodb):
        """测试创建MongoDB存储"""
        # 设置mock
        mock_instance = MagicMock()
        mock_mongodb.return_value = mock_instance
        
        config = {
            "type": "mongodb",
            "host": "test-host",
            "port": 27017,
            "username": "test-user",
            "password": "test-pass",
            "database": "test-db",
            "collection_prefix": "test-"
        }
        
        storage = StorageFactory.create_storage(config)
        
        # 验证mock调用
        mock_mongodb.assert_called_once_with(
            host="test-host",
            port=27017,
            username="test-user",
            password="test-pass",
            database="test-db",
            collection_prefix="test-"
        )
        
        self.assertEqual(storage, mock_instance, "应该返回MongoDBStorage实例")
    
    def test_create_pickle_storage(self):
        """测试创建Pickle存储"""
        config = {
            "type": "pickle",
            "path": self.test_dir
        }
        
        storage = StorageFactory.create_storage(config)
        
        self.assertIsInstance(storage, PickleStorage, "应该创建PickleStorage实例")
        self.assertEqual(storage.base_path, self.test_dir, "base_path应该正确设置")
    
    def test_invalid_storage_type(self):
        """测试无效的存储类型"""
        config = {
            "type": "invalid_type",
            "path": self.test_dir
        }
        
        with self.assertRaises(ValueError):
            StorageFactory.create_storage(config)
    
    def test_missing_type(self):
        """测试缺少type字段"""
        config = {
            "path": self.test_dir
        }
        
        with self.assertRaises(ValueError):
            StorageFactory.create_storage(config)
    
    def test_missing_required_config(self):
        """测试缺少必需的配置项"""
        # 测试CSV存储缺少path
        config = {
            "type": "csv"
        }
        
        with self.assertRaises(ValueError):
            StorageFactory.create_storage(config)
        
        # 测试SQLite存储缺少database_url
        config = {
            "type": "sqlite"
        }
        
        with self.assertRaises(ValueError):
            StorageFactory.create_storage(config)
        
        # 测试Pickle存储缺少path
        config = {
            "type": "pickle"
        }
        
        with self.assertRaises(ValueError):
            StorageFactory.create_storage(config)


if __name__ == '__main__':
    unittest.main() 