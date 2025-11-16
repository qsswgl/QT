# 📧 邮件网络问题排查指南

## 🔍 问题诊断

你的邮件系统遇到了 **WinError 10060（网络超时）** 错误。

### 症状
```
❌ 邮件发送失败: [WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。
```

### 原因分析
1. **DNS解析**: ✅ 正常 (smtp.gmail.com → 142.250.99.109)
2. **端口连接**: ✅ 正常 (587端口可达)
3. **TLS握手**: ✅ 正常 (加密通道建立成功)
4. **SMTP登录**: ❌ **超时** (TLS加密后的数据传输超时)

这是**间歇性网络问题**，可能原因：
- 网络延迟过高（国内访问Gmail服务器）
- 防火墙/代理干扰TLS加密连接
- ISP对Gmail SMTP的连接限制
- VPN/代理不稳定

---

## 🛠️ 解决方案

### 方案1: 增加超时时间（已实施）

已在 `email_service.py` 中增加：
- SMTP超时: **60秒** (默认为5-10秒)
- 重试次数: **3次**
- 重试间隔: **5秒**

### 方案2: 使用VPN/代理

如果你有稳定的VPN或代理：

```powershell
# 设置代理（根据你的VPN配置修改）
$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"

# 运行策略检查
.\daily_strategy_check.bat
```

### 方案3: 换用其他邮件服务

如果Gmail连接始终不稳定，可以考虑：

#### 选项A: 使用QQ邮箱
```python
# 在 email_config.py 中修改
smtp_server: str = "smtp.qq.com"
smtp_port: int = 587
use_tls: bool = True
use_ssl: bool = False
```

#### 选项B: 使用163邮箱
```python
smtp_server: str = "smtp.163.com"
smtp_port: int = 465
use_tls: bool = False
use_ssl: bool = True
```

### 方案4: 修改Windows网络设置

#### 4.1 禁用IPv6（有时可以改善Gmail连接）
```powershell
# 以管理员身份运行
netsh interface ipv6 set global randomizeidentifiers=disabled
netsh interface ipv6 set privacy state=disabled
```

#### 4.2 刷新DNS缓存
```powershell
ipconfig /flushdns
```

#### 4.3 修改DNS服务器（使用Google DNS）
```powershell
# 以管理员身份运行
netsh interface ip set dns "以太网" static 8.8.8.8
netsh interface ip add dns "以太网" 8.8.4.4 index=2
```

### 方案5: 网络高峰时段避免执行

如果你发现某些时段网络特别稳定：

```bat
REM 在 daily_strategy_check.bat 中添加时间判断
@echo off
echo 等待网络空闲时段...
timeout /t 3600 >nul
.\daily_strategy_check.bat
```

---

## 🧪 测试网络稳定性

运行以下命令测试对Gmail的连接质量：

```powershell
# 测试1: Ping Gmail邮件服务器
ping smtp.gmail.com -n 10

# 测试2: 测试端口连接
Test-NetConnection smtp.gmail.com -Port 587

# 测试3: 完整邮件系统测试
.\.venv\Scripts\python.exe src\notification\test_email_system.py

# 测试4: 简化版邮件发送测试
.\.venv\Scripts\python.exe src\notification\test_simple_email.py
```

---

## 📊 监控和日志

### 查看详细的SMTP调试信息

创建测试脚本 `test_smtp_debug.py`:

```python
import smtplib
import sys

server = None
try:
    print("连接SMTP服务器...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=120)
    server.set_debuglevel(2)  # 启用详细调试
    
    print("\n启动TLS...")
    server.starttls()
    
    print("\n登录...")
    server.login('qsswgl@gmail.com', 'clhbzzxtafvinvni')
    
    print("\n✅ 连接成功!")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    if server:
        try:
            server.quit()
        except:
            pass
```

运行：
```powershell
.\.venv\Scripts\python.exe test_smtp_debug.py
```

---

## 💡 建议

### 短期方案
每次运行策略前先测试邮件系统：
```powershell
# 1. 测试邮件系统
.\.venv\Scripts\python.exe src\notification\test_email_system.py

# 2. 如果测试通过，立即运行策略
.\daily_strategy_check.bat
```

### 长期方案
1. **考虑使用国内邮件服务**（QQ邮箱/163邮箱）- 网络更稳定
2. **配置企业级邮件转发服务**（如SendGrid, Mailgun）
3. **使用本地SMTP服务器**作为中转
4. **改用其他通知方式**（微信公众号、钉钉机器人、Telegram Bot）

---

## 🚨 紧急情况处理

如果邮件系统完全无法工作，你仍可以：

### 手动检查策略结果

```powershell
# 1. 运行策略但忽略邮件错误
.\daily_strategy_check.bat

# 2. 查看信号文件
Get-Content backtest_results\daily\signals_daily.csv | Select-Object -Last 5

# 3. 查看执行日志
Get-Content STRATEGY_EXECUTION_LOG.md | Select-Object -Last 50
```

### 禁用邮件推送

在 `src/notification/email_config.py` 中：
```python
enabled: bool = False  # 临时禁用邮件
```

---

## 📝 记录问题

如果问题持续，请记录：

```powershell
# 生成诊断报告
.\.venv\Scripts\python.exe src\notification\test_email_system.py > email_diagnostic_report.txt 2>&1

# 测试网络质量
ping smtp.gmail.com -n 100 > network_quality_report.txt

# 测试时间
echo "测试时间: $(Get-Date)" >> email_diagnostic_report.txt
```

将报告保存后可以分析网络问题的时间规律。

---

## ✅ 当前系统状态

- ✅ 代码已优化（60秒超时 + 3次重试）
- ✅ 邮件配置正确（测试曾经成功）
- ❌ 网络连接不稳定（间歇性超时）

**建议**: 先使用方案2（VPN/代理）或方案3（换用国内邮箱）快速解决问题。
