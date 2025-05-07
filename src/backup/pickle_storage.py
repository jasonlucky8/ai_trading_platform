import os
import pandas as pd
import pickle
from typing import List, Dict, Any, Optional, Union
import logging
import json
from datetime import datetime

from src.data.data_storage import DataStorage

logger = logging.getLogger(__name__)


class PickleStorage(DataStorage):
    """
    Pickle文件存储实现
    
    使用Pickle序列化格式存储数据，每个数据集对应一个文件
    """
    
    def __init__(self, base_path: str):
        """
        初始化Pickle存储
        
        参数:
            base_path (str): Pickle文件存储的基础路径
        """
        self.base_path = base_path
        # 确保目录存在
        os.makedirs(self.base_path, exist_ok=True)
        # 创建元数据存储
        self.metadata_path = os.path.join(self.base_path, 'metadata.json')
        if not os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'w') as f:
                json.dump({}, f)
        
        logger.info(f"Pickle Storage initialized at {self.base_path}")
    
    def get_file_path(self, name: str) -> str:
        """
        获取指定数据集的文件路径
        
        参数:
            name (str): 数据集名称
            
        返回:
            str: 文件路径
        """
        # 确保名称安全
        safe_name = name.replace('/', '_').replace('\\', '_')
        return os.path.join(self.base_path, f"{safe_name}.pkl")
    
    def save_data(self, name: str, data: pd.DataFrame, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到Pickle文件
        
        参数:
            name (str): 数据集名称
            data (pd.DataFrame): 要保存的数据
            metadata (Dict, optional): 元数据
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            file_path = self.get_file_path(name)
            
            # 保存数据
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            # 更新元数据
            if metadata is None:
                metadata = {}
            
            metadata['updated_at'] = datetime.now().isoformat()
            
            # 读取当前元数据
            with open(self.metadata_path, 'r') as f:
                all_metadata = json.load(f)
            
            # 如果是新数据集，添加创建时间
            if name not in all_metadata:
                metadata['created_at'] = metadata['updated_at']
            else:
                # 保留原有的创建时间
                metadata['created_at'] = all_metadata[name].get('created_at', metadata['updated_at'])
            
            # 更新元数据
            all_metadata[name] = metadata
            
            # 保存更新后的元数据
            with open(self.metadata_path, 'w') as f:
                json.dump(all_metadata, f, default=str)
            
            logger.info(f"Saved data to {file_path}, rows: {len(data)}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data '{name}': {str(e)}")
            return False
    
    def load_data(self, name: str, query: Optional[Dict] = None) -> pd.DataFrame:
        """
        从Pickle文件加载数据
        
        参数:
            name (str): 数据集名称
            query (Dict, optional): 查询条件（简单实现）
            
        返回:
            pd.DataFrame: 加载的数据
        """
        try:
            file_path = self.get_file_path(name)
            
            if not os.path.exists(file_path):
                logger.warning(f"Data '{name}' not found at {file_path}")
                return pd.DataFrame()
            
            # 读取数据
            with open(file_path, 'rb') as f:
                df = pickle.load(f)
            
            # 应用简单查询（如果提供）
            if query and isinstance(df, pd.DataFrame):
                for key, value in query.items():
                    if key in df.columns:
                        df = df[df[key] == value]
            
            logger.info(f"Loaded data from {file_path}, rows: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"Failed to load data '{name}': {str(e)}")
            return pd.DataFrame()
    
    def delete_data(self, name: str) -> bool:
        """
        删除数据
        
        参数:
            name (str): 数据集名称
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            file_path = self.get_file_path(name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted data file {file_path}")
                
                # 删除元数据
                with open(self.metadata_path, 'r') as f:
                    all_metadata = json.load(f)
                
                if name in all_metadata:
                    del all_metadata[name]
                    
                    with open(self.metadata_path, 'w') as f:
                        json.dump(all_metadata, f)
                
                return True
            else:
                logger.warning(f"Data file {file_path} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Failed to delete data '{name}': {str(e)}")
            return False
    
    def list_data(self) -> List[str]:
        """
        列出所有可用的数据集
        
        返回:
            List[str]: 数据集名称列表
        """
        try:
            files = [f for f in os.listdir(self.base_path) if f.endswith('.pkl')]
            # 去掉文件扩展名
            data_names = [os.path.splitext(f)[0] for f in files]
            return data_names
        except Exception as e:
            logger.error(f"Failed to list data: {str(e)}")
            return []
    
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据集元数据
        
        参数:
            name (str): 数据集名称
            
        返回:
            Dict: 元数据字典
        """
        try:
            with open(self.metadata_path, 'r') as f:
                all_metadata = json.load(f)
            
            return all_metadata.get(name, {})
        except Exception as e:
            logger.error(f"Failed to get metadata for '{name}': {str(e)}")
            return {}
    
    def append_data(self, name: str, data: pd.DataFrame) -> bool:
        """
        追加数据到现有数据集
        
        参数:
            name (str): 数据集名称
            data (pd.DataFrame): 要追加的数据
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            file_path = self.get_file_path(name)
            
            if os.path.exists(file_path):
                # 读取现有数据
                with open(file_path, 'rb') as f:
                    existing_data = pickle.load(f)
                
                # 合并数据
                if isinstance(existing_data, pd.DataFrame) and isinstance(data, pd.DataFrame):
                    combined_data = pd.concat([existing_data, data])
                    # 去重（假设索引是唯一的）
                    combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                    
                    # 保存合并后的数据
                    with open(file_path, 'wb') as f:
                        pickle.dump(combined_data, f)
                    
                    # 更新元数据时间戳
                    with open(self.metadata_path, 'r') as f:
                        all_metadata = json.load(f)
                    
                    if name in all_metadata:
                        all_metadata[name]['updated_at'] = datetime.now().isoformat()
                        
                        with open(self.metadata_path, 'w') as f:
                            json.dump(all_metadata, f, default=str)
                    
                    logger.info(f"Appended data to {file_path}, new rows: {len(data)}, total rows: {len(combined_data)}")
                    return True
                else:
                    logger.error(f"Cannot append: either existing data or new data is not a DataFrame")
                    return False
            else:
                # 文件不存在，直接保存
                return self.save_data(name, data)
        except Exception as e:
            logger.error(f"Failed to append data to '{name}': {str(e)}")
            return False 