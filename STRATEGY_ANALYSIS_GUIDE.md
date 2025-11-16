# 📊 策略执行记录和分析系统使用指南

## 📋 系统概述

本系统提供完整的策略执行记录、分析和评分功能,包括:

1. **自动记录**: 每次策略执行自动记录结果
2. **周度分析**: 汇总一周的策略表现
3. **月度分析**: 汇总一个月的策略表现
4. **策略评分**: 为每个策略打分并排名
5. **对比分析**: 对比三个股票的策略表现
6. **邮件通知**: 自动发送执行汇总邮件

---

## 🚀 快速开始

### 1. 每日策略执行 (推荐)

使用智能每日检查,一键运行所有策略并记录结果:

```bash
.\smart_daily_check.bat
```

**功能**:
- 自动运行 TSLA、NVDA、INTC 三个股票的每日策略
- 自动记录每次执行的结果到 `strategy_execution_records.json`
- 自动发送邮件汇总到你的邮箱

**执行记录包含**:
- 执行时间
- 总信号数和新信号数
- 最新信号的日期、动作和价格
- 是否成功执行
- 错误信息 (如果有)

---

### 2. 生成周度报告

```bash
.\generate_weekly_reports.bat
```

**输出文件**:
- `weekly_report_YYYY-MM-DD_to_YYYY-MM-DD.md` (每个股票一份)

**报告内容**:
- 本周信号统计 (BUY/SELL)
- 本周交易统计 (次数、胜率、盈亏)
- 日度策略和周度策略对比
- 策略评估和建议

---

### 3. 生成月度报告

月度报告会在周度报告生成时一起生成。

**输出文件**:
- `monthly_report_YYYY_MM.md` (每个股票一份)

**报告内容**:
- 本月信号统计
- 本月交易统计
- 盈亏详情 (总盈亏、平均、最大最小)
- 月度策略考核 (交易频率、胜率、盈亏表现)
- 详细改进建议

---

### 4. 生成策略对比和评分报告

```bash
.\generate_all_reports.bat
```

这会生成所有报告,包括:
- 周度报告 (3个)
- 月度报告 (3个)
- 策略对比报告
- 策略评分数据

**策略对比报告包含**:
- 6个策略的总分排名 (3个股票 × 2个周期)
- 详细评分 (胜率分、盈利分、稳定分、频率分、风险收益分)
- 最佳和最差策略分析
- 按股票的优化建议
- 行动计划

**评分标准**:
| 评分项 | 权重 | 说明 |
|--------|------|------|
| 胜率 | 30% | 盈利交易占比 |
| 盈利 | 25% | 总盈亏金额 |
| 稳定性 | 20% | 盈利交易一致性 |
| 交易频率 | 15% | 交易次数是否合理 |
| 风险收益比 | 10% | 平均每笔盈亏 |

**等级划分**:
- 90+ 分: A+ 优秀
- 80-89 分: A 良好
- 70-79 分: B+ 中上
- 60-69 分: B 中等
- 50-59 分: C 及格
- <50 分: D 不及格

---

## 📂 文件结构

```
k:\QT\
├── strategy_execution_records.json     # 执行记录 (自动生成)
├── weekly_report_*.md                  # 周度报告
├── monthly_report_*.md                 # 月度报告
├── strategy_comparison_*.md            # 策略对比报告
├── strategy_scores_*.csv               # 评分数据 (CSV格式)
│
├── NVDA\
│   └── strategy_execution_records.json
│
└── INTC\
    └── strategy_execution_records.json
```

---

## 🔧 高级用法

### 手动记录执行结果

如果你单独运行某个策略,可以手动记录结果:

```python
from src.analysis.strategy_analyzer import StrategyAnalyzer

analyzer = StrategyAnalyzer("TSLA")
analyzer.record_execution(
    strategy_type="daily",
    signals_count=250,
    new_signals_count=1,
    latest_signal_date="2025-11-15",
    latest_signal_action="BUY",
    latest_signal_price=430.50,
    notes="手动执行"
)
```

### 查看特定周的报告

```python
from src.analysis.strategy_analyzer import StrategyAnalyzer

analyzer = StrategyAnalyzer("TSLA")

# 生成指定周的报告
report = analyzer.generate_weekly_report(start_date="2025-11-11")
print(report)
```

### 查看特定月的报告

