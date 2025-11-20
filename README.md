# 多维度量化交易系统 (Multi-Dimensional Quant Trading System)

本项目是一个**全方位智能投资决策系统**,整合了7大类数据源,为TSLA、NVDA、INTC等股票提供自动化交易策略和综合投资分析。

## 🎯 项目特色
- **多维度数据**: 整合价格、新闻、基本面、期权、宏观、社交媒体、内部人交易7类数据
- **智能评分**: 自动计算综合投资评分(0-100),提供买入/持有/观望建议
- **全自动化**: 每日自动执行策略、发送邮件报告、Windows任务调度
- **多股票支持**: 同时监控TSLA、NVDA、INTC三只科技股
- **可扩展架构**: 模块化设计,易于添加新策略、新股票、新数据源Quant Trading Automation

本项目旨在构建一个针对特斯拉（NASDAQ: TSLA）的自动化量化交易系统，满足“每周进行两次交易”的节奏，在实现稳定收益的同时控制风险。

## 🎯 项目目标
- 自动生成交易信号、下单执行、绩效评估，形成可靠闭环。
- 支持回测、模拟盘与实盘的逐步过渡。
- 具备可扩展的架构，方便未来加入新策略、标的或风控逻辑。

## 🏗️ 系统架构
```
┌─────────────────────────────────────────────────────────┐
│                   统一数据源层                            │
│  价格 | 新闻情绪 | 基本面 | 期权 | 宏观 | 社交 | 内部人    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              综合分析与评分系统                           │
│  多维度数据聚合 → 智能评分算法 → 投资建议生成            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               策略执行与风控层                            │
│  动量策略 | 仓位管理 | 风险控制 | 自动交易                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            监控报告与通知系统                             │
│  邮件通知 | HTML报告 | 任务调度 | 性能监控                │
└─────────────────────────────────────────────────────────┘
```

## 📂 项目目录结构
```
QT/
├── README.md
├── requirements.txt
├── .env.template                    # ✨ API密钥配置模板
├── MULTI_DATA_SOURCES_COMPLETION.md # ✨ 多数据源完成报告
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   ├── backtest_report.md
│   ├── alphavantage_setup.md
│   ├── multi_data_sources.md
│   └── MULTI_DIMENSIONAL_DATA_SOURCES_GUIDE.md  # ✨ 完整使用指南
├── src/
│   ├── data/
│   │   ├── providers.py              # Yahoo Finance价格数据
│   │   ├── alphavantage.py           # Alpha Vantage备用数据
│   │   ├── news_sentiment.py         # ✨ 新闻情绪分析
│   │   ├── fundamentals.py           # ✨ 基本面财报数据
│   │   ├── options_data.py           # ✨ 期权衍生品数据
│   │   ├── macro_data.py             # ✨ 宏观经济数据
│   │   ├── social_sentiment.py       # ✨ 社交媒体情绪
│   │   ├── insider_trading.py        # ✨ 内部人交易数据
│   │   └── unified_provider.py       # ✨ 统一数据源管理器
│   ├── signals/
│   │   └── momentum.py               # 动量策略
│   ├── portfolio/
│   │   └── allocator.py              # 仓位管理
│   ├── execution/
│   │   └── mock_broker.py            # 模拟交易
│   ├── backtest/                     # 回测引擎
│   │   ├── engine.py
│   │   └── metrics.py
│   ├── pipeline/                     # 策略执行管道
│   │   ├── run_daily_check_email.py      # TSLA日度策略
│   │   ├── run_daily_check_email_nvda.py # NVDA日度策略
│   │   └── run_daily_check_email_intc.py # INTC日度策略
│   └── notification/
│       └── email_service.py          # 邮件通知服务
├── examples/
│   └── multi_data_sources_demo.py    # ✨ 多数据源使用示例
├── backtest_results/                 # 回测结果
├── data/                             # 历史数据
└── reports/                          # ✨ 综合分析报告
```
│   │   └── visualizer.py
│   └── pipeline/
│       ├── run_once.py
│       ├── run_backtest.py         ⭐ 回测脚本
│       ├── update_data.py
│       └── fetch_alphavantage.py
├── tests/
│   ├── test_signals.py
│   ├── test_alphavantage.py
│   └── test_backtest.py            ⭐ 回测测试
├── data/
│   └── sample_tsla.csv
├── backtest_results/               ⭐ 回测结果
│   ├── equity_curve.csv
│   ├── trades.csv
│   ├── metrics.txt
│   └── charts/
│       ├── equity_curve.png
│       ├── drawdown.png
│       ├── monthly_returns.png
│       └── trades_distribution.png
├── requirements.txt
└── 需求.txt
```

## 🌟 核心功能

### 1️⃣ 七大类数据源整合
| 数据类型 | 数据源 | 用途 | 免费版限制 |
|---------|--------|------|-----------|
| **价格数据** | Yahoo Finance, Alpha Vantage | 历史行情、实时报价 | 频率限制 / 500次/天 |
| **新闻情绪** | NewsAPI, Finnhub | 实时新闻、情绪分析 | 100次/天 / 60次/分钟 |
| **基本面** | FMP, Alpha Vantage | 财报、估值指标 | 250次/天 / 共享配额 |
| **期权数据** | Tradier, Yahoo Finance | 期权链、Put/Call比率 | 沙盒免费 / 无限制 |
| **宏观经济** | FRED, World Bank | 利率、GDP、CPI | 无限制 |
| **社交媒体** | Reddit, StockTwits | 散户情绪、热度 | 无限制 |
| **内部人交易** | SEC EDGAR, FMP | 高管买卖行为 | 无限制 / 共享配额 |

### 2️⃣ 综合投资评分系统
- **智能评分**: 基于7类数据源的加权评分(0-100分)
- **评级建议**: A(强烈买入) → B(买入) → C(持有) → D(观望) → F(谨慎)
- **权重配置**: 基本面25% + 新闻15% + 社交15% + 期权15% + 内部人15% + 宏观15%

### 3️⃣ 自动化交易策略
- **动量策略**: 5日/20日双均线系统
- **多股票**: 同时监控TSLA、NVDA、INTC
- **每日执行**: 自动检查信号、发送邮件报告
- **仓位管理**: 显示当前持仓、盈亏情况

### 4️⃣ 全自动运行
- **Windows任务调度**: 每周一至周五 08:00 自动执行
- **邮件通知**: 多账户failover(QQ→Gmail→139)
- **HTML报告**: 包含交易信号、持仓信息、图表

## 🚀 快速开始

### 方式A: 使用现有策略系统(推荐)

#### 1. 安装依赖
```powershell
pip install -r requirements.txt
```

#### 2. 配置API密钥(可选)
```powershell
# 复制配置模板
Copy-Item .env.template .env

