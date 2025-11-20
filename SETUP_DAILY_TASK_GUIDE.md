# 📅 Windows 任务计划设置指南

## 🎯 目标

将每日实时策略检查设置为 Windows 自动任务，无需手动运行。

---

## ⚙️ 任务配置

### 基本信息
- **任务名称**: `QT_DailyStrategyCheck`
- **执行脚本**: `K:\QT\daily_real_check.bat`
- **执行时间**: 每个工作日（周一至周五）早上 **08:00**
- **执行内容**: 
  - 检查 TSLA 日度策略
  - 检查 NVDA 日度策略
  - 检查 INTC 日度策略
  - 发送邮件到 qsswgl@gmail.com

### 时间设置说明
- **北京时间 08:00** = **美东时间 19:00**（前一日）
- 美股交易时间：美东 09:30 - 16:00
- 在美股盘前查看策略信号，方便决策

---

## 🚀 快速设置（推荐）

### 方法一：使用 PowerShell 脚本（推荐）

1. **以管理员身份运行 PowerShell**
   - 右键点击"开始"菜单
   - 选择"Windows PowerShell (管理员)"

2. **执行设置脚本**
   ```powershell
   cd K:\QT
   .\setup_daily_task.ps1
   ```

3. **按提示完成设置**
   - 脚本会自动创建任务计划
   - 询问是否立即测试运行
   - 显示下次运行时间

### 方法二：使用批处理脚本

1. **以管理员身份运行**
   - 右键点击 `setup_daily_task.bat`
   - 选择"以管理员身份运行"

2. **按任意键完成设置**

---

## 📋 手动设置步骤

如果脚本方式不工作，可以手动设置：

### 1. 打开任务计划程序
- 按 `Win + R`
- 输入 `taskschd.msc`
- 按回车

### 2. 创建基本任务
1. 点击右侧"创建基本任务"
2. 输入名称：`QT_DailyStrategyCheck`
3. 描述：`量化交易策略每日检查`
4. 点击"下一步"

### 3. 设置触发器
1. 选择"每周"
2. 点击"下一步"
3. 选择时间：`08:00:00`
4. 勾选：周一、周二、周三、周四、周五
5. 点击"下一步"

### 4. 设置操作
1. 选择"启动程序"
2. 点击"下一步"
3. 程序或脚本：`K:\QT\daily_real_check.bat`
4. 起始于：`K:\QT`
5. 点击"下一步"

### 5. 完成设置
1. 勾选"当单击完成时，打开此任务属性对话框"
2. 点击"完成"

### 6. 高级设置（在属性对话框中）
1. **常规**选项卡：
   - 勾选"使用最高权限运行"
   
2. **条件**选项卡：
   - 勾选"只有在以下网络连接可用时才启动: 任何连接"
   - 取消"只有在计算机使用交流电源时才启动任务"
   
3. **设置**选项卡：
   - 勾选"允许按需运行任务"
   - 勾选"如果过了计划开始时间，立即启动任务"
   - 停止任务如果运行超过：2小时

4. 点击"确定"保存

---

## 🧪 测试运行

### 立即运行任务
```powershell
# PowerShell
Start-ScheduledTask -TaskName "QT_DailyStrategyCheck"

# 或使用 CMD
schtasks /Run /TN "QT_DailyStrategyCheck"
```

### 查看运行结果
1. 任务计划程序中查看"上次运行结果"
2. 查看邮箱 qsswgl@gmail.com
3. 检查日志输出

---

## 🔍 管理任务

### 查看任务详情
```powershell
# PowerShell
Get-ScheduledTask -TaskName "QT_DailyStrategyCheck" | Get-ScheduledTaskInfo

# CMD
schtasks /Query /TN "QT_DailyStrategyCheck" /V /FO LIST
```

### 查看下次运行时间
```powershell
# PowerShell
$task = Get-ScheduledTask -TaskName "QT_DailyStrategyCheck"
$info = $task | Get-ScheduledTaskInfo
Write-Host "下次运行: $($info.NextRunTime)"
```

### 禁用任务
```powershell
# PowerShell
Disable-ScheduledTask -TaskName "QT_DailyStrategyCheck"

# CMD
schtasks /Change /TN "QT_DailyStrategyCheck" /DISABLE
```

### 启用任务
```powershell
# PowerShell
Enable-ScheduledTask -TaskName "QT_DailyStrategyCheck"

# CMD
schtasks /Change /TN "QT_DailyStrategyCheck" /ENABLE
```

### 删除任务
```powershell
# PowerShell
Unregister-ScheduledTask -TaskName "QT_DailyStrategyCheck" -Confirm:$false

# CMD
schtasks /Delete /TN "QT_DailyStrategyCheck" /F
```

### 修改执行时间
```powershell
# 修改为每天早上 7:00
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "07:00"
Set-ScheduledTask -TaskName "QT_DailyStrategyCheck" -Trigger $trigger
```

---

## 📊 运行日志