```python
from src.analysis.strategy_analyzer import StrategyAnalyzer

analyzer = StrategyAnalyzer("TSLA")

# 生成指定月的报告
report = analyzer.generate_monthly_report(year=2025, month=11)
print(report)
```

### 自定义评分权重

编辑 `src/analysis/strategy_scorer.py`:

```python
class StrategyScorer:
    WEIGHTS = {
        "win_rate": 0.40,        # 提高胜率权重
        "profit": 0.30,          # 提高盈利权重
        "consistency": 0.15,     # 降低稳定性权重
        "frequency": 0.10,       # 降低频率权重
        "risk_reward": 0.05      # 降低风险收益权重
    }
```

---

## 📊 查看历史记录

### 查看执行记录

```python
import json

# 读取 TSLA 的执行记录
with open('strategy_execution_records.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查看最近5次执行
for execution in data['executions'][-5:]:
    print(f"{execution['timestamp']}: {execution['strategy_type']}")
    print(f"  信号数: {execution['signals_count']}")
    print(f"  新信号: {execution['new_signals_count']}")
    print()
```

### 导出到Excel

评分数据已经保存为CSV格式,可以直接在Excel中打开:
- `strategy_scores_month_YYYYMMDD.csv`

---

## 🎯 最佳实践

### 1. 每日工作流

```
早上:
1. 运行 .\smart_daily_check.bat
2. 查看邮件汇总
3. 如有新信号,评估是否交易

晚上:
4. 查看 Firstrade 账户执行情况
5. 更新 TRADE_EXECUTION_LOG.md
```

### 2. 每周工作流

```
周末:
1. 运行 .\generate_weekly_reports.bat
2. 查看三个股票的周度报告
3. 评估本周策略表现
4. 记录需要调整的参数
```

### 3. 每月工作流

```
月末:
1. 运行 .\generate_all_reports.bat
2. 查看月度报告和策略对比
3. 根据评分确定下月重点策略
4. 调整策略参数或仓位配置
5. 更新交易计划
```

---

## 🔍 故障排查

### 问题1: 执行记录文件不存在

**解决方法**: 首次运行时会自动创建,无需担心。

### 问题2: 没有交易数据

**原因**: 可能是策略还没有生成足够的信号或执行交易。

**解决方法**: 
1. 检查 `backtest_results/daily/signals_daily.csv` 是否有数据
2. 确认策略是否正常运行
3. 查看策略执行日志

### 问题3: 报告显示数据为0

**原因**: 选定的时间范围内没有交易。

**解决方法**:
1. 确认策略是否在该时间段运行过
2. 检查信号文件的日期范围
3. 尝试生成更长时间段的报告

### 问题4: 评分异常

**原因**: 数据不完整或计算公式需要调整。

**解决方法**:
1. 检查交易数据的完整性
2. 查看是否有异常的盈亏数据
3. 根据实际情况调整评分权重

---

## 📧 邮件通知配置

邮件系统已配置为使用 QQ 邮箱发送,接收方为 Gmail。

**发件人**: 13794881@qq.com
**收件人**: qsswgl@gmail.com

如需修改,请编辑 `src/notification/email_config.py`。

---

## 💡 改进建议

### 自动化建议

1. **定时任务**: 设置 Windows 任务计划程序,每天自动运行 `smart_daily_check.bat`
2. **周报定时**: 每周日自动生成周度报告
3. **月报定时**: 每月最后一天自动生成月度报告

### 可视化建议

1. 添加图表展示策略表现趋势
2. 创建仪表板显示实时策略评分
3. 生成交易热力图

### 功能扩展建议

1. 添加策略回测功能
2. 支持参数优化建议
3. 增加风险预警系统
4. 支持多个邮箱接收

---

## 📚 相关文档

- [快速开始指南](QUICK_START_GUIDE.md)
- [策略执行日志指南](STRATEGY_LOG_GUIDE.md)
- [邮件系统配置](QQ_EMAIL_SUCCESS.md)
- [多股票系统指南](MULTI_STOCK_SYSTEM_GUIDE.md)

---

## 🆘 获取帮助

如遇到问题:
1. 查看相关批处理文件的输出日志
2. 检查 `strategy_execution_records.json` 的错误信息
3. 查看策略执行日志文件
4. 参考上述故障排查部分

---

**最后更新**: 2025-11-15
**版本**: 1.0
