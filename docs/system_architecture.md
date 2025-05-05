# AI量化交易平台系统架构

## 1. 系统概述

AI量化交易平台是一个基于人工智能的量化交易系统，旨在利用机器学习模型自动分析市场数据，生成交易信号，并执行交易策略。系统采用模块化设计，具有高度可扩展性和可定制性，支持多种交易所和交易品种。

### 1.1 设计理念

- **模块化**: 系统被划分为功能独立的模块，每个模块负责特定的功能，通过明确的接口进行通信。
- **可扩展性**: 各模块通过接口抽象，便于添加新的实现，如新的数据源、预测模型或交易策略。
- **可维护性**: 采用高内聚、低耦合的设计原则，使代码易于维护和测试。
- **安全性**: 交易执行模块包含风险管理机制，防止意外损失。
- **性能**: 关键组件优化以处理大量数据和实时交易需求。

## 2. 系统架构

系统采用分层架构设计，包含以下五个核心层：

1. **数据层**：负责市场数据获取、处理和存储
2. **模型层**：负责预测模型的训练和执行
3. **策略层**：负责交易信号生成
4. **执行层**：负责交易执行和风险管理
5. **界面层**：提供用户界面和API

### 2.1 模块划分图

```
+------------------+    +------------------+    +------------------+
|    界面层        |    |                  |    |                  |
|  Interface Layer |    |   Web Dashboard  |    |    REST API      |
+------------------+    +------------------+    +------------------+
         |                       |                      |
         v                       v                      v
+------------------+    +------------------+    +------------------+
|    执行层        |    |                  |    |                  |
| Execution Layer  |<-->| Risk Management |<-->| Order Management |
+------------------+    +------------------+    +------------------+
         |                                             |
         v                                             v
+------------------+    +------------------+    +------------------+
|    策略层        |    |                  |    |                  |
|  Strategy Layer  |<-->|  ML Strategies   |<-->| Classic Strategies|
+------------------+    +------------------+    +------------------+
         |                       |                      |
         v                       v                      v
+------------------+    +------------------+    +------------------+
|    模型层        |    |                  |    |                  |
|   Model Layer    |<-->|  Model Training  |<-->| Model Evaluation |
+------------------+    +------------------+    +------------------+
         |                       |                      |
         v                       v                      v
+------------------+    +------------------+    +------------------+
|    数据层        |    |                  |    |                  |
|   Data Layer     |<-->| Data Processing  |<-->|  Data Storage    |
+------------------+    +------------------+    +------------------+
         |                       |                      |
         v                       v                      v
+------------------+    +------------------+    +------------------+
|   外部数据源     |    |                  |    |                  |
| External Sources |    |     CCXT API     |    |   Market Data    |
+------------------+    +------------------+    +------------------+
```

## 3. 模块详细设计

### 3.1 数据层 (Data Layer)

数据层负责从各种来源获取市场数据，进行预处理和存储。

#### 3.1.1 核心组件

- **DataProvider**: 数据提供者接口，负责从交易所或其他来源获取市场数据
  - `CCXTDataProvider`: 使用CCXT库连接各大交易所获取数据
  - `CSVDataProvider`: 从CSV文件读取历史数据
  - `APIDataProvider`: 从第三方API获取数据

- **DataProcessor**: 数据预处理器，负责清洗、标准化和转换原始市场数据
  - `clean_data()`: 清除缺失值和异常值
  - `normalize_data()`: 数据标准化
  - `resample_data()`: 数据重采样（改变时间帧）
  - `split_data()`: 划分训练集和测试集

- **FeatureEngineering**: 特征工程模块，计算技术指标
  - `add_moving_averages()`: 添加移动平均线
  - `add_macd()`: 添加MACD指标
  - `add_rsi()`: 添加RSI指标
  - `add_bollinger_bands()`: 添加布林带
  - `add_all_features()`: 添加所有标准指标

- **DataStorage**: 数据存储接口，负责数据的持久化和检索
  - `CSVStorage`: 文件系统存储实现
  - `DatabaseStorage`: 数据库存储实现（SQLite/MongoDB等）

#### 3.1.2 数据流

1. `DataProvider`从外部数据源获取原始市场数据
2. `DataProcessor`对原始数据进行清洗和预处理
3. `FeatureEngineering`计算各种技术指标，生成特征
4. `DataStorage`将处理后的数据存储至持久化存储

