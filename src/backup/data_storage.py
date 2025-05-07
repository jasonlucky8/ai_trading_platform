from abc import ABC, abstractmethod
import pandas as pd
import os
import json
import pickle
from typing import Dict, Optional, Union, List
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


class DataStorage(ABC):
    """
    数据存储接口，定义数据的持久化和检索方法
    """

    @abstractmethod
    def save_data(self, data: pd.DataFrame, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据
        
        参数:
            data: 要保存的数据
            name: 数据名称/标识符
            metadata: 数据的元信息（可选）
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def load_data(self, name: str) -> pd.DataFrame:
        """
        加载数据
        
        参数:
            name: 数据名称/标识符
            
        返回:
            DataFrame: 加载的数据
        """
        pass
    
    @abstractmethod
    def delete_data(self, name: str) -> bool:
        """
        删除数据
        
        参数:
            name: 数据名称/标识符
            
        返回:
            bool: 删除成功返回True，否则返回False
        """
        pass
    
    @abstractmethod
    def list_data(self) -> List[str]:
        """
        列出所有可用的数据
        
        返回:
            List[str]: 数据名称/标识符列表
        """
        pass
    
    @abstractmethod
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据的元信息
        
        参数:
            name: 数据名称/标识符
            
        返回:
            Dict: 数据的元信息
        """
        pass


class CSVStorage(DataStorage):
    """
    使用CSV文件存储数据
    """

    def __init__(self, base_path: str):
        """
        初始化CSV存储
        
        参数:
            base_path: 存储文件的基础路径
        """
        self.base_path = base_path
        self.metadata_file = os.path.join(base_path, "metadata.json")
        
        # 确保目录存在
        os.makedirs(base_path, exist_ok=True)
        
        # 加载或创建元数据文件
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
            self._save_metadata()
    
    def _save_metadata(self) -> bool:
        """
        保存元数据到文件
        
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"保存元数据失败: {str(e)}")
            return False
    
    def save_data(self, data: pd.DataFrame, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到CSV文件
        
        参数:
            data: 要保存的数据
            name: 数据名称/标识符
            metadata: 数据的元信息（可选）
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            if data.empty:
                logger.warning(f"尝试保存空数据: {name}")
                return False
            
            # 确保文件名以.csv结尾
            if not name.endswith('.csv'):
                name = f"{name}.csv"
            
            file_path = os.path.join(self.base_path, name)
            
            # 保存数据
            data.to_csv(file_path)
            
            # 更新元数据
            self.metadata[name] = {
                "rows": len(data),
                "columns": list(data.columns),
                "last_modified": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # 保存元数据
            self._save_metadata()
            
            logger.info(f"成功保存数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False
    
    def load_data(self, name: str) -> pd.DataFrame:
        """
        从CSV文件加载数据
        
        参数:
            name: 数据名称/标识符
            
        返回:
            DataFrame: 加载的数据
        """
        try:
            # 确保文件名以.csv结尾
            if not name.endswith('.csv'):
                name = f"{name}.csv"
            
            file_path = os.path.join(self.base_path, name)
            
            if not os.path.exists(file_path):
                logger.warning(f"数据文件不存在: {file_path}")
                return pd.DataFrame()
            
            # 加载数据
            df = pd.read_csv(file_path)
            
            # 如果第一列是日期或时间戳，将其设置为索引
            if 'timestamp' in df.columns or 'date' in df.columns:
                index_col = 'timestamp' if 'timestamp' in df.columns else 'date'
                df[index_col] = pd.to_datetime(df[index_col])
                df.set_index(index_col, inplace=True)
            elif df.columns[0] == 'Unnamed: 0':
                # 第一列可能是索引，但被保存为普通列
                df.set_index(df.columns[0], inplace=True)
            
            logger.info(f"成功加载数据: {name}")
            return df
        
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return pd.DataFrame()
    
    def delete_data(self, name: str) -> bool:
        """
        删除CSV文件
        
        参数:
            name: 数据名称/标识符
            
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 确保文件名以.csv结尾
            if not name.endswith('.csv'):
                name = f"{name}.csv"
            
            file_path = os.path.join(self.base_path, name)
            
            if not os.path.exists(file_path):
                logger.warning(f"数据文件不存在: {file_path}")
                return False
            
            # 删除文件
            os.remove(file_path)
            
            # 更新元数据
            if name in self.metadata:
                del self.metadata[name]
                self._save_metadata()
            
            logger.info(f"成功删除数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self) -> List[str]:
        """
        列出所有可用的CSV数据文件
        
        返回:
            List[str]: 数据名称/标识符列表
        """
        try:
            files = [f for f in os.listdir(self.base_path) if f.endswith('.csv')]
            return files
        
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据的元信息
        
        参数:
            name: 数据名称/标识符
            
        返回:
            Dict: 数据的元信息
        """
        # 确保文件名以.csv结尾
        if not name.endswith('.csv'):
            name = f"{name}.csv"
        
        return self.metadata.get(name, {})


class SQLiteStorage(DataStorage):
    """
    使用SQLite数据库存储数据
    """

    def __init__(self, database_path: str):
        """
        初始化SQLite存储
        
        参数:
            database_path: SQLite数据库文件路径
        """
        self.database_path = database_path
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        
        # 创建元数据表
        self._create_metadata_table()
    
    def _create_metadata_table(self):
        """创建元数据表"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    name TEXT PRIMARY KEY,
                    rows INTEGER,
                    columns TEXT,
                    last_modified TEXT,
                    extra_metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            logger.error(f"创建元数据表失败: {str(e)}")
    
    def save_data(self, data: pd.DataFrame, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到SQLite数据库
        
        参数:
            data: 要保存的数据
            name: 数据名称/标识符（表名）
            metadata: 数据的元信息（可选）
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            if data.empty:
                logger.warning(f"尝试保存空数据: {name}")
                return False
            
            # 创建连接
            conn = sqlite3.connect(self.database_path)
            
            # 保存数据
            data.to_sql(name, conn, if_exists='replace', index=True)
            
            # 更新元数据
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (name, rows, columns, last_modified, extra_metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                name, 
                len(data), 
                json.dumps(list(data.columns)), 
                datetime.now().isoformat(),
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"成功保存数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False
    
    def load_data(self, name: str) -> pd.DataFrame:
        """
        从SQLite数据库加载数据
        
        参数:
            name: 数据名称/标识符（表名）
            
        返回:
            DataFrame: 加载的数据
        """
        try:
            # 创建连接
            conn = sqlite3.connect(self.database_path)
            
            # 检查表是否存在
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
            if not cursor.fetchone():
                logger.warning(f"数据表不存在: {name}")
                conn.close()
                return pd.DataFrame()
            
            # 加载数据
            df = pd.read_sql(f"SELECT * FROM {name}", conn)
            
            conn.close()
            
            logger.info(f"成功加载数据: {name}")
            return df
        
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return pd.DataFrame()
    
    def delete_data(self, name: str) -> bool:
        """
        从SQLite数据库删除数据表
        
        参数:
            name: 数据名称/标识符（表名）
            
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 创建连接
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
            if not cursor.fetchone():
                logger.warning(f"数据表不存在: {name}")
                conn.close()
                return False
            
            # 删除表
            cursor.execute(f"DROP TABLE IF EXISTS {name}")
            
            # 删除元数据
            cursor.execute("DELETE FROM metadata WHERE name = ?", (name,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"成功删除数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self) -> List[str]:
        """
        列出所有可用的数据表
        
        返回:
            List[str]: 数据表名列表
        """
        try:
            # 创建连接
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 获取所有表名，排除系统表和元数据表
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name != 'metadata' AND name != 'sqlite_sequence'
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            return tables
        
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据的元信息
        
        参数:
            name: 数据名称/标识符（表名）
            
        返回:
            Dict: 数据的元信息
        """
        try:
            # 创建连接
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # 获取元数据
            cursor.execute("""
                SELECT rows, columns, last_modified, extra_metadata 
                FROM metadata WHERE name = ?
            """, (name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {}
            
            return {
                "rows": row[0],
                "columns": json.loads(row[1]),
                "last_modified": row[2],
                **(json.loads(row[3]) if row[3] else {})
            }
        
        except Exception as e:
            logger.error(f"获取元数据失败: {str(e)}")
            return {}


class PickleStorage(DataStorage):
    """
    使用Pickle文件存储数据
    """

    def __init__(self, base_path: str):
        """
        初始化Pickle存储
        
        参数:
            base_path: 存储文件的基础路径
        """
        self.base_path = base_path
        self.metadata_file = os.path.join(base_path, "metadata.json")
        
        # 确保目录存在
        os.makedirs(base_path, exist_ok=True)
        
        # 加载或创建元数据文件
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
            self._save_metadata()
    
    def _save_metadata(self) -> bool:
        """
        保存元数据到文件
        
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"保存元数据失败: {str(e)}")
            return False
    
    def save_data(self, data: pd.DataFrame, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到Pickle文件
        
        参数:
            data: 要保存的数据
            name: 数据名称/标识符
            metadata: 数据的元信息（可选）
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            if data.empty:
                logger.warning(f"尝试保存空数据: {name}")
                return False
            
            # 确保文件名以.pkl结尾
            if not name.endswith('.pkl'):
                name = f"{name}.pkl"
            
            file_path = os.path.join(self.base_path, name)
            
            # 保存数据
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            # 更新元数据
            self.metadata[name] = {
                "rows": len(data),
                "columns": list(data.columns),
                "last_modified": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # 保存元数据
            self._save_metadata()
            
            logger.info(f"成功保存数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False
    
    def load_data(self, name: str) -> pd.DataFrame:
        """
        从Pickle文件加载数据
        
        参数:
            name: 数据名称/标识符
            
        返回:
            DataFrame: 加载的数据
        """
        try:
            # 确保文件名以.pkl结尾
            if not name.endswith('.pkl'):
                name = f"{name}.pkl"
            
            file_path = os.path.join(self.base_path, name)
            
            if not os.path.exists(file_path):
                logger.warning(f"数据文件不存在: {file_path}")
                return pd.DataFrame()
            
            # 加载数据
            with open(file_path, 'rb') as f:
                df = pickle.load(f)
            
            logger.info(f"成功加载数据: {name}")
            return df
        
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            return pd.DataFrame()
    
    def delete_data(self, name: str) -> bool:
        """
        删除Pickle文件
        
        参数:
            name: 数据名称/标识符
            
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 确保文件名以.pkl结尾
            if not name.endswith('.pkl'):
                name = f"{name}.pkl"
            
            file_path = os.path.join(self.base_path, name)
            
            if not os.path.exists(file_path):
                logger.warning(f"数据文件不存在: {file_path}")
                return False
            
            # 删除文件
            os.remove(file_path)
            
            # 更新元数据
            if name in self.metadata:
                del self.metadata[name]
                self._save_metadata()
            
            logger.info(f"成功删除数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self) -> List[str]:
        """
        列出所有可用的Pickle数据文件
        
        返回:
            List[str]: 数据名称/标识符列表
        """
        try:
            files = [f for f in os.listdir(self.base_path) if f.endswith('.pkl')]
            return files
        
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据的元信息
        
        参数:
            name: 数据名称/标识符
            
        返回:
            Dict: 数据的元信息
        """
        # 确保文件名以.pkl结尾
        if not name.endswith('.pkl'):
            name = f"{name}.pkl"
        
        return self.metadata.get(name, {}) 