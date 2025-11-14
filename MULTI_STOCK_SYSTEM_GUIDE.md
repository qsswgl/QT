# 多股票量化交易系统使用指南

## 📊 系统概述

本系统支持同时运行多个股票的量化交易策略。目前已配置：
- **TSLA** (特斯拉)
- **NVDA** (英伟达)
- **INTC** (英特尔)

每个股票使用相同的日内动量交易策略，但独立运行和分析。

## 🎯 策略特点

### 核心策略
- **策略类型**: 日内动量交易
- **交易频率**: 每天最多1次
- **仓位比例**: 60%
- **动量窗口**: 5日
- **趋势过滤**: 20日移动平均
- **成交量确认**: 1.3倍平均成交量
- **止盈**: 5%
- **止损**: 2%

### 信号规则
1. **买入信号**: 5日动量 > 3% + 成交量放大 + 处于上升趋势
2. **卖出信号**: 止盈/止损触发 或 动量转负(-2%)

## 📁 目录结构

```
K:\QT\
├── TSLA/                                    # TSLA股票目录
│   ├── data/
│   │   └── sample_tsla.csv                 # TSLA历史数据
│   ├── backtest_results/daily/              # 回测结果
│   │   ├── equity_curve_daily.csv
│   │   ├── trades_daily.csv
│   │   └── signals_daily.csv
│   ├── daily_strategy_check.bat            # 自动化脚本
│   └── STRATEGY_EXECUTION_LOG.md           # 策略执行日志
│
├── NVDA/                                    # NVDA股票目录
│   ├── data/
│   │   └── sample_nvda.csv                 # NVDA历史数据
│   ├── backtest_results/daily/
│   ├── daily_strategy_check_nvda.bat
│   └── STRATEGY_EXECUTION_LOG.md
│
├── INTC/                                    # INTC股票目录
│   ├── data/
│   │   └── sample_intc.csv
│   ├── backtest_results/daily/
│   ├── daily_strategy_check_intc.bat
│   └── STRATEGY_EXECUTION_LOG.md
│
└── src/pipeline/
    ├── update_data_multi_source.py         # 数据更新脚本
    ├── run_daily_strategy_*.py             # 策略执行脚本
    ├── run_daily_check_email_*.py          # 邮件通知脚本
    └── log_strategy_execution_*.py         # 日志记录脚本
```

## 🚀 快速开始

### 1. 首次设置

#### 获取历史数据
```bash
# NVDA
python src/pipeline/update_data_multi_source.py NVDA --days 365 --output NVDA/data/sample_nvda.csv

# INTC
python src/pipeline/update_data_multi_source.py INTC --days 365 --output INTC/data/sample_intc.csv
```

### 2. 每日运行策略

#### 方法1: 使用批处理文件（推荐）
```powershell
# 在PowerShell中运行NVDA策略
cd K:\QT\NVDA
.\daily_strategy_check_nvda.bat

# 运行INTC策略
cd K:\QT\INTC
.\daily_strategy_check_intc.bat

# 或者在文件管理器中直接双击运行对应的.bat文件
```

#### 方法2: 手动执行各步骤
```powershell
# 步骤1: 更新数据
k:/QT/.venv/Scripts/python.exe src/pipeline/update_data_multi_source.py NVDA --output NVDA/data/sample_nvda.csv

# 步骤2: 运行策略
k:/QT/.venv/Scripts/python.exe src/pipeline/run_daily_strategy_nvda.py

# 步骤3: 发送邮件通知
k:/QT/.venv/Scripts/python.exe src/pipeline/run_daily_check_email_nvda.py

# 步骤4: 记录日志
k:/QT/.venv/Scripts/python.exe src/pipeline/log_strategy_execution_nvda.py
```

## 📧 邮件通知

系统会在以下情况发送邮件：
1. **有新信号**: 当策略生成买入/卖出信号时
2. **每日摘要**: 即使没有信号也会发送状态更新

### 邮件内容
- 策略执行状态
- 最新市场数据
- 交易信号详情
- 操作建议

### 配置邮箱
邮件发送到: `qsswgl@gmail.com`

如需修改，编辑各股票的 `run_daily_check_email_*.py` 文件。

## 📝 日志系统

### 日志文件位置
- NVDA: `K:\QT\NVDA\STRATEGY_EXECUTION_LOG.md`
- INTC: `K:\QT\INTC\STRATEGY_EXECUTION_LOG.md`
- TSLA: `K:\QT\STRATEGY_EXECUTION_LOG.md`

