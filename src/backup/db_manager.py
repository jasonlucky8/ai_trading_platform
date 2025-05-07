import logging
from typing import Dict, Optional, Any

from src.data.data_storage import DataStorage
from src.data.storage_factory import StorageFactory
from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    数据库管理类，用于管理数据库连接和存储实例的创建
    """
    
    def __init__(self):
        """初始化数据库管理器"""
        self.storage_instances = {}  # 存储实例缓存
    
    def get_storage(self, storage_type: str) -> Optional[DataStorage]:
        """
        获取数据存储实例
        
        参数:
            storage_type: 存储类型，可选值: "market_data", "trade_data"
            
        返回:
            DataStorage: 数据存储实例，如果创建失败则返回None
        """
        try:
            # 检查缓存中是否已有实例
            if storage_type in self.storage_instances:
                return self.storage_instances[storage_type]
            
            # 获取存储配置
            storage_config = config_manager.get_database_config(storage_type)
            
            if not storage_config:
                logger.error(f"未找到存储配置: {storage_type}")
                return None
            
            # 创建存储实例
            storage = StorageFactory.create_storage(storage_config)
            
            # 缓存实例
            self.storage_instances[storage_type] = storage
            
            return storage
        
        except Exception as e:
            logger.error(f"创建存储实例失败 ({storage_type}): {str(e)}")
            return None
    
    def close_all(self):
        """关闭所有存储连接"""
        for storage_type, storage in self.storage_instances.items():
            try:
                if hasattr(storage, 'close'):
                    storage.close()
                    logger.info(f"已关闭存储连接: {storage_type}")
            except Exception as e:
                logger.error(f"关闭存储连接失败 ({storage_type}): {str(e)}")
        
        # 清空缓存
        self.storage_instances = {}


# 创建一个全局数据库管理器实例
db_manager = DatabaseManager() 