### 3.2 模型层 (Model Layer)

模型层负责预测模型的训练、评估和预测。

#### 3.2.1 核心组件

- **Model**: 模型接口，定义所有预测模型的通用接口
  - `BaseModel`: 实现模型接口的通用功能
  - `LSTMModel`: LSTM神经网络模型实现
  - `GRUModel`: GRU神经网络模型实现
  - `AttentionModel`: 基于Attention机制的模型实现

- **ModelFactory**: 模型工厂，负责创建模型实例
  - `create_model()`: 根据配置创建模型实例

- **ModelRegistry**: 模型注册表，管理可用模型
  - `register_model()`: 注册新模型
  - `get_model()`: 获取模型实例

- **ModelEvaluator**: 模型评估器，评估模型性能
  - `evaluate_accuracy()`: 评估模型准确率
  - `evaluate_rmse()`: 评估均方根误差
  - `evaluate_sharpe()`: 评估夏普比率
  - `evaluate_trading_performance()`: 评估交易表现
  - `compare_models()`: 比较多个模型

#### 3.2.2 数据流

1. `Model`从数据层获取处理好的训练数据
2. 模型进行训练和验证
3. `ModelEvaluator`评估模型性能
4. 训练好的模型被保存并用于预测

### 3.3 策略层 (Strategy Layer)

策略层负责根据模型预测或技术指标生成交易信号。

#### 3.3.1 核心组件

- **Strategy**: 策略接口，定义所有交易策略的通用接口
  - `BaseStrategy`: 实现策略接口的通用功能
  - `MovingAverageStrategy`: 基于移动平均的策略实现
  - `MLStrategy`: 基于机器学习模型的策略实现

- **StrategyFactory**: 策略工厂，负责创建策略实例
  - `create_strategy()`: 根据配置创建策略实例

- **StrategyRegistry**: 策略注册表，管理可用策略
  - `register_strategy()`: 注册新策略
  - `get_strategy()`: 获取策略实例

#### 3.3.2 数据流

1. `Strategy`从数据层获取市场数据和指标
2. 对于`MLStrategy`，调用模型层获取预测结果
3. 根据预测结果或技术指标生成交易信号
4. 交易信号传递给执行层

### 3.4 执行层 (Execution Layer)

执行层负责根据策略信号执行交易，并管理订单和持仓。

#### 3.4.1 核心组件

- **TradeExecutor**: 交易执行器接口，负责与交易所交互执行交易
  - `CCXTTradeExecutor`: 使用CCXT库连接交易所执行交易

- **OrderManager**: 订单管理器，负责管理订单的生命周期
  - `create_order()`: 创建新订单
  - `update_order()`: 更新订单状态
  - `cancel_order()`: 取消订单
  - `get_order_status()`: 获取订单状态
  - `get_open_orders()`: 获取未成交订单

- **PositionTracker**: 持仓跟踪器，负责跟踪和管理交易持仓
  - `update_position()`: 更新持仓
  - `get_position()`: 获取当前持仓
  - `calculate_pnl()`: 计算盈亏

- **RiskManager**: 风险管理器，负责控制交易风险
  - `check_order_risk()`: 检查订单风险
  - `calculate_position_size()`: 计算仓位大小
  - `set_stop_loss()`: 设置止损
  - `check_portfolio_risk()`: 检查组合风险

- **BacktestEngine**: 回测引擎，负责模拟和回测交易策略
  - `run_backtest()`: 运行回测
  - `evaluate_performance()`: 评估策略性能
  - `generate_report()`: 生成回测报告
  - `visualize_results()`: 可视化回测结果

#### 3.4.2 数据流

1. `TradeExecutor`接收来自策略层的交易信号
2. `RiskManager`检查交易风险并计算合适的仓位大小
3. `OrderManager`创建并管理订单
4. `PositionTracker`跟踪持仓变化和计算收益

### 3.5 界面层 (Interface Layer)

界面层为用户提供交互界面，包括Web仪表板和API接口。

#### 3.5.1 核心组件

- **WebAPI**: Web API服务，提供REST API接口
  - `/api/market-data`: 市场数据相关API
  - `/api/models`: 模型管理API
  - `/api/strategies`: 策略管理API
  - `/api/trading`: 交易执行相关API
  - `/api/config`: 配置管理API

