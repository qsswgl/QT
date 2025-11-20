# 📊 日度策略使用指南

## 🔑 关键区别

### ⚠️ 两种不同的脚本

| 类型 | 脚本名称 | 用途 | 运行频率 |
|------|---------|------|---------|
| **历史回测** | `run_daily_strategy*.py` | 评估策略历史表现 | 偶尔（策略调整时） |
| **实时检查** | `run_daily_check_email*.py` | 获取今日交易建议 | **每天运行** |

---

## 📈 历史回测脚本

### 脚本列表
```bash
src\pipeline\run_daily_strategy.py         # TSLA 历史回测
src\pipeline\run_daily_strategy_nvda.py    # NVDA 历史回测
src\pipeline\run_daily_strategy_intc.py    # INTC 历史回测
```

### 功能说明
- ✅ 分析整个历史期间（例如：2010-2025）
- ✅ 生成完整回测报告（342个历史信号）
- ✅ 评估策略表现（总收益、夏普比率、最大回撤）
- ❌ **不提供**当日交易建议

### 运行方式
```bash
# 快捷方式（批处理文件）
daily_strategy_check.bat

# 或单独运行
.\.venv\Scripts\python.exe src\pipeline\run_daily_strategy.py
```

### 输出示例
```
总收益率: 8.84%
年化收益率: 0.55%
总交易次数: 171
胜率: 43.86%
```

### 使用场景
- 🔧 调整策略参数后验证效果
- 📊 评估策略历史表现
- 📈 生成报告给他人展示

---

## 📧 实时策略检查脚本（⭐ 每天使用）

### 脚本列表
```bash
src\pipeline\run_daily_check_email.py       # TSLA 实时检查
src\pipeline\run_daily_check_email_nvda.py  # NVDA 实时检查
src\pipeline\run_daily_check_email_intc.py  # INTC 实时检查
```

### 功能说明
- ✅ 检查**今天**是否有新交易信号
- ✅ 发送当日操作建议邮件
- ✅ 告诉你今天要不要买入/卖出
- ✅ **这才是每日交易指导**

### 运行方式（推荐）
```bash
# 🌟 推荐：一键运行所有实时检查
daily_real_check.bat

# 或单独运行
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email.py
```

### 输出示例

#### 情况1：有新信号
```
✅ 发现 1 个新信号!

最新信号:
  日期: 2025-11-18
  动作: BUY
  数量: 135
  价格: $401.99
  原因: 动量突破

📧 发送邮件提醒...
✅ 邮件发送成功!
```

#### 情况2：无新信号（今天的情况）
```
✓ 暂无新交易信号

📧 发送每日总结...
✅ 邮件发送成功!
```

### 邮件内容
- **有信号时**：交易提醒（股票、动作、数量、价格）
- **无信号时**：每日总结（当前状态、持仓建议）

---

## 🚀 推荐使用流程

### 每日操作（工作日早晨）

1. **运行实时检查**
   ```bash
   daily_real_check.bat
   ```

2. **查收邮件**
   - 邮箱：qsswgl@gmail.com
   - 检查是否有新的交易信号

3. **执行交易**（如果有信号）
   - 登录 Firstrade
   - 根据邮件建议执行买入/卖出

4. **记录交易**（如果执行了）
   - 更新 `TRADE_EXECUTION_LOG.md`

### 策略调整时操作（偶尔）

1. **修改策略参数**
   - 编辑 `src/pipeline/run_daily_strategy.py`
   - 调整止盈止损、动量窗口等

2. **运行历史回测**
   ```bash
   daily_strategy_check.bat
   ```

3. **评估新参数效果**
   - 查看总收益率、夏普比率
   - 对比调整前后的表现

4. **如果满意，应用到实时检查**
   - 同步参数到 `run_daily_check_email.py`

---

## 📋 快速参考

### 批处理文件对照表

| 批处理文件 | 脚本类型 | 用途 | 运行频率 |
|----------|---------|------|---------|
| `daily_real_check.bat` | ⭐ 实时检查 | 今日交易建议 | **每天** |
| `daily_strategy_check.bat` | 历史回测 | 策略评估 | 偶尔 |
| `send_all_emails.bat` | 补发邮件 | 手动补发 | 按需 |
| `weekly_check.bat` | 周度分析 | 周报 | 每周 |

### 常见问题

**Q1: 为什么邮件里只有历史回测，没有今日建议？**
- ❌ 运行了 `daily_strategy_check.bat`（历史回测）
- ✅ 应该运行 `daily_real_check.bat`（实时检查）

**Q2: 如何知道今天要不要交易？**
- 运行 `daily_real_check.bat`
- 查看邮件或终端输出

**Q3: 今天没有信号，是不是系统有问题？**
- ✅ 系统正常！无信号说明市场条件不满足策略要求
- 保持观望，等待更好的交易机会

**Q4: 什么时候需要运行历史回测？**
- 调整策略参数后
- 想要评估策略表现时
- 生成报告给他人看时

---

## 💡 最佳实践

### ✅ 推荐做法
1. **每天早晨**运行 `daily_real_check.bat`
2. **根据邮件**决定是否交易
3. **每周日**运行周度分析
4. **策略调整后**运行历史回测验证

### ❌ 避免错误
1. 不要把历史回测当成交易建议
2. 不要忽略邮件中的"无信号"提醒
3. 不要在没有信号时强行交易
4. 不要频繁调整策略参数

---

## 📞 联系方式

如有问题，请查看：
- `QUICK_START_GUIDE.md` - 快速入门
- `STRATEGY_EXECUTION_LOG.md` - 执行日志
- `TRADE_EXECUTION_LOG.md` - 交易记录

---

**最后更新**: 2025-11-18
