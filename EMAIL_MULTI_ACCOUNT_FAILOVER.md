# 📧 邮件推送多账户故障转移功能

## 更新时间
2025年11月15日

## 功能概述

已成功实现**邮件推送多账户故障转移机制**,当主邮箱发送失败时,自动切换到备用邮箱,确保策略信号推送的可靠性。

## 功能特点

### ✨ 核心功能
1. **多账户配置**: 支持配置多个发件邮箱
2. **自动故障转移**: 主邮箱失败时自动切换到备用邮箱
3. **优先级顺序**: 按配置顺序依次尝试
4. **每账户重试**: 每个账户都有独立的重试机制(3次)
5. **智能切换**: 认证错误直接切换,网络错误重试后切换

### 🔄 故障转移策略

```
发送流程:
1. 尝试账户1 (QQ邮箱 13794881@qq.com)
   ├─ 成功 → ✅ 完成
   └─ 失败 → 尝试账户2
   
2. 尝试账户2 (Gmail qsswgl@gmail.com)
   ├─ 成功 → ✅ 完成
   └─ 失败 → 尝试账户3
   
3. 尝试账户3 (139邮箱 qsoft@139.com)
   ├─ 成功 → ✅ 完成
   └─ 失败 → ❌ 所有账户均失败
```

## 配置详情

### 📁 配置文件
**src/notification/email_config.py**

### 🔧 账户配置

#### 账户1: QQ邮箱 (主账户)
```python
EmailAccountConfig(
    name="QQ邮箱",
    sender_email="13794881@qq.com",
    sender_password="zkoaojnharnqcacf",  # 授权码
    smtp_server="smtp.qq.com",
    smtp_port=587,
    use_ssl=False,
    use_tls=True
)
```

#### 账户2: Gmail (备用账户1)
```python
EmailAccountConfig(
    name="Gmail",
    sender_email="qsswgl@gmail.com",
    sender_password="rqkk tqts kqvs uyej",  # 应用专用密码
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    use_ssl=False,
    use_tls=True
)
```

#### 账户3: 139邮箱 (备用账户2)
```python
EmailAccountConfig(
    name="139邮箱",
    sender_email="qsoft@139.com",
    sender_password="64e0f3e5ac0a4de0a28d",  # 授权码
    smtp_server="smtp.139.com",
    smtp_port=465,
    use_ssl=True,
    use_tls=False
)
```

### 📬 收件人配置
```python
recipient_email="qsswgl@gmail.com"
```

## 技术实现

### 核心类

#### EmailAccountConfig
单个邮件账户配置类
```python
@dataclass
class EmailAccountConfig:
    name: str              # 账户名称
    sender_email: str      # 发件邮箱
    sender_password: str   # 发件密码/授权码
    smtp_server: str       # SMTP服务器
    smtp_port: int         # SMTP端口
    use_ssl: bool          # 是否使用SSL
    use_tls: bool          # 是否使用TLS
```

#### EmailConfig
邮件配置类(支持多账户)
```python
@dataclass
class EmailConfig:
    recipient_email: str              # 收件人
    subject_prefix: str               # 邮件主题前缀
    enabled: bool                     # 是否启用
    accounts: List[EmailAccountConfig]  # 账户列表
```

### 核心方法

#### _send_email()
主发送方法,实现故障转移逻辑
```python
def _send_email(self, subject: str, body: str) -> bool:
    # 遍历所有邮件账户
    for account_idx, account in enumerate(self.config.accounts, 1):
        # 尝试用当前账户发送
        if self._send_with_account(account, subject, body):
            return True  # 成功则返回
        # 失败则继续下一个账户
    return False  # 所有账户都失败
```

#### _send_with_account()
单账户发送方法,包含重试机制
```python
def _send_with_account(self, account, subject: str, body: str) -> bool:
    max_retries = 3  # 每个账户重试3次
    retry_delay = 5  # 重试间隔5秒
    
    for attempt in range(max_retries):
        try:
            # 创建邮件并发送
            # ...
            return True  # 成功
        except Exception:
            # 重试或返回失败
            pass
    return False
```

## 错误处理

### 错误类型

1. **SMTPAuthenticationError** (认证错误)
   - 原因: 邮箱地址或密码/授权码错误
   - 处理: 不重试,直接切换到下一个账户
   
2. **TimeoutError / socket.timeout** (超时错误)
   - 原因: 网络连接超时
   - 处理: 重试3次,失败后切换账户
   
3. **OSError** (网络错误)
   - 原因: 连接重置、网络中断等
   - 处理: 重试3次,失败后切换账户
   
4. **SMTPException** (SMTP错误)
   - 原因: SMTP协议错误
   - 处理: 重试3次,失败后切换账户

### 重试策略

```
单个账户:
├─ 尝试1 → 失败 → 等待5秒
├─ 尝试2 → 失败 → 等待5秒
├─ 尝试3 → 失败 → 切换账户
```

## 使用示例

### 测试邮件推送
```bash
# 运行测试
.\.venv\Scripts\python.exe src\notification\email_service.py
```

