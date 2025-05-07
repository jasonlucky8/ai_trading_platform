import pandas as pd
import numpy as np
from typing import Dict, Optional, Union, List
import logging
from datetime import datetime, timezone

from influxdb import InfluxDBClient
from src.data.data_storage import DataStorage

logger = logging.getLogger(__name__)


class InfluxDBStorage(DataStorage):
    """
    使用InfluxDB存储时间序列数据
    
    InfluxDB特别适合存储和查询时间序列数据，如市场价格和交易量数据。
    该类实现了DataStorage接口，提供标准的数据持久化和检索方法。
    """

    def __init__(self, host: str = 'localhost', port: int = 8086, 
                 username: str = None, password: str = None, 
                 database: str = 'market_data', ssl: bool = False):
        """
        初始化InfluxDB存储
        
        参数:
            host: InfluxDB服务器主机名
            port: InfluxDB服务器端口
            username: 用户名（可选）
            password: 密码（可选）
            database: 数据库名称
            ssl: 是否使用SSL连接
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.ssl = ssl
        
        # 创建InfluxDB客户端
        try:
            self.client = InfluxDBClient(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                ssl=self.ssl,
                verify_ssl=self.ssl
            )
            
            # 创建数据库（如果不存在）
            databases = self.client.get_list_database()
            if not any(db['name'] == self.database for db in databases):
                self.client.create_database(self.database)
            
            # 切换到指定数据库
            self.client.switch_database(self.database)
            
            logger.info(f"成功连接到InfluxDB数据库: {self.database}")
        
        except Exception as e:
            logger.error(f"连接InfluxDB数据库失败: {str(e)}")
            raise
        
        # 元数据保存在单独的measurement中
        self.metadata_measurement = 'metadata'
        self._create_metadata_measurement()
    
    def _create_metadata_measurement(self):
        """创建元数据measurement（如果不存在）"""
        try:
            # 检查元数据measurement是否存在
            result = self.client.query(f"SHOW MEASUREMENTS WHERE name = '{self.metadata_measurement}'")
            if not list(result.get_points()):
                # 创建一个dummy点以确保measurement存在
                json_body = [
                    {
                        "measurement": self.metadata_measurement,
                        "tags": {
                            "name": "initialization"
                        },
                        "time": datetime.now(timezone.utc).isoformat(),
                        "fields": {
                            "init": True
                        }
                    }
                ]
                self.client.write_points(json_body)
                logger.info(f"创建元数据measurement: {self.metadata_measurement}")
        
        except Exception as e:
            logger.error(f"创建元数据measurement失败: {str(e)}")
    
    def save_data(self, data: pd.DataFrame, name: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存数据到InfluxDB
        
        参数:
            data: 要保存的数据
            name: 数据名称/标识符（measurement名称）
            metadata: 数据的元信息（可选）
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            if data.empty:
                logger.warning(f"尝试保存空数据: {name}")
                return False
            
            # 确保dataframe有时间索引
            if not isinstance(data.index, pd.DatetimeIndex):
                logger.warning("DataFrame没有时间索引，尝试转换")
                if 'timestamp' in data.columns:
                    data.set_index('timestamp', inplace=True)
                    data.index = pd.to_datetime(data.index)
                else:
                    logger.error("DataFrame没有时间索引且无法转换")
                    return False
            
            # 确保索引具有UTC时区
            if data.index.tzinfo is None:
                data.index = data.index.tz_localize('UTC')
            
            # 准备InfluxDB数据点
            json_body = []
            
            for timestamp, row in data.iterrows():
                # 将非数值列作为tags，数值列作为fields
                fields = {}
                tags = {}
                
                for column, value in row.items():
                    if pd.api.types.is_numeric_dtype(type(value)):
                        # InfluxDB不接受NaN值，将其转换为None
                        if pd.isna(value):
                            fields[column] = None
                        else:
                            fields[column] = float(value)
                    else:
                        # 非数值列作为tags（如交易对符号）
                        if pd.notna(value):
                            tags[column] = str(value)
                
                # 只有当fields非空时才添加数据点
                if fields:
                    point = {
                        "measurement": name,
                        "tags": tags,
                        "time": timestamp.isoformat(),
                        "fields": fields
                    }
                    json_body.append(point)
            
            # 写入数据
            if json_body:
                self.client.write_points(json_body)
            
            # 保存元数据
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "rows": len(data),
                "columns": list(data.columns),
                "last_modified": datetime.now(timezone.utc).isoformat()
            })
            
            metadata_point = {
                "measurement": self.metadata_measurement,
                "tags": {
                    "name": name
                },
                "time": datetime.now(timezone.utc).isoformat(),
                "fields": {
                    "metadata": str(metadata)
                }
            }
            
            self.client.write_points([metadata_point])
            
            logger.info(f"成功保存数据: {name}, 行数: {len(data)}")
            return True
        
        except Exception as e:
            logger.error(f"保存数据到InfluxDB失败: {str(e)}")
            return False
    
    def load_data(self, name: str) -> pd.DataFrame:
        """
        从InfluxDB加载数据
        
        参数:
            name: 数据名称/标识符（measurement名称）
            
        返回:
            DataFrame: 加载的数据
        """
        try:
            # 查询数据
            query = f'SELECT * FROM "{name}"'
            result = self.client.query(query)
            
            if not result:
                logger.warning(f"未找到数据: {name}")
                return pd.DataFrame()
            
            # 将结果转换为DataFrame
            df = pd.DataFrame(list(result.get_points()))
            
            if df.empty:
                logger.warning(f"加载的数据为空: {name}")
                return df
            
            # 设置时间索引
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'], utc=True)
                df.set_index('time', inplace=True)
            
            logger.info(f"成功加载数据: {name}, 行数: {len(df)}")
            return df
        
        except Exception as e:
            logger.error(f"从InfluxDB加载数据失败: {str(e)}")
            return pd.DataFrame()
    
    def delete_data(self, name: str) -> bool:
        """
        从InfluxDB删除数据
        
        参数:
            name: 数据名称/标识符（measurement名称）
            
        返回:
            bool: 删除成功返回True，否则返回False
        """
        try:
            # 删除measurement
            query = f'DROP MEASUREMENT "{name}"'
            self.client.query(query)
            
            # 删除元数据
            delete_query = f'DELETE FROM "{self.metadata_measurement}" WHERE "name" = \'{name}\''
            self.client.query(delete_query)
            
            logger.info(f"成功删除数据: {name}")
            return True
        
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self) -> List[str]:
        """
        列出所有可用的数据（measurements）
        
        返回:
            List[str]: 数据名称/标识符列表
        """
        try:
            # 查询所有measurements
            result = self.client.query("SHOW MEASUREMENTS")
            measurements = [m['name'] for m in result.get_points()]
            
            # 排除元数据measurement
            if self.metadata_measurement in measurements:
                measurements.remove(self.metadata_measurement)
            
            return measurements
        
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_metadata(self, name: str) -> Dict:
        """
        获取数据的元信息
        
        参数:
            name: 数据名称/标识符（measurement名称）
            
        返回:
            Dict: 数据的元信息
        """
        try:
            # 查询元数据
            query = f'SELECT * FROM "{self.metadata_measurement}" WHERE "name" = \'{name}\' ORDER BY time DESC LIMIT 1'
            result = self.client.query(query)
            
            if not result:
                logger.warning(f"未找到元数据: {name}")
                return {}
            
            # 解析元数据
            points = list(result.get_points())
            if not points:
                return {}
            
            metadata_str = points[0].get('metadata', '{}')
            # 将字符串转换为字典
            import ast
            metadata = ast.literal_eval(metadata_str)
            
            return metadata
        
        except Exception as e:
            logger.error(f"获取元数据失败: {str(e)}")
            return {}
    
    def close(self):
        """关闭InfluxDB连接"""
        try:
            self.client.close()
            logger.info("InfluxDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭InfluxDB连接失败: {str(e)}")
    
    def __del__(self):
        """析构函数，确保连接被关闭"""
        try:
            self.close()
        except:
            pass

    def get_measurement_names(self) -> List[str]:
        """
        获取数据库中所有的measurement名称
        
        返回:
            List[str]: measurement名称列表
        """
        try:
            result = self.client.query("SHOW MEASUREMENTS")
            measurements = [item['name'] for item in result.get_points()]
            return measurements
        except Exception as e:
            logger.error(f"获取measurement列表失败: {str(e)}")
            return [] 