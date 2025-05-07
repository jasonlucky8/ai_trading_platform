#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理器

该模块提供了加载和访问配置信息的功能。
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    配置管理器类
    
    负责加载和管理配置信息。
    """
    
    def __init__(self, config_dir: str = "configs"):
        """
        初始化配置管理器
        
        参数:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.yaml")
        self.config = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        返回:
            bool: 是否成功加载
        """
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"配置文件不存在: {self.config_file}")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            logger.info(f"成功加载配置文件: {self.config_file}")
            return True
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return False
    
    def reload_config(self) -> bool:
        """
        重新加载配置文件
        
        返回:
            bool: 是否成功加载
        """
        return self.load_config()
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取完整配置
        
        返回:
            Dict[str, Any]: 配置信息
        """
        return self.config
    
    def get_exchange_config(self, exchange: str) -> Dict[str, Any]:
        """
        获取特定交易所的配置
        
        参数:
            exchange: 交易所名称
            
        返回:
            Dict[str, Any]: 交易所配置信息
        """
        exchanges = self.config.get('exchanges', {})
        return exchanges.get(exchange, {})
    
    def get_database_config(self, db_type: str) -> Dict[str, Any]:
        """
        获取数据库配置
        
        参数:
            db_type: 数据库类型（market_data 或 trade_data）
            
        返回:
            Dict[str, Any]: 数据库配置信息
        """
        storage = self.config.get('system', {}).get('storage', {})
        return storage.get(db_type, {})
    
    def get_strategy_config(self, strategy_type: str) -> Dict[str, Any]:
        """
        获取策略配置
        
        参数:
            strategy_type: 策略类型
            
        返回:
            Dict[str, Any]: 策略配置信息
        """
        strategies = self.config.get('strategies', {})
        return strategies.get(strategy_type, {})
    
    def get_enabled_exchanges(self) -> List[str]:
        """
        获取所有启用的交易所
        
        返回:
            List[str]: 启用的交易所列表
        """
        exchanges = self.config.get('exchanges', {})
        return [name for name, config in exchanges.items() if config.get('enabled', False)]
    
    def get_system_config(self) -> Dict[str, Any]:
        """
        获取系统配置
        
        返回:
            Dict[str, Any]: 系统配置信息
        """
        return self.config.get('system', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        返回:
            Dict[str, Any]: 日志配置信息
        """
        return self.config.get('system', {}).get('logging', {})


# 创建全局配置管理器实例
config_manager = ConfigManager() 