### 查看任务历史
1. 打开任务计划程序
2. 找到任务 `QT_DailyStrategyCheck`
3. 点击"历史记录"选项卡
4. 查看每次运行的详细日志

### 日志位置
- Windows 事件查看器：`事件查看器 > Windows 日志 > 应用程序`
- 筛选来源：`Task Scheduler`

---

## ⚠️ 故障排查

### 任务未运行
**可能原因**：
1. ❌ 计算机未开机
2. ❌ 任务被禁用
3. ❌ 用户未登录（需设置"不管用户是否登录都要运行"）

**解决方案**：
```powershell
# 检查任务状态
Get-ScheduledTask -TaskName "QT_DailyStrategyCheck" | Select-Object State

# 确保任务已启用
Enable-ScheduledTask -TaskName "QT_DailyStrategyCheck"
```

### 任务运行失败
**可能原因**：
1. ❌ 路径错误
2. ❌ 权限不足
3. ❌ Python 环境问题
4. ❌ 网络连接问题

**解决方案**：
1. 手动运行 `K:\QT\daily_real_check.bat` 测试
2. 检查任务历史记录查看错误信息
3. 确保虚拟环境路径正确
4. 检查网络连接

### 邮件未收到
**可能原因**：
1. ❌ 邮件服务器连接失败
2. ❌ 邮件被拦截到垃圾邮件
3. ❌ 邮箱配置错误

**解决方案**：
1. 检查垃圾邮件文件夹
2. 运行脚本查看终端输出
3. 验证邮箱配置：`src\notification\email_config.py`

---

## 🔐 安全说明

### 权限要求
- 任务需要**最高权限**运行
- 确保 Python 脚本有文件读写权限
- 邮件配置文件包含敏感信息，注意保护

### 密码安全
- 邮箱密码存储在 `email_config.py`
- 建议使用应用专用密码（而非主密码）
- 定期更换密码

### 日志隐私
- 任务运行日志可能包含交易信号
- 注意保护日志文件访问权限

---

## 📈 执行流程

### 自动执行流程
```
08:00 任务触发
  ↓
运行 daily_real_check.bat
  ↓
执行 TSLA 策略检查
  ├─ 加载历史数据
  ├─ 运行回测
  ├─ 检查新信号
  ├─ 计算持仓信息
  └─ 发送邮件
  ↓
执行 NVDA 策略检查
  └─ (同上)
  ↓
执行 INTC 策略检查
  └─ (同上)
  ↓
完成 - 邮件发送到 qsswgl@gmail.com
```

### 预计执行时间
- TSLA: ~30秒
- NVDA: ~15秒
- INTC: ~15秒
- 邮件发送: ~10秒
- **总计**: 约 1-2 分钟

---

## 💡 使用建议

### 最佳实践
1. ✅ **定期检查**：每周查看一次任务运行记录
2. ✅ **测试运行**：设置后立即测试一次
3. ✅ **备份配置**：定期备份任务配置
4. ✅ **监控邮件**：确保每天都收到邮件
5. ✅ **及时更新**：策略调整后重新测试任务

### 时间调整建议
根据你的作息时间，可以调整执行时间：

| 北京时间 | 美东时间 | 说明 |
|---------|---------|------|
| 07:00 | 18:00 (前日) | 更早收到信号 |
| 08:00 | 19:00 (前日) | **当前设置** |
| 09:00 | 20:00 (前日) | 稍晚一些 |
| 21:00 | 08:00 (当日) | 美股开盘前 |
| 22:00 | 09:00 (当日) | 美股开盘时 |

---

## 📞 相关文档

- `DAILY_STRATEGY_USAGE_GUIDE.md` - 日度策略使用指南
- `POSITION_INFO_UPDATE.md` - 持仓信息功能说明
- `QUICK_START_GUIDE.md` - 快速入门指南

---

## 🆘 常见问题

### Q1: 任务创建失败，提示权限不足？
**A**: 必须以**管理员身份**运行 PowerShell 或 CMD。

### Q2: 任务显示"上次运行结果: 0x1"？
**A**: 这通常表示脚本执行出错，手动运行 `daily_real_check.bat` 查看具体错误。

### Q3: 如何确认任务已设置成功？
**A**: 运行以下命令：
```powershell
Get-ScheduledTask -TaskName "QT_DailyStrategyCheck"
```
如果显示任务信息，说明设置成功。

### Q4: 可以设置多个执行时间吗？
**A**: 可以！修改脚本中的触发器配置，或在任务计划程序中添加多个触发器。

### Q5: 周末和假期会运行吗？
**A**: 不会。任务只在工作日（周一至周五）运行。美股假期需要手动禁用任务。

### Q6: 如何临时停止自动执行？
**A**: 禁用任务：
```powershell
Disable-ScheduledTask -TaskName "QT_DailyStrategyCheck"
```

---

**设置日期**: 2025-11-18  
**版本**: v1.0  
**状态**: ✅ 可用
