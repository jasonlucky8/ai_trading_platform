import pandas as pd
import numpy as np
from typing import Dict, Optional, Union, List
import logging
from datetime import datetime
import json
import pymongo

from src.data.data_storage import DataStorage

logger = logging.getLogger(__name__)


class MongoDBStorage(DataStorage):
    """
    使用MongoDB存储数据
    
    MongoDB特别适合存储非结构化或半结构化数据，如交易策略配置、模型参数等。
    该类实现了DataStorage接口，提供标准的数据持久化和检索方法。
    """

    def __init__(self, host: str = 'localhost', port: int = 27017, 
                 username: str = None, password: str = None, 
                 database: str = 'trading_platform', collection_prefix: str = ''):
        """
        初始化MongoDB存储
        
        参数:
            host: MongoDB服务器主机名
            port: MongoDB服务器端口
            username: 用户名（可选）
            password: 密码（可选）
            database: 数据库名称
            collection_prefix: 集合名称前缀（可选）
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database
        self.collection_prefix = collection_prefix
        
        # 创建MongoDB客户端
        try:
            # 构建连接URI
            if username and password:
                uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                uri = f"mongodb://{host}:{port}/{database}"
            
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[database]
            
            # 测试连接
            self.client.server_info()
            
            logger.info(f"成功连接到MongoDB数据库: {database}")
        
        except Exception as e:
            logger.error(f"连接MongoDB数据库失败: {str(e)}")
            raise
        
        # 元数据集合
        self.metadata_collection = f"{self.collection_prefix}metadata"
    
    def _get_collection_name(self, name: str) -> str:
        """
        获取完整的集合名称
        
        参数:
            name: 数据名称/标识符
            
        返回:
            str: 完整的集合名称
        """
        return f"{self.collection_prefix}{name}"
    
    def save_data(self, data: pd.DataFrame, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到MongoDB
        
        参数:
            data: 要保存的数据
            name: 数据名称/标识符（集合名称）
            metadata: 数据的元信息（可选）
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            if data.empty:
                logger.warning(f"尝试保存空数据: {name}")
                return False
            
            collection_name = self._get_collection_name(name)
            collection = self.db[collection_name]
            
            # 准备数据
            # 如果DataFrame有日期索引，将其转换回列
            if isinstance(data.index, pd.DatetimeIndex):
                data = data.reset_index()
            
            # 将DataFrame转换为记录列表
            records = data.to_dict('records')
            
            # 添加更新时间
            for record in records:
                record['_updated_at'] = datetime.utcnow()
            
            # 清空集合（如果存在）
            collection.delete_many({})
            
            # 插入数据
            if records:
                collection.insert_many(records)
            
            # 保存元数据
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "rows": len(data),
                "columns": list(data.columns),
                "last_modified": datetime.utcnow().isoformat()
            })
            
            # 更新元数据集合
            metadata_collection = self.db[self.metadata_collection]
            metadata_collection.update_one(
                {"name": name},
                {"$set": {
                    "name": name,
                    "metadata": metadata,
                    "updated_at": datetime.utcnow()
                }},
                upsert=True
            )
            
            logger.info(f"成功保存数据: {name}, 行数: {len(data)}")
            return True
        
        except Exception as e:
            logger.error(f"保存数据到MongoDB失败: {str(e)}")
            return False
    
    def load_data(self, name: str) -> pd.DataFrame:
        """
        从MongoDB加载数据
        
        参数:
            name: 数据名称/标识符（集合名称）
            
        返回:
            DataFrame: 加载的数据
        """
        try:
            collection_name = self._get_collection_name(name)
            
            # 检查集合是否存在
            if collection_name not in self.db.list_collection_names():
                logger.warning(f"集合不存在: {collection_name}")
                return pd.DataFrame()
            
            collection = self.db[collection_name]
            
            # 查询所有数据
            cursor = collection.find({}, {'_id': 0, '_updated_at': 0})
            
            # 将结果转换为DataFrame
            df = pd.DataFrame(list(cursor))
            
            if df.empty:
                logger.warning(f"加载的数据为空: {name}")
                return df
            
            # 检查是否存在timestamp列，如果有则设置为索引
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            
            logger.info(f"成功加载数据: {name}, 行数: {len(df)}")
            return df
        
        except Exception as e:
            logger.error(f"从MongoDB加载数据失败: {str(e)}")
            return pd.DataFrame()
    
    def delete_data(self, name: str) -> bool:
        """
        从MongoDB删除数据
        
        参数:
            name: 数据名称/标识符（集合名称）
            
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            collection_name = self._get_collection_name(name)
            
            # 检查集合是否存在
            if collection_name not in self.db.list_collection_names():
                logger.warning(f"集合不存在: {collection_name}")
                return False
            
            # 删除集合
            self.db.drop_collection(collection_name)
            
            # 删除元数据
            metadata_collection = self.db[self.metadata_collection]
            metadata_collection.delete_one({"name": name})
            
            logger.info(f"成功删除数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self) -> List[str]:
        """
        列出所有可用的数据（集合）
        
        返回:
            List[str]: 数据名称/标识符列表
        """
        try:
            # 获取所有集合名称
            collections = self.db.list_collection_names()
            
            # 过滤掉元数据集合和以系统命名的集合
            result = []
            prefix_len = len(self.collection_prefix)
            for collection in collections:
                if collection == self.metadata_collection or collection.startswith('system.'):
                    continue
                
                if self.collection_prefix and collection.startswith(self.collection_prefix):
                    # 移除前缀
                    collection = collection[prefix_len:]
                
                result.append(collection)
            
            return result
        
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据的元信息
        
        参数:
            name: 数据名称/标识符（集合名称）
            
        返回:
            Dict: 数据的元信息
        """
        try:
            metadata_collection = self.db[self.metadata_collection]
            
            # 查询元数据
            result = metadata_collection.find_one({"name": name})
            
            if not result:
                return {}
            
            return result.get('metadata', {})
        
        except Exception as e:
            logger.error(f"获取元数据失败: {str(e)}")
            return {}
    
    def close(self):
        """关闭MongoDB连接"""
        try:
            self.client.close()
            logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭MongoDB连接失败: {str(e)}")
    
    def __del__(self):
        """析构函数，确保连接被关闭"""
        try:
            self.close()
        except:
            pass 