- **WebDashboard**: Web仪表板前端，提供可视化界面
  - 登录和用户管理页面
  - 仪表板总览页面
  - 市场数据监控页面
  - 模型管理和预测结果页面
  - 策略配置和执行页面
  - 交易管理和记录页面
  - 系统配置页面

- **ConfigManager**: 配置管理器，管理系统配置和用户偏好设置
  - `load_config()`: 加载配置
  - `save_config()`: 保存配置
  - `get_setting()`: 获取配置项
  - `update_setting()`: 更新配置项

#### 3.5.2 数据流

1. 用户通过Web仪表板或API接口发送请求
2. 请求被处理并传递到相应的模块
3. 模块返回结果
4. 结果通过Web仪表板或API接口返回给用户

## 4. 系统数据流

### 4.1 总体数据流程图

```
+-------------+     +-------------+     +-------------+
| 数据采集    |---->| 数据处理    |---->| 特征工程    |
+-------------+     +-------------+     +-------------+
                                              |
                                              v
+-------------+     +-------------+     +-------------+
| 交易执行    |<----| 策略生成    |<----| 模型预测    |
+-------------+     +-------------+     +-------------+
      |
      v
+-------------+     +-------------+
| 订单管理    |---->| 持仓跟踪    |
+-------------+     +-------------+
      |                   |
      v                   v
+----------------------------------+
|           性能评估              |
+----------------------------------+
                |
                v
+----------------------------------+
|           用户界面              |
+----------------------------------+
```

### 4.2 具体流程说明

1. **数据采集流程**:
   - 系统定期从交易所API获取市场数据
   - 数据包括价格、交易量、订单簿等信息
   - 数据被存储到本地数据库或文件系统

2. **数据处理流程**:
   - 原始数据被清洗，处理缺失值和异常值
   - 数据进行标准化处理
   - 根据需要进行重采样（如将分钟数据转换为小时数据）

3. **特征工程流程**:
   - 计算各种技术指标（如移动平均线、RSI、MACD等）
   - 生成模型所需特征
   - 准备训练数据集和测试数据集

4. **模型训练与预测流程**:
   - 使用处理好的数据训练预测模型
   - 对模型进行评估和优化
   - 使用模型对未来价格或趋势进行预测

5. **策略生成流程**:
   - 根据模型预测或技术指标生成交易信号
   - 信号包括交易方向、时机和规模
   - 策略可以是基于规则的或基于机器学习的

6. **交易执行流程**:
   - 风险管理器检查交易风险
   - 计算适当的仓位大小
   - 创建交易订单并发送到交易所
   - 监控订单状态并更新持仓信息

7. **性能评估流程**:
   - 计算交易策略的各种性能指标
   - 包括收益率、夏普比率、最大回撤等
   - 生成性能报告和可视化图表

## 5. 技术栈选择

### 5.1 核心技术

| 类别 | 技术选择 | 选择理由 |
|------|----------|----------|
| 编程语言 | Python | Python在数据科学、机器学习和量化交易领域有丰富的库和社区支持 |
| 数据处理 | pandas, numpy | 高效的数据处理和数值计算库，适合大规模金融数据处理 |
| 机器学习 | TensorFlow, PyTorch | 主流深度学习框架，支持复杂模型开发和GPU加速 |
| 回测框架 | 自定义实现 | 更灵活地适应项目特定需求，便于与其他模块集成 |
| 交易接口 | CCXT | 支持多个加密货币交易所的统一API接口 |
| Web框架 | FastAPI | 高性能异步API框架，适合构建实时交易系统 |
| 前端技术 | React | 流行的前端框架，适合构建复杂的单页应用 |
| 数据存储 | SQLite, MongoDB, InfluxDB | 关系型和非关系型数据库结合，满足不同数据存储需求 |

### 5.2 技术选择理由

- **Python**: Python在金融科技领域被广泛使用，提供了丰富的数据处理和机器学习库，如pandas、numpy、scikit-learn、TensorFlow等。

- **CCXT**: CCXT库提供了统一的API接口连接多个加密货币交易所，简化了交易所集成工作，支持市场数据获取和交易执行。

- **TensorFlow/PyTorch**: 这两个深度学习框架功能强大，支持各种复杂模型的开发，包括LSTM、GRU和Transformer模型，适合时间序列预测。

- **FastAPI**: FastAPI是一个现代化的高性能Web框架，支持异步请求处理，适合构建实时交易系统的API服务。