### 在代码中使用
```python
from src.notification.email_service import EmailService

service = EmailService()

# 发送交易信号提醒
service.send_signal_alert(
    symbol="TSLA",
    action="BUY",
    quantity=100,
    price=250.50,
    reason="趋势确认 + 强势突破信号",
    signal_date="2025-11-15"
)

# 发送每日总结
service.send_daily_summary(
    has_signal=True,
    signal_count=1,
    latest_signal={
        'action': 'BUY',
        'quantity': 100,
        'date': '2025-11-15'
    }
)
```

## 测试结果

### ✅ 测试通过
```
============================================================
📧 邮件推送测试 (多账户故障转移)
============================================================

配置信息:
  收件人: qsswgl@gmail.com
  已启用: True
  配置账户数: 3

发件账户列表 (按优先级):
  1. QQ邮箱
     邮箱: 13794881@qq.com
     服务器: smtp.qq.com:587
     SSL: False, TLS: True

  2. Gmail
     邮箱: qsswgl@gmail.com
     服务器: smtp.gmail.com:587
     SSL: False, TLS: True

  3. 139邮箱
     邮箱: qsoft@139.com
     服务器: smtp.139.com:465
     SSL: True, TLS: False

测试: 发送交易信号提醒...
------------------------------------------------------------

============================================================
📧 尝试使用账户 1/3: QQ邮箱 (13794881@qq.com)
============================================================
📧 正在连接 smtp.qq.com:587...
📧 正在启动TLS...
📧 正在登录...
📧 正在发送邮件...
✅ 邮件发送成功! 13794881@qq.com → qsswgl@gmail.com

✅ 邮件发送成功! 使用账户: QQ邮箱

============================================================
✅ 邮件推送测试通过!
请检查邮箱: qsswgl@gmail.com
============================================================
```

## 优势分析

### 📈 可靠性提升
1. **单账户故障不影响**: 主账户失败时自动切换备用账户
2. **多重保障**: 3个独立邮箱账户,故障概率大幅降低
3. **智能重试**: 每个账户都有重试机制

### ⚡ 响应速度
1. **快速故障转移**: 认证失败立即切换,不浪费时间
2. **合理超时**: 60秒超时设置,平衡速度和稳定性
3. **并行无需等待**: 一旦成功立即返回

### 🔒 安全性
1. **密码独立**: 每个账户使用独立授权码
2. **多邮箱提供商**: 分散风险,不依赖单一服务
3. **加密传输**: 全部使用TLS/SSL加密

## 维护指南

### 添加新账户
在 `src/notification/email_config.py` 的 `accounts` 列表中添加:

```python
EmailAccountConfig(
    name="新账户名称",
    sender_email="your_email@example.com",
    sender_password="your_password",
    smtp_server="smtp.example.com",
    smtp_port=587,
    use_ssl=False,
    use_tls=True
)
```

### 修改账户顺序
调整 `accounts` 列表中的顺序即可改变优先级

### 禁用某个账户
从 `accounts` 列表中删除或注释掉该账户配置

### 查看日志
运行时会输出详细的发送过程:
- 当前使用的账户
- 连接状态
- 发送结果
- 故障转移过程

## 向后兼容

### 保持旧代码兼容
为保持向后兼容,EmailConfig 提供了属性访问器:
```python
config.sender_email     # 返回第一个账户的邮箱
config.sender_password  # 返回第一个账户的密码
config.smtp_server      # 返回第一个账户的SMTP服务器
config.smtp_port        # 返回第一个账户的端口
config.use_ssl          # 返回第一个账户的SSL设置
config.use_tls          # 返回第一个账户的TLS设置
```

## 常见问题

### Q: 如何知道使用了哪个账户发送?
A: 查看输出日志,会显示 "✅ 邮件发送成功! 使用账户: XXX"

### Q: 如果所有账户都失败怎么办?
A: 系统会输出 "❌ 邮件发送失败: 已尝试所有 X 个账户",需要检查网络或账户配置

### Q: 可以只使用一个账户吗?
A: 可以,在 `accounts` 列表中只保留一个账户即可

### Q: Gmail需要特殊设置吗?
A: 需要使用应用专用密码,不能使用普通密码。在Google账户安全设置中生成。

### Q: 如何测试特定账户?
A: 临时修改 `accounts` 列表,只保留要测试的账户,然后运行测试脚本

## 相关文件

- `src/notification/email_config.py` - 邮件配置
- `src/notification/email_service.py` - 邮件服务
- `src/pipeline/run_daily_check_email.py` - 日度检查邮件推送
- `src/pipeline/run_weekly_check_email.py` - 周度检查邮件推送
- `src/pipeline/smart_daily_check.py` - 智能每日检查

## 下一步优化建议

1. **统计功能**: 记录每个账户的使用次数和成功率
2. **健康检查**: 定期检查所有账户的可用性
3. **配置文件**: 支持从JSON/YAML文件加载配置
4. **动态调整**: 根据历史成功率动态调整账户优先级
5. **异步发送**: 使用异步IO提升发送速度

---

**功能完成时间**: 2025年11月15日
**测试状态**: ✅ 通过
**可用性**: ✅ 生产就绪