### 日志内容
每次执行自动记录：
- 执行时间和状态
- 数据更新情况
- 市场状态（价格、成交量）
- 信号情况
- 策略决策
- 回顾分析

### 手动填写项
需要在日志中手动补充：
1. 数据来源（Yahoo Finance / Alpha Vantage / Twelve Data）
2. 当前持仓情况
3. 决策依据
4. 特殊情况备注
5. 每周策略表现评价（✅ 正确 / ❌ 错误 / ⚠️ 待观察）

## 🔄 每日工作流

### 市场开盘前
1. 运行各股票的批处理文件更新数据和生成信号
2. 查收邮件通知
3. 查看策略执行日志

### 有信号时
1. 查看信号详情（类型、价格、原因）
2. 评估市场环境
3. 决定是否执行交易
4. 在日志中记录决策和理由

### 市场收盘后
1. 更新日志中的"当前持仓"
2. 记录实际执行情况
3. 添加市场观察备注

## 📊 每周回顾

### 回顾时间
建议每周日进行

### 回顾步骤
1. 打开各股票的 `STRATEGY_EXECUTION_LOG.md`
2. 回顾本周所有日志条目
3. 填写"策略表现"评价：
   - ✅ **正确**: 信号符合后续市场走势
   - ❌ **错误**: 信号与市场走势相反
   - ⚠️ **待观察**: 尚未有明确结果
4. 在日志末尾的"每周回顾总结"部分：
   - 统计本周信号数和准确率
   - 分析市场趋势
   - 总结策略表现
   - 规划下周重点

### 回顾模板
```markdown
### 第X周 (YYYY-MM-DD ~ YYYY-MM-DD)

**本周概况**:
- 策略执行次数: X次
- 产生信号数: X个 (X个BUY, X个SELL)
- 正确信号: X个
- 错误信号: X个
- 准确率: XX%

**市场分析**:
- XXX周涨跌: +X.XX%
- 市场趋势: 上涨/下跌/震荡
- 主要影响因素:
  - 
  - 

**策略表现**:
- 策略优势:
  - 
- 改进空间:
  - 

**下周计划**:
- 
```

## 🎯 添加新股票

### 步骤1: 创建目录结构
```bash
# 假设添加 AMD
mkdir AMD
mkdir AMD\data
mkdir AMD\backtest_results
mkdir AMD\backtest_results\daily
```

### 步骤2: 复制脚本文件
```bash
# 复制策略脚本
Copy-Item src\pipeline\run_daily_strategy_nvda.py src\pipeline\run_daily_strategy_amd.py

# 复制邮件脚本
Copy-Item src\pipeline\run_daily_check_email_nvda.py src\pipeline\run_daily_check_email_amd.py

# 复制日志脚本
Copy-Item src\pipeline\log_strategy_execution_nvda.py src\pipeline\log_strategy_execution_amd.py
```

### 步骤3: 修改脚本
在各脚本文件中替换：
- `NVDA` → `AMD`
- `nvda` → `amd`
- `英伟达` → `超威半导体` (可选)

关键修改点：
1. **run_daily_strategy_amd.py**: 
   - 类名: `DailyTradingStrategyAMD`
   - `self.symbol = "AMD"`
   - 数据路径: `"AMD" / "data" / "sample_amd.csv"`
   - 结果路径: `"AMD" / "backtest_results" / "daily"`

2. **run_daily_check_email_amd.py**:
   - 信号文件: `"AMD/backtest_results/daily/signals_daily.csv"`

3. **log_strategy_execution_amd.py**:
   - `SYMBOL = "AMD"`
   - `DATA_DIR = project_root / "AMD"`

### 步骤4: 创建批处理文件
在 `AMD/` 目录下创建 `daily_strategy_check_amd.bat`:

```batch
@echo off
echo ============================================================
echo AMD Daily Trading Strategy Check
echo ============================================================
echo.

cd /d K:\QT

echo Step 1/4: Updating AMD data...
k:\QT\.venv\Scripts\python.exe src\pipeline\update_data_multi_source.py AMD --output AMD\data\sample_amd.csv
if errorlevel 1 (
    echo ERROR: Data update failed
    pause
    exit /b 1
)
echo.

echo Step 2/4: Running AMD strategy...
k:\QT\.venv\Scripts\python.exe src\pipeline\run_daily_strategy_amd.py
if errorlevel 1 (
    echo ERROR: Strategy execution failed
    pause
    exit /b 1
)
echo.

echo Step 3/4: Sending email notification...
k:\QT\.venv\Scripts\python.exe src\pipeline\run_daily_check_email_amd.py
if errorlevel 1 (
    echo WARNING: Email notification failed
)
echo.

echo Step 4/4: Logging execution...
k:\QT\.venv\Scripts\python.exe src\pipeline\log_strategy_execution_amd.py
if errorlevel 1 (
    echo WARNING: Logging failed
)
echo.

echo ============================================================
echo AMD Strategy Check Complete!
echo ============================================================
pause
```