# 编辑.env文件,填入API密钥
# 基础功能只需要ALPHAVANTAGE_API_KEY
# 高级功能需要其他API密钥
```

#### 3. 运行日度策略检查
```powershell
# 检查TSLA策略
python -m src.pipeline.run_daily_check_email

# 检查所有三只股票
.\daily_real_check.bat
```

#### 4. 设置自动化任务
```powershell
# 配置每日自动执行
.\setup_daily_task.bat
```

### 方式B: 使用多维度数据源系统(高级)

#### 1. 配置所有API密钥
```powershell
# 设置环境变量
$env:NEWS_API_KEY="your_newsapi_key"
$env:FINNHUB_API_KEY="your_finnhub_key"
$env:FMP_API_KEY="your_fmp_key"
$env:ALPHAVANTAGE_API_KEY="your_alphavantage_key"
$env:TRADIER_API_KEY="your_tradier_key"
$env:FRED_API_KEY="your_fred_key"
```

#### 2. 生成综合分析报告
```python
from src.data.unified_provider import UnifiedDataProvider

# 初始化统一数据源
provider = UnifiedDataProvider()

# 获取TSLA全方位分析
analysis = provider.get_comprehensive_analysis('TSLA')

# 查看综合评分
print(f"评分: {analysis['综合评分']['score']}/100")
print(f"建议: {analysis['综合评分']['recommendation']}")

