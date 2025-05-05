# AI量化交易平台

基于人工智能的量化交易平台，支持市场数据分析、策略生成和自动化交易执行。

## 项目概述

本项目旨在构建一个完整的AI驱动量化交易系统，使用先进的机器学习模型对金融市场进行预测，并自动执行交易策略。系统集成了[CCXT](https://github.com/ccxt/ccxt)交易所接口库和高性能预测模型，通过模块化设计提供灵活的交易框架。

### 主要特性

- 多交易所支持：通过CCXT接入主流加密货币交易所
- AI预测模型：集成多种深度学习和机器学习模型
- 策略回测：历史数据策略回测和性能评估
- 实时交易：基于策略信号的自动化交易执行
- 风险管理：内置风险控制和资金管理机制
- Web仪表板：直观的交易监控和系统管理界面

## 系统架构

系统采用模块化、分层架构设计，包含以下核心模块：

1. **数据层**：负责市场数据获取、处理和存储
   - 数据提供者接口(DataProvider)
   - 数据预处理器(DataProcessor)
   - 特征工程(FeatureEngineering)
   - 数据存储(DataStorage)

2. **模型层**：负责预测模型的训练和执行
   - 模型接口(Model)
   - 模型评估器(ModelEvaluator)
   - 各种预测模型实现(LSTM, GRU, Attention等)

3. **策略层**：负责交易信号生成
   - 策略接口(Strategy)
   - 移动平均策略(MovingAverageStrategy)
   - 机器学习预测策略(MLStrategy)

4. **执行层**：负责交易执行和风险管理
   - 交易执行器(TradeExecutor)
   - 订单管理器(OrderManager)
   - 持仓跟踪器(PositionTracker)
   - 风险管理器(RiskManager)

5. **界面层**：提供用户界面和API
   - Web API接口
   - Web仪表板前端

## 安装

### 系统要求

- Python 3.8+
- pip包管理器
- 虚拟环境(推荐)

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ai_trading_platform.git
cd ai_trading_platform
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置系统
```bash
cp configs/config_template.yaml configs/config.yaml
# 编辑config.yaml填入必要的API密钥和配置
```

## 使用指南

### 数据获取

```python
from src.data.ccxt_data_provider import CCXTDataProvider

# 创建数据提供者实例
data_provider = CCXTDataProvider(exchange='binance')

# 获取历史数据
historical_data = data_provider.get_historical_data(
    symbol='BTC/USDT', 
    timeframe='1h',
    since='2023-01-01'
)
```

### 模型训练

```python
from src.models.lstm_model import LSTMModel
from src.data.data_processor import DataProcessor

# 准备数据
processor = DataProcessor()
X_train, X_test, y_train, y_test = processor.prepare_training_data(
    historical_data,
    features=['close', 'volume', 'rsi'],
    target='close',
    window_size=24
)

# 创建和训练模型
model = LSTMModel(input_shape=(X_train.shape[1], X_train.shape[2]))
model.train(X_train, y_train, epochs=50, batch_size=32)
model.evaluate(X_test, y_test)
```

### 策略回测

```python
from src.strategies.ml_strategy import MLStrategy
from src.execution.backtest_engine import BacktestEngine

# 创建策略
strategy = MLStrategy(model=model, data_processor=processor)

# 回测引擎
backtest = BacktestEngine(
    data=historical_data,
    strategy=strategy,
    initial_capital=10000
)

# 运行回测
results = backtest.run_backtest()
backtest.generate_report()
```

### 实时交易

```python
from src.execution.ccxt_trade_executor import CCXTTradeExecutor
from src.execution.risk_manager import RiskManager

# 创建交易执行器
executor = CCXTTradeExecutor(
    exchange='binance',
    api_key='YOUR_API_KEY',
    api_secret='YOUR_API_SECRET'
)

# 风险管理器
risk_manager = RiskManager(max_position_size=0.1)

# 执行交易
order = executor.place_order(
    symbol='BTC/USDT',
    order_type='limit',
    side='buy',
    amount=risk_manager.calculate_position_size(account_balance, 'BTC/USDT'),
    price=50000
)
```

## 贡献指南

欢迎提交Pull Request或Issue。请确保遵循代码规范，并为新功能编写测试。

## 许可证

MIT License 