- **React**: React是一个流行的前端框架，适合构建复杂的单页应用，提供良好的用户体验。

- **混合数据库**: 使用不同类型的数据库满足不同需求：
  - SQLite用于轻量级的关系型数据存储
  - MongoDB用于灵活的文档存储（如交易策略配置）
  - InfluxDB用于高效的时序数据存储（如市场数据）

## 6. 接口定义

### 6.1 模块接口

#### 6.1.1 DataProvider接口

```python
class DataProvider(ABC):
    @abstractmethod
    def get_historical_data(self, symbol, timeframe, since, limit=None):
        """
        获取历史市场数据
        
        参数:
            symbol: 交易对符号，如'BTC/USDT'
            timeframe: 时间帧，如'1m', '1h', '1d'
            since: 起始时间
            limit: 数据点数量限制
            
        返回:
            DataFrame: 包含市场数据的DataFrame
        """
        pass
    
    @abstractmethod
    def get_live_data(self, symbol, timeframe):
        """
        获取实时市场数据
        
        参数:
            symbol: 交易对符号
            timeframe: 时间帧
            
        返回:
            DataFrame: 包含最新市场数据的DataFrame
        """
        pass
    
    @abstractmethod
    def get_orderbook(self, symbol, limit=None):
        """
        获取订单簿数据
        
        参数:
            symbol: 交易对符号
            limit: 订单数量限制
            
        返回:
            Dict: 包含买单和卖单的字典
        """
        pass
```

#### 6.1.2 Model接口

```python
class Model(ABC):
    @abstractmethod
    def train(self, X_train, y_train, **kwargs):
        """
        训练模型
        
        参数:
            X_train: 训练特征数据
            y_train: 训练目标数据
            **kwargs: 其他训练参数
            
        返回:
            None
        """
        pass
    
    @abstractmethod
    def predict(self, X):
        """
        使用模型进行预测
        
        参数:
            X: 预测特征数据
            
        返回:
            ndarray: 预测结果
        """
        pass
    
    @abstractmethod
    def evaluate(self, X_test, y_test):
        """
        评估模型性能
        
        参数:
            X_test: 测试特征数据
            y_test: 测试目标数据
            
        返回:
            Dict: 包含评估指标的字典
        """
        pass
    
    @abstractmethod
    def save(self, path):
        """
        保存模型到指定路径
        
        参数:
            path: 保存路径
            
        返回:
            None
        """
        pass
    
    @abstractmethod
    def load(self, path):
        """
        从指定路径加载模型
        
        参数:
            path: 模型路径
            
        返回:
            None
        """
        pass
```

#### 6.1.3 Strategy接口

```python
class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, data):
        """
        根据数据生成交易信号
        
        参数:
            data: 市场数据和指标
            
        返回:
            DataFrame: 包含交易信号的DataFrame
        """
        pass
    
    @abstractmethod
    def optimize_parameters(self, data, **kwargs):
        """
        优化策略参数
        
        参数:
            data: 用于优化的历史数据
            **kwargs: 优化参数
            
        返回:
            Dict: 优化后的参数
        """
        pass
```

#### 6.1.4 TradeExecutor接口

```python
class TradeExecutor(ABC):
    @abstractmethod
    def place_order(self, symbol, order_type, side, amount, price=None):
        """
        下单
        
        参数:
            symbol: 交易对符号
            order_type: 订单类型，如'market', 'limit'
            side: 交易方向，'buy'或'sell'
            amount: 交易数量
            price: 价格（limit订单需要）
            
        返回:
            Dict: 订单信息
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id, symbol=None):
        """
        取消订单
        
        参数:
            order_id: 订单ID
            symbol: 交易对符号
            
        返回:
            Dict: 取消结果
        """
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol=None):
        """
        获取未成交订单
        
        参数:
            symbol: 交易对符号（可选）
            
        返回:
            List: 未成交订单列表
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol):
        """
        获取持仓信息
        
        参数:
            symbol: 交易对符号
            
        返回:
            Dict: 持仓信息
        """
        pass
```

### 6.2 API接口

#### 6.2.1 市场数据API

- `GET /api/market-data/symbols`: 获取支持的交易对列表
- `GET /api/market-data/historical?symbol={symbol}&timeframe={timeframe}&since={since}&limit={limit}`: 获取历史市场数据
- `GET /api/market-data/live?symbol={symbol}&timeframe={timeframe}`: 获取实时市场数据
- `GET /api/market-data/orderbook?symbol={symbol}&limit={limit}`: 获取订单簿数据