# 生成详细报告
provider.generate_report('TSLA', 'reports/TSLA_analysis.md')
```

#### 3. 运行演示脚本
```powershell
# 查看所有数据源功能
python examples/multi_data_sources_demo.py
```

---

## 📊 回测系统

### 1. 运行回测
```powershell
python -m src.pipeline.run_backtest
```

回测会生成:
- 📊 性能指标报告 (`backtest_results/metrics.txt`)
- 📈 资产净值曲线 (`backtest_results/equity_curve.csv`)
- 📋 交易记录 (`backtest_results/trades.csv`)
- 🎨 可视化图表 (`backtest_results/charts/`)

### 2. 查看结果
打开 `backtest_results/metrics.txt` 查看:
- 总收益率
- 夏普比率
- 最大回撤
- 胜率
- 盈亏比

---

**生成可视化图表**:
```powershell
python -m src.backtest.visualizer
```

**查看详细分析**:
参考 [回测报告](docs/backtest_report.md) 了解策略表现、风险指标和优化建议。

### 4. 实盘模拟
运行示例策略（使用mock broker）：
```powershell
python -m src.pipeline.run_once
```

### 5. 运行测试
```powershell
python -m unittest
```

---

## 📊 回测结果概览

### 核心指标
- **总收益率**: 335.16% (15.4年)
- **年化收益率**: 10.05%
- **夏普比率**: 0.46
- **最大回撤**: -90.61% ⚠️
- **胜率**: 100% (5/5 交易)

### 关键发现
✅ **优势**:
- 长期盈利能力强
- 交易纪律严格(仅6笔交易)
- 无亏损交易

⚠️ **风险**:
- 最大回撤过大,需要添加止损
- 夏普比率偏低
- 信号不平衡(只有卖出信号)

详细分析请查看 [完整回测报告](docs/backtest_report.md)

---

## 🛣️ 路线图

### ✅ 已完成
- ✅ 项目架构设计与文档
- ✅ CSV数据加载器
- ✅ 动量信号模型
- ✅ 仓位分配器
- ✅ Mock订单执行
- ✅ Alpha Vantage 免费数据源
- ✅ **回测框架** (引擎 + 可视化)
- ✅ **完整性能评估** (夏普比率、回撤、胜率)
- ✅ 单元测试覆盖

### 🚧 进行中
- 策略优化(参数调整、止损机制)
- 风险控制增强

### 📅 计划中
- 实盘券商API对接 (IBKR/Alpaca)
- 多策略框架
- 实时监控与告警
- 多股票支持
- 机器学习模型

## 📚 文档导航

### 核心文档
- [**多维度数据源完整指南**](docs/MULTI_DIMENSIONAL_DATA_SOURCES_GUIDE.md) - 7类数据源的详细使用文档 ⭐
- [**多数据源完成报告**](MULTI_DATA_SOURCES_COMPLETION.md) - 新增功能的完整说明
- [**回测报告**](docs/backtest_report.md) - 策略性能分析报告
- [**架构设计**](docs/architecture.md) - 系统架构说明
- [**路线图**](docs/roadmap.md) - 项目发展规划

### 配置指南
- [**Alpha Vantage配置**](docs/alphavantage_setup.md) - 免费数据源配置
- [**多数据源配置**](docs/multi_data_sources.md) - 备用数据源说明
- [**API密钥模板**](.env.template) - 所有API密钥配置示例

### 使用指南
- [**快速开始指南**](QUICK_START_GUIDE.md) - 新手入门
- [**日度策略使用**](DAILY_STRATEGY_USAGE_GUIDE.md) - 实时策略说明
- [**多股票系统**](MULTI_STOCK_SYSTEM_GUIDE.md) - 三股票策略使用
- [**邮件系统**](EMAIL_PUSH_SETUP_COMPLETE.md) - 邮件通知配置
- [**任务调度**](SETUP_DAILY_TASK_GUIDE.md) - Windows自动化设置

### 示例代码
- [**多数据源演示**](examples/multi_data_sources_demo.py) - 所有数据源使用示例 ⭐

---

## 🎯 主要成果

### 数据源系统 (v2.0)
- ✅ **7类数据源**: 价格、新闻、基本面、期权、宏观、社交、内部人
- ✅ **统一接口**: UnifiedDataProvider整合所有数据
- ✅ **智能评分**: 综合投资评分系统(0-100分)
- ✅ **自动报告**: 生成Markdown格式综合分析报告

### 交易策略系统 (v1.0)
- ✅ **三股票策略**: TSLA、NVDA、INTC同时监控
- ✅ **日度策略**: 每日自动执行,邮件通知
- ✅ **回测系统**: 完整的性能评估和可视化
- ✅ **自动化**: Windows任务调度(周一至周五08:00)

### 核心指标
**TSLA策略回测**(2010-2024):
- 总收益: 335.16%
- 年化收益: 10.05%
- 交易次数: 6笔
- 胜率: 100%

---

## 🛣️ 发展路线图

### ✅ 已完成(v2.0)
- ✅ 多维度数据源系统(7类)
- ✅ 综合投资评分算法
- ✅ 统一数据源管理器
- ✅ 完整使用文档和示例

### ✅ 已完成(v1.0)
- ✅ 三股票策略系统
- ✅ 动量策略实现
- ✅ 回测框架
- ✅ 邮件通知系统
- ✅ Windows自动化调度

### 🚧 进行中(v2.1)
- 🔄 数据缓存机制(Redis/SQLite)
- 🔄 策略集成多数据源
- 🔄 深度学习情绪分析(BERT)
- 🔄 实时数据流(Websocket)

### 📅 计划中(v3.0)
- 📋 Web Dashboard可视化
- 📋 实盘券商API对接(IBKR/Alpaca)
- 📋 多策略组合管理
- 📋 机器学习预测模型
- 📋 风险管理系统

---

## ⚠️ 免责声明

**本项目仅供学习和研究使用,不构成任何投资建议。**

- 股票投资有风险,入市需谨慎
- 历史业绩不代表未来表现
- 使用本系统产生的任何投资损失,开发者不承担责任
- 请在充分了解风险的前提下做出投资决策

---

## 📞 联系方式

- **邮箱**: qsswgl@gmail.com
- **GitHub**: https://github.com/qsswgl/QT
- **问题反馈**: [GitHub Issues](https://github.com/qsswgl/QT/issues)

---

## 📄 许可证

MIT License

---

*最后更新: 2025-11-19*  
*版本: v2.0.0*  
*维护者: GitHub Copilot*