### 步骤5: 创建日志模板
复制 `NVDA/STRATEGY_EXECUTION_LOG.md` 到 `AMD/STRATEGY_EXECUTION_LOG.md`，并修改标题。

### 步骤6: 获取历史数据
```powershell
k:/QT/.venv/Scripts/python.exe src/pipeline/update_data_multi_source.py AMD --days 365 --output AMD/data/sample_amd.csv
```

### 步骤7: 测试运行
```powershell
cd AMD
.\daily_strategy_check_amd.bat
```

## 🔧 策略参数调整

如需为不同股票使用不同参数，修改对应的 `run_daily_strategy_*.py` 中的策略配置：

```python
strategy = DailyTradingStrategyXXX(
    initial_cash=100000.0,      # 初始资金
    position_pct=0.6,           # 仓位比例 (60%)
    momentum_window=5,          # 动量窗口 (5日)
    trend_window=20,            # 趋势窗口 (20日)
    volume_threshold=1.3,       # 成交量阈值 (1.3x)
    profit_target=0.05,         # 止盈 (5%)
    stop_loss=0.02              # 止损 (2%)
)
```

### 参数说明
- **initial_cash**: 回测初始资金
- **position_pct**: 每次交易使用的资金比例
- **momentum_window**: 计算动量的天数
- **trend_window**: 判断趋势的天数
- **volume_threshold**: 成交量放大倍数
- **profit_target**: 止盈百分比
- **stop_loss**: 止损百分比

## 📈 性能监控

### 关键指标
- **总收益率**: 整个回测期间的总回报
- **年化收益率**: 年化后的回报率
- **夏普比率**: 风险调整后收益（>1为好）
- **最大回撤**: 最大的资产回撤幅度
- **胜率**: 盈利交易占比
- **盈亏比**: 平均盈利/平均亏损

### 查看方式
1. **实时**: 运行策略时在终端显示
2. **文件**: 查看 `*/backtest_results/daily/summary_daily.txt`
3. **CSV**: 分析 `equity_curve_daily.csv` 和 `trades_daily.csv`

## ⚠️ 注意事项

### 数据相关
1. 数据来源可能被限流，建议：
   - 不要频繁更新（每天1次即可）
   - 系统会自动切换数据源
   - Yahoo Finance失败后会用Alpha Vantage

2. 数据质量：
   - 定期检查数据完整性
   - 注意停牌日、节假日数据缺失
   - 在日志中记录数据异常

### 策略相关
1. 回测结果≠实盘结果
2. 考虑滑点和交易成本
3. 市场环境变化会影响策略表现
4. 定期评估和调整参数

### 风险控制
1. 不要投入超过承受能力的资金
2. 严格执行止损
3. 分散投资多个股票
4. 定期回顾策略表现

## 📞 故障排查

### 数据更新失败
- 检查网络连接
- 等待后重试（可能是API限流）
- 查看是否需要更新API key

### 策略执行失败
- 确认数据文件存在
- 检查数据格式是否正确
- 查看错误日志详情

### 邮件发送失败
- 检查邮箱配置
- 确认Gmail应用专用密码
- 查看SMTP设置

### 日志记录异常
- 确认日志文件权限
- 检查文件编码
- 查看磁盘空间

## 🔗 相关文档

- `README.md` - 项目总览
- `QUICK_START_GUIDE.md` - 快速入门
- `docs/multi_data_sources.md` - 多数据源使用
- `GMAIL_SETUP_GUIDE.md` - 邮件配置
- `STRATEGY_LOG_GUIDE.md` - 日志系统详解

## 📝 版本历史

### v1.0 (2025-11-14)
- ✅ 支持TSLA、NVDA、INTC三只股票
- ✅ 统一的日内动量交易策略
- ✅ 自动化数据更新、策略执行、邮件通知、日志记录
- ✅ 完整的每周回顾系统

## 🎯 下一步计划

1. 添加更多股票（如AMD、MSFT、AAPL等）
2. 开发策略比较工具
3. 实现自动化定时任务
4. 开发Web监控界面
5. 增加实盘交易接口

---

最后更新: 2025-11-14
维护者: QT量化交易系统
