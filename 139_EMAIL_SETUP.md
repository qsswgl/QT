# 📧 139邮箱 SMTP 设置步骤

## 🔍 当前问题

**错误信息**: `450 Mail rejected, please try again`

**原因**: 139邮箱需要先激活或配置 SMTP 服务

---

## ✅ 139邮箱设置步骤

### Step 1: 登录139邮箱网页版

访问: https://mail.10086.cn

使用 qsoft@139.com 登录

### Step 2: 开启SMTP服务

1. 点击右上角 **设置**
2. 进入 **客户端设置** 或 **POP3/SMTP/IMAP**
3. 找到 **SMTP服务** 选项
4. **开启** SMTP服务
5. 如果需要，生成新的授权码

### Step 3: 发送一封测试邮件

在网页版发送一封邮件到任意地址（激活发信功能）

### Step 4: 检查配置

确认以下信息：
- SMTP服务器: smtp.139.com
- SMTP端口: 25
- 加密方式: TLS
- 授权码: 574a283d502db51ea200

---

## 🧪 测试当前配置

```powershell
cd k:\QT
.\.venv\Scripts\python.exe src\notification\test_email_system.py
```

**当前测试结果**:
- ✅ DNS解析: 成功
- ✅ 端口连接: 成功
- ✅ SMTP连接: 成功
- ✅ 认证: 成功
- ❌ 发送邮件: 失败 (450错误)

---

## 💡 替代方案: QQ邮箱（推荐）

QQ邮箱通常更稳定，成功率更高。

### QQ邮箱配置

如果有QQ邮箱，可以尝试：

1. 登录 https://mail.qq.com
2. 设置 → 账户 → 开启 **SMTP服务**
3. 生成授权码
4. 运行切换工具:
   ```powershell
   .\.venv\Scripts\python.exe src\notification\switch_to_qq_email.py
   ```

---

## 📝 当前配置

已配置 139 邮箱:
- 发件人: qsoft@139.com
- 收件人: qsswgl@gmail.com
- SMTP: smtp.139.com:25 (TLS)
- 授权码: 574a283d502db51ea200

---

## 🔄 如需恢复Gmail配置

```python
# 在 email_config.py 中修改:
sender_email: str = "qsswgl@gmail.com"
sender_password: str = "clhbzzxtafvinvni"
smtp_server: str = "smtp.gmail.com"
smtp_port: int = 587
use_ssl: bool = False
use_tls: bool = True
```

---

**更新时间**: 2025-11-14 23:10  
**状态**: 139邮箱认证成功，但发送被拒绝（450错误）  
**建议**: 完成139邮箱设置步骤，或改用QQ邮箱
