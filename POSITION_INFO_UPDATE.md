# 📊 持仓信息显示功能更新

## 🎯 更新目标

在实时策略邮件中，即使没有新的交易信号，也要显示当前持有股票的详细信息。

---

## ✅ 完成的更新

### 1. 邮件服务增强 (`src/notification/email_service.py`)

#### 修改 `send_daily_summary` 方法
- 新增参数：`position_info: Optional[dict]`
- 持仓信息结构：
  ```python
  {
      'symbol': str,           # 股票代码
      'quantity': int,         # 持仓数量
      'avg_price': float,      # 平均成本
      'current_price': float,  # 当前价格
      'market_value': float,   # 市值
      'profit_loss': float,    # 浮动盈亏（金额）
      'profit_loss_pct': float # 浮动盈亏（百分比）
  }
  ```

#### 修改 `_build_summary_email_body` 方法
- 新增持仓信息HTML展示
- **有持仓时**显示：
  - 📊 股票代码
  - 📈 持仓数量
  - 💵 平均成本
  - 💹 当前价格
  - 💰 总市值
  - 📊 浮动盈亏（金额和百分比，颜色区分盈亏）
- **空仓时**显示：
  - ⚪ 空仓状态
  - 提示：等待买入信号

### 2. 实时检查脚本更新

#### TSLA (`src/pipeline/run_daily_check_email.py`)
- ✅ 新增 `get_current_position()` 函数
- ✅ 从 `trades_daily.csv` 读取交易记录
- ✅ 计算当前持仓数量和成本
- ✅ 在邮件中包含持仓信息

#### NVDA (`src/pipeline/run_daily_check_email_nvda.py`)
- ✅ 新增 `get_current_position()` 函数
- ✅ 从 `NVDA/backtest_results/daily/trades_daily.csv` 读取
- ✅ 在邮件中包含持仓信息

#### INTC (`src/pipeline/run_daily_check_email_intc.py`)
- ✅ 新增 `get_current_position()` 函数
- ✅ 从 `INTC/backtest_results/daily/trades_daily.csv` 读取
- ✅ 在邮件中包含持仓信息

---

## 📧 邮件展示效果

### 空仓状态（当前情况）
```
✅ 日度策略检查完成
TSLA 策略运行正常

📊 检查结果
暂无新交易信号
策略运行正常,继续持有当前仓位即可

📊 当前持仓
⚪ 空仓
等待买入信号

💡 提示: 无需任何操作,系统将继续自动检查
📅 检查时间: 2025-11-18 08:55:32
```

### 有持仓状态（示例）
```
✅ 日度策略检查完成
TSLA 策略运行正常

📊 检查结果
暂无新交易信号
策略运行正常,继续持有当前仓位即可

📊 当前持仓
┌─────────────┬──────────────┐
│ 股票代码    │ TSLA         │
│ 持仓数量    │ 148 股       │
│ 平均成本    │ $448.98      │
│ 当前价格    │ $401.99      │
│ 市值        │ $59,494.52   │
│ 浮动盈亏    │ -$10,493.04 (-15.00%) │
└─────────────┴──────────────┘

💡 提示: 无需任何操作,系统将继续自动检查
📅 检查时间: 2025-11-18 08:55:32
```

---

## 🔧 持仓计算逻辑

### 算法说明
1. **读取交易记录**：从 `trades_daily.csv` 读取所有历史交易
2. **累计持仓**：
   - BUY：增加持仓数量和总成本
   - SELL：按比例减少持仓数量和总成本
3. **计算指标**：
   - 平均成本 = 总成本 / 持仓数量
   - 市值 = 持仓数量 × 当前价格
   - 浮动盈亏 = 市值 - 总成本
   - 盈亏百分比 = (浮动盈亏 / 总成本) × 100%

### 代码示例
```python
quantity = 0
total_cost = 0

for trade in trades:
    if trade['action'] == 'BUY':
        quantity += trade['quantity']
        total_cost += trade['total']
    elif trade['action'] == 'SELL':
        if quantity > 0:
            sell_ratio = trade['quantity'] / quantity
            total_cost *= (1 - sell_ratio)
            quantity -= trade['quantity']
```

---

## 🎨 邮件样式特性

### 持仓表格样式
- ✅ 清晰的表格布局
- ✅ 交替行背景色（便于阅读）
- ✅ 盈亏动态颜色：
  - 🟢 绿色：盈利
  - 🔴 红色：亏损
- ✅ 响应式设计（适配移动端）

### 空仓样式
- ✅ 居中显示
- ✅ 大字体提示
- ✅ 灰色色调（中性状态）

---

## 🚀 使用方法

### 每日运行（推荐）
```bash
# 一键运行所有股票实时检查
daily_real_check.bat

# 或单独运行
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email.py       # TSLA
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email_nvda.py  # NVDA
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email_intc.py  # INTC
```

### 邮件接收
- 📧 收件箱：qsswgl@gmail.com
- 📊 包含内容：
  - ✅ 每日检查结果
  - ✅ 新信号提醒（如有）
  - ✅ 当前持仓详情
  - ✅ 操作建议

---

## 📊 测试结果

### 2025-11-18 测试
| 股票 | 持仓数量 | 平均成本 | 当前状态 | 邮件发送 |
|------|---------|---------|---------|---------|
| TSLA | 0 股 | $0.00 | ⚪ 空仓 | ✅ 成功 |
| NVDA | 0 股 | $0.00 | ⚪ 空仓 | ✅ 成功 |
| INTC | 0 股 | $0.00 | ⚪ 空仓 | ✅ 成功 |

**测试结论**：
- ✅ 所有脚本正常运行
- ✅ 持仓信息正确显示
- ✅ 邮件成功发送
- ✅ 空仓状态正确展示

---

## 💡 优势说明

### 1. 信息完整性
- ✅ 即使无新信号，也能了解持仓状态
- ✅ 实时掌握盈亏情况
- ✅ 无需登录券商平台查询

### 2. 决策支持
- ✅ 清晰的成本价格对比
- ✅ 直观的盈亏展示
- ✅ 帮助判断是否需要调整仓位

### 3. 风险管理
- ✅ 每日提醒当前风险敞口
- ✅ 浮动盈亏百分比警示
- ✅ 及时发现异常情况

---

## 📝 注意事项

### 持仓计算准确性
- ⚠️ 基于回测交易记录计算
- ⚠️ **实盘交易需手动同步**
- ⚠️ 不包括分红、拆股等企业行为

### 实盘vs回测
- 📈 邮件显示的是**回测系统**中的持仓
- 📈 实际持仓请以 Firstrade 账户为准
- 📈 建议定期对账确保一致性

### 数据更新
- 📊 当前价格基于最新收盘价
- 📊 盘中价格变动不会实时更新
- 📊 每日策略运行后更新一次

---

## 🔄 后续优化建议

### 1. 实盘同步（优先级：高）
- 从 Firstrade API 获取实际持仓
- 对比回测与实盘差异
- 自动同步交易记录

### 2. 多账户支持（优先级：中）
- 支持多个券商账户
- 统计总体持仓
- 分账户展示

### 3. 历史趋势（优先级：低）
- 持仓成本趋势图
- 盈亏曲线
- 周/月持仓报告

---

## 📞 相关文档

- `DAILY_STRATEGY_USAGE_GUIDE.md` - 日度策略使用指南
- `EMAIL_DISPLAY_GUIDE.md` - 邮件显示说明
- `QUICK_START_GUIDE.md` - 快速入门指南

---

**更新日期**: 2025-11-18  
**版本**: v1.0  
**状态**: ✅ 已完成并测试
