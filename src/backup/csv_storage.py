import os
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime
import json

from src.data.data_storage import DataStorage

logger = logging.getLogger(__name__)


class CSVStorage(DataStorage):
    """
    CSV文件存储实现
    
    使用CSV文件存储数据，每个数据集对应一个CSV文件
    """
    
    def __init__(self, base_path: str):
        """
        初始化CSV存储
        
        参数:
            base_path (str): CSV文件存储的基础路径
        """
        self.base_path = base_path
        # 确保目录存在
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"CSV Storage initialized at {self.base_path}")
    
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
        return os.path.join(self.base_path, f"{safe_name}.csv")
    
    def save_data(self, name: str, data: pd.DataFrame, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到CSV文件
        
        参数:
            name (str): 数据集名称
            data (pd.DataFrame): 要保存的数据
            metadata (Dict, optional): 元数据
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            file_path = self.get_file_path(name)
            
            # 保存元数据（如果提供）
            if metadata:
                metadata_path = file_path.replace('.csv', '.meta.json')
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, default=str)
            
            # 保存数据
            data.to_csv(file_path)
            logger.info(f"Saved data to {file_path}, rows: {len(data)}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data '{name}': {str(e)}")
            return False
    
    def load_data(self, name: str, query: Optional[Dict] = None) -> pd.DataFrame:
        """
        从CSV文件加载数据
        
        参数:
            name (str): 数据集名称
            query (Dict, optional): 查询条件（简单实现可能无法支持复杂查询）
            
        返回:
            pd.DataFrame: 加载的数据
        """
        try:
            file_path = self.get_file_path(name)
            
            if not os.path.exists(file_path):
                logger.warning(f"Data '{name}' not found at {file_path}")
                return pd.DataFrame()
            
            # 读取数据
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            
            # 应用简单查询（如果提供）
            if query:
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
                
                # 删除元数据文件（如果存在）
                metadata_path = file_path.replace('.csv', '.meta.json')
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                    logger.info(f"Deleted metadata file {metadata_path}")
                
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
            files = [f for f in os.listdir(self.base_path) if f.endswith('.csv')]
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
            file_path = self.get_file_path(name)
            metadata_path = file_path.replace('.csv', '.meta.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"No metadata found for '{name}'")
                return {}
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
                existing_data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                # 合并数据
                combined_data = pd.concat([existing_data, data])
                # 去重（假设索引是唯一的）
                combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                # 保存合并后的数据
                combined_data.to_csv(file_path)
                logger.info(f"Appended data to {file_path}, new rows: {len(data)}, total rows: {len(combined_data)}")
                return True
            else:
                # 如果文件不存在，直接保存
                return self.save_data(name, data)
        except Exception as e:
            logger.error(f"Failed to append data to '{name}': {str(e)}")
            return False 