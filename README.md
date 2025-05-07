# AI交易平台

基于现代Web技术的交易平台应用，支持K线图表展示。

## 项目概述

本项目为一个轻量级的交易平台Web应用，主要功能包括市场数据可视化展示，使用专业级图表进行K线展示。项目前端采用现代Web技术构建，提供流畅的用户体验。

### 主要特性

- **专业图表**：基于Lightweight Charts库的TradingView风格K线图表
- **多语言支持**：支持中英文界面切换
- **响应式设计**：适配不同屏幕尺寸的设备，支持移动端和桌面端

## 系统架构

系统采用简洁的前后端分离设计：

1. **后端（Flask）**：
   - 数据处理层：处理和转换市场数据
   - API层：提供RESTful接口

2. **前端**：
   - 图表组件：基于Lightweight Charts的交易图表
   - 用户界面：响应式界面设计
   - 国际化支持：中英文语言切换功能

## 安装

### 系统要求

- Python 3.8+
- pip包管理器
- Git（可选，用于克隆仓库）

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ai_trading_platform.git
cd ai_trading_platform
```

2. 创建并激活虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 启动应用
```bash
python src/web/flask_app.py
```

5. 访问应用
在浏览器中打开 http://localhost:5000 即可访问应用。

## 使用指南

### 浏览K线图表

1. 从顶部选择交易对（例如：BTC/USDT）
2. 选择时间帧（1分钟到1周）
3. 浏览图表数据

### 切换语言

- 点击右上角的语言切换按钮，可在中文和英文之间切换

## 项目结构

```
ai_trading_platform/
├── src/
│   ├── data/               # 数据处理相关代码
│   │   └── ccxt_data_provider.py
│   │
│   ├── web/                # Web应用相关代码
│       ├── flask_app.py    # Flask应用主文件
│       ├── static/         # 静态资源
│       │   ├── css/        # 样式表
│       │   │   └── style.css
│       │   └── js/         # JavaScript文件
│       │       ├── chart.js    # 图表处理
│       │       ├── layout.js   # 布局控制
│       │       └── i18n.js     # 国际化支持
│       └── templates/      # HTML模板
│           └── index.html  # 主页模板
│
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明
```

## 技术栈

- **后端**：
  - Flask：轻量级Web框架
  - Pandas：数据处理和分析

- **前端**：
  - Bootstrap：响应式UI框架
  - Lightweight Charts：交易图表库
  - jQuery：DOM操作和AJAX请求
  - Font Awesome：图标库

## 未来计划

- 实现图表标注工具
- 添加用户认证和个人设置
- 支持多交易所数据源接入

## 贡献指南

欢迎提交Pull Request或Issue。请确保遵循代码规范，并为新功能编写测试。

## 许可证

MIT License 

## 数据存储服务

项目使用混合数据库策略，包括：

1. **InfluxDB** - 用于存储时间序列市场数据
2. **MongoDB** - 用于存储非结构化数据（如策略配置、模型参数等）
3. **SQLite** - 用于本地开发和测试场景
4. **CSV/Pickle** - 用于数据备份和导出

### 本地开发环境设置

使用Docker Compose快速启动开发环境：

```bash
# 启动所有服务
docker-compose up -d

# 只启动特定服务
docker-compose up -d influxdb mongodb
```

服务默认端口：
- InfluxDB: 8086
- MongoDB: 27017
- MongoDB Express (Web界面): 8081
- Chronograf (InfluxDB Web界面): 8888

### 测试数据库连接

```bash
# 测试InfluxDB连接
python -m tests.integration.test_influxdb_real

# 测试MongoDB连接
python -m tests.integration.test_mongodb_real

# 只有明确设置环境变量时才会执行真实数据库测试
export RUN_REAL_DB_TESTS=true
python -m tests.integration.test_influxdb_real
```

### 下载市场数据

使用内置脚本从交易所下载市场数据：

```bash
# 下载Binance的BTC/USDT过去7天的1小时K线数据
python scripts/download_market_data.py --exchange binance --symbol BTC/USDT --timeframe 1h --days 7

# 下载多个交易对，多个时间周期
python scripts/download_market_data.py --exchange binance --symbol BTC/USDT,ETH/USDT --timeframe 1h,15m

# 指定InfluxDB连接参数
python scripts/download_market_data.py --symbol BTC/USDT --influxdb-host localhost --influxdb-port 8086 --influxdb market_data
```

### 配置文件

数据库连接配置可以在`configs/config.yaml`文件中设置：

```yaml
system:
  storage:
    market_data:
      type: influxdb
      host: localhost
      port: 8086
      username: admin
      password: admin123
      database: market_data
    
    trade_data:
      type: mongodb
      host: localhost
      port: 27017
      username: admin
      password: admin123
      database: trading_platform
``` 