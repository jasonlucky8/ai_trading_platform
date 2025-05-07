import os
import pandas as pd
import sqlite3
from typing import List, Dict, Any, Optional, Union
import logging
import json
from datetime import datetime

from src.data.data_storage import DataStorage

logger = logging.getLogger(__name__)


class SQLiteStorage(DataStorage):
    """
    SQLite数据库存储实现
    
    使用SQLite数据库存储数据，每个数据集对应一个表
    """
    
    def __init__(self, database_path: str):
        """
        初始化SQLite存储
        
        参数:
            database_path (str): SQLite数据库文件路径
        """
        self.database_path = database_path
        # 确保目录存在
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        # 初始化元数据表
        self._init_metadata_table()
        logger.info(f"SQLite Storage initialized at {self.database_path}")
    
    def _init_metadata_table(self):
        """初始化元数据表"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 创建元数据表（如果不存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    name TEXT PRIMARY KEY,
                    created_at TEXT,
                    updated_at TEXT,
                    metadata_json TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to initialize metadata table: {str(e)}")
    
    def _table_name(self, name: str) -> str:
        """
        获取安全的表名
        
        参数:
            name (str): 数据集名称
            
        返回:
            str: 安全的表名
        """
        # 替换非法字符
        return f"data_{name.replace('/', '_').replace('-', '_').replace('.', '_')}"
    
    def save_data(self, name: str, data: pd.DataFrame, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到SQLite数据库
        
        参数:
            name (str): 数据集名称
            data (pd.DataFrame): 要保存的数据
            metadata (Dict, optional): 元数据
            
        返回:
            bool: 成功返回True，失败返回False
        """
        try:
            conn = sqlite3.connect(self.database_path)
            
            # 保存数据
            table_name = self._table_name(name)
            data.to_sql(table_name, conn, if_exists='replace', index=True)
            
            # 更新元数据
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            if not metadata:
                metadata = {}
            
            metadata_json = json.dumps(metadata, default=str)
            
            # 检查是否已存在
            cursor.execute("SELECT 1 FROM metadata WHERE name = ?", (name,))
            if cursor.fetchone():
                # 更新
                cursor.execute("""
                    UPDATE metadata
                    SET updated_at = ?, metadata_json = ?
                    WHERE name = ?
                """, (now, metadata_json, name))
            else:
                # 插入
                cursor.execute("""
                    INSERT INTO metadata (name, created_at, updated_at, metadata_json)
                    VALUES (?, ?, ?, ?)
                """, (name, now, now, metadata_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved data to SQLite table {table_name}, rows: {len(data)}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data '{name}': {str(e)}")
            return False
    
    def load_data(self, name: str, query: Optional[Dict] = None) -> pd.DataFrame:
        """
        从SQLite数据库加载数据
        
        参数:
            name (str): 数据集名称
            query (Dict, optional): 查询条件
            
        返回:
            pd.DataFrame: 加载的数据
        """
        try:
            conn = sqlite3.connect(self.database_path)
            
            table_name = self._table_name(name)
            
            # 检查表是否存在
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                logger.warning(f"Table '{table_name}' not found in database")
                conn.close()
                return pd.DataFrame()
            
            # 构建SQL查询
            sql = f"SELECT * FROM {table_name}"
            params = []
            
            if query and len(query) > 0:
                conditions = []
                for key, value in query.items():
                    conditions.append(f"{key} = ?")
                    params.append(value)
                
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)
            
            # 加载数据
            df = pd.read_sql_query(sql, conn, params=params, parse_dates=True)
            
            conn.close()
            
            logger.info(f"Loaded data from SQLite table {table_name}, rows: {len(df)}")
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
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            table_name = self._table_name(name)
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                # 删除表
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # 删除元数据
                cursor.execute("DELETE FROM metadata WHERE name = ?", (name,))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Deleted data table {table_name}")
                return True
            else:
                logger.warning(f"Table '{table_name}' not found for deletion")
                conn.close()
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
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 查询所有以data_开头的表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'data_%'")
            tables = cursor.fetchall()
            
            conn.close()
            
            # 去掉data_前缀
            data_names = [table[0].replace('data_', '', 1) for table in tables]
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
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 查询元数据
            cursor.execute("SELECT metadata_json FROM metadata WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return json.loads(result[0])
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
            conn = sqlite3.connect(self.database_path)
            
            table_name = self._table_name(name)
            
            # 检查表是否存在
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                # 表存在，追加数据
                data.to_sql(table_name, conn, if_exists='append', index=True)
                
                # 更新元数据的更新时间
                now = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE metadata
                    SET updated_at = ?
                    WHERE name = ?
                """, (now, name))
                
                conn.commit()
                conn.close()
                
                logger.info(f"Appended data to SQLite table {table_name}, rows: {len(data)}")
                return True
            else:
                # 表不存在，创建新表
                conn.close()
                return self.save_data(name, data)
        except Exception as e:
            logger.error(f"Failed to append data to '{name}': {str(e)}")
            return False 