# PowerShell 运行批处理文件说明

## ⚠️ 重要提示

在PowerShell中运行批处理文件（.bat）时，**必须使用 `.\` 前缀**！

## ✅ 正确方法

### 方法1: 在PowerShell中运行（推荐）

```powershell
# TSLA策略
cd K:\QT
.\daily_strategy_check.bat      # ✅ 正确
.\weekly_strategy_check.bat     # ✅ 正确

# NVDA策略
cd K:\QT\NVDA
.\daily_strategy_check_nvda.bat # ✅ 正确

# INTC策略
cd K:\QT\INTC
.\daily_strategy_check_intc.bat # ✅ 正确
```

### 方法2: 在文件管理器中双击（最简单）

1. 打开文件管理器
2. 导航到对应目录
3. 双击 `.bat` 文件即可运行

### 方法3: 使用完整路径

```powershell
# 不需要cd，直接运行
K:\QT\NVDA\daily_strategy_check_nvda.bat   # ✅ 在CMD中可以
& K:\QT\NVDA\daily_strategy_check_nvda.bat # ✅ 在PowerShell中使用 &
```

## ❌ 错误方法

```powershell
# ❌ 错误 - 缺少 .\
cd K:\QT\NVDA
daily_strategy_check_nvda.bat

# 错误提示：
# 无法将"daily_strategy_check_nvda.bat"项识别为 cmdlet、函数、脚本文件或可运行程序的名称
```

## 🔍 为什么需要 `.\`？

PowerShell出于安全考虑，**不会从当前目录自动执行程序**。

- `.\` 明确告诉PowerShell："我要运行当前目录下的文件"
- 这是PowerShell的安全特性，防止意外执行恶意程序

## 📝 快速参考

| 场景 | 命令 |
|------|------|
| TSLA日度策略 | `cd K:\QT; .\daily_strategy_check.bat` |
| TSLA周度策略 | `cd K:\QT; .\weekly_strategy_check.bat` |
| NVDA日度策略 | `cd K:\QT\NVDA; .\daily_strategy_check_nvda.bat` |
| INTC日度策略 | `cd K:\QT\INTC; .\daily_strategy_check_intc.bat` |

## 💡 小技巧

### 使用Tab自动补全

```powershell
cd K:\QT\NVDA
.\dai<Tab>  # 按Tab键自动补全为 .\daily_strategy_check_nvda.bat
```

### 查看帮助

```powershell
# 查看PowerShell命令执行规则
Get-Help about_Command_Precedence
```

### 切换到CMD

如果不习惯PowerShell，可以切换到传统的CMD：

```cmd
# 在PowerShell中输入
cmd

# 然后就可以直接运行（不需要 .\）
cd K:\QT\NVDA
daily_strategy_check_nvda.bat
```

## 🔧 常见问题

### Q1: 为什么CMD不需要 `.\`？

**A**: CMD会自动在当前目录查找可执行文件，而PowerShell不会。

### Q2: 可以修改PowerShell的行为吗？

**A**: 可以，但**不推荐**（会降低安全性）：

```powershell
# 不推荐 - 将当前目录添加到PATH
$env:PATH += ";."
```

### Q3: 每次都要输入 `.\` 太麻烦？

**A**: 有3个更简单的方法：

1. **双击运行** - 最简单！
2. **创建快捷方式** - 放到桌面
3. **使用Windows任务计划程序** - 自动定时运行

## 📋 总结

记住这个简单规则：

```
PowerShell中运行.bat文件 = .\ + 文件名
```

示例：
- ✅ `.\daily_strategy_check.bat`
- ❌ `daily_strategy_check.bat`

---

最后更新: 2025-11-14