#### 6.2.2 模型API

- `GET /api/models/list`: 获取可用模型列表
- `POST /api/models/train`: 训练模型
- `POST /api/models/predict`: 使用模型进行预测
- `POST /api/models/evaluate`: 评估模型性能
- `GET /api/models/{model_id}`: 获取模型详情

#### 6.2.3 策略API

- `GET /api/strategies/list`: 获取可用策略列表
- `POST /api/strategies/backtest`: 回测策略
- `POST /api/strategies/optimize`: 优化策略参数
- `GET /api/strategies/{strategy_id}`: 获取策略详情
- `POST /api/strategies/generate-signals`: 生成交易信号

#### 6.2.4 交易API

- `POST /api/trading/place-order`: 下单
- `POST /api/trading/cancel-order`: 取消订单
- `GET /api/trading/open-orders`: 获取未成交订单
- `GET /api/trading/positions`: 获取持仓信息
- `GET /api/trading/account-balance`: 获取账户余额

#### 6.2.5 配置API

- `GET /api/config/all`: 获取所有配置
- `GET /api/config/{category}`: 获取特定类别的配置
- `POST /api/config/update`: 更新配置

## 7. 架构决策记录 (ADR)

### ADR-001: 使用Python作为主要开发语言

- **状态**: 已接受
- **背景**: 需要选择一种适合AI量化交易系统开发的编程语言。
- **决策**: 采用Python作为主要开发语言。
- **理由**: Python在数据科学、机器学习和量化交易领域有丰富的库和社区支持。主要库包括pandas、numpy、scikit-learn、TensorFlow等，能够满足数据处理和模型训练的需求。
- **影响**: 系统开发效率高，但可能在性能要求极高的场景下需要考虑部分模块使用C++或其他高性能语言实现。

### ADR-002: 使用CCXT库连接加密货币交易所

- **状态**: 已接受
- **背景**: 需要一种统一方式连接不同的加密货币交易所。
- **决策**: 采用CCXT库作为交易所连接的中间层。
- **理由**: CCXT提供了统一的API接口连接100多个加密货币交易所，简化了交易所集成工作，支持市场数据获取和交易执行。
- **影响**: 简化了对多交易所的支持，但对于某些交易所特有的功能可能需要额外开发。

### ADR-003: 采用分层架构设计

- **状态**: 已接受
- **背景**: 需要一种清晰的架构设计来组织系统各模块。
- **决策**: 采用五层架构：数据层、模型层、策略层、执行层和界面层。
- **理由**: 分层架构使系统各部分职责明确，便于开发和维护。各层之间通过定义良好的接口通信，减少耦合。
- **影响**: 系统结构清晰，但可能增加一些通信开销。

### ADR-004: 使用FastAPI构建Web服务

- **状态**: 已接受
- **背景**: 需要选择一个Web框架来构建系统的API服务。
- **决策**: 采用FastAPI作为Web框架。
- **理由**: FastAPI是一个现代化的高性能Web框架，支持异步请求处理，自动生成API文档，适合构建实时交易系统的API服务。
- **影响**: 提高了API服务的性能和开发效率，但团队需要学习新框架。

### ADR-005: 使用混合数据库策略

- **状态**: 已接受
- **背景**: 系统需要存储不同类型的数据，包括市场数据、模型参数、交易记录等。
- **决策**: 使用混合数据库策略，包括SQLite、MongoDB和InfluxDB。
- **理由**: 不同类型的数据库适合不同类型的数据：
  - SQLite: 轻量级关系型数据，适合交易记录和系统配置
  - MongoDB: 灵活的文档存储，适合模型参数和策略配置
  - InfluxDB: 高效的时序数据库，适合市场数据
- **影响**: 能够更好地适应不同数据的存储需求，但增加了系统复杂性。

### ADR-006: 客户端-服务器分离架构

- **状态**: 已接受
- **背景**: 需要选择前端与后端的架构模式。
- **决策**: 采用客户端-服务器分离架构，前端使用React，后端提供REST API。
- **理由**: 分离架构使前端和后端可以独立开发和部署，提高开发效率。React适合构建复杂的单页应用，提供良好的用户体验。
- **影响**: 开发效率提高，但需要维护两个独立的代码库。 