# AI交易平台快速启动指南

本指南将帮助你快速开始使用AI交易平台，包括启动必要的服务、下载数据和使用基本功能。

## 先决条件

- [Docker](https://www.docker.com/get-started) 和 Docker Compose
- Python 3.8+
- Git

## 安装

1. 克隆代码库:

```bash
git clone https://github.com/yourusername/ai_trading_platform.git
cd ai_trading_platform
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

## 启动数据库服务

平台使用混合数据库存储策略:
- InfluxDB 用于时间序列市场数据
- MongoDB 用于非结构化数据(策略配置、模型参数等)

使用Docker Compose启动服务:

```bash
# 启动所有服务(包括web管理界面)
docker-compose up -d

# 或者仅启动必要的数据库服务
docker-compose up -d influxdb mongodb
```

服务启动后可通过以下地址访问管理界面:
- InfluxDB Web界面 (Chronograf): http://localhost:8888
- MongoDB Web界面 (Mongo Express): http://localhost:8081

## 下载市场数据

在使用平台功能前，需要下载市场数据。使用内置脚本从交易所获取数据:

```bash
# 下载Binance的BTC/USDT最近7天的小时级K线数据
python scripts/download_market_data.py --exchange binance --symbol BTC/USDT --timeframe 1h --days 7

# 下载多个交易对和时间周期
python scripts/download_market_data.py --exchange binance --symbol BTC/USDT,ETH/USDT --timeframe 1h,4h,1d --days 30
```

下载的数据将自动保存到InfluxDB中。

## 可视化市场数据

使用Streamlit应用查看和分析市场数据:

```bash
streamlit run apps/market_data_viewer.py
```

应用将自动在浏览器中打开，默认地址: http://localhost:8501

在数据查看器中，你可以:
- 选择不同的交易对和时间周期
- 查看不同时间范围的数据
- 显示各种技术指标(EMA、RSI、MACD、布林带等)
- 下载原始数据进行进一步分析

## 执行集成测试

要验证数据库连接和存储功能是否正常工作，可以运行集成测试:

```bash
# 运行InfluxDB集成测试
export RUN_REAL_DB_TESTS=true
python -m tests.integration.test_influxdb_real

# 运行MongoDB集成测试
export RUN_REAL_DB_TESTS=true
python -m tests.integration.test_mongodb_real
```

## 下一步

完成以上步骤后，你可以:

1. 探索代码库了解系统架构
2. 查看 `configs/config_template.yaml` 了解配置选项
3. 通过 `tests` 目录中的单元测试了解各个组件
4. 在 `src/data` 目录下查看更多数据处理功能

## 故障排除

### 数据库连接问题

如果遇到数据库连接问题，请检查:

1. Docker服务是否正常运行: `docker ps`
2. 数据库容器是否启动: `docker-compose ps`
3. 配置文件中的连接参数是否正确

### 数据下载失败

如果数据下载失败，可能是:

1. 网络连接问题
2. 交易所API限制
3. 交易对或时间周期不受支持

请尝试降低请求频率或更改时间范围。

### 可视化工具无法启动

如果Streamlit应用无法启动，请检查:

1. 依赖是否正确安装: `pip install -r requirements.txt`
2. 是否在项目根目录运行命令
3. 是否有其他服务占用了8501端口 

## 功能概览

- 支持从多个交易所获取行情数据
- 专业级K线图表展示
- 响应式设计，支持移动端和桌面端使用
- 支持自定义图表样式和颜色主题
- 多语言支持（中/英文）

## 界面功能

- **图表区域**：展示K线图表数据
- **时间帧选择**：选择不同的时间周期
- **交易对选择**：选择不同的交易对
- **交易所选择**：选择不同的交易所
- **数据表格**：以表格形式显示最近数据
- **语言切换**：切换界面语言 