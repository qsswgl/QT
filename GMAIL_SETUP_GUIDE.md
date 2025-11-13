# Gmail SMTP 配置指南

## 📧 已完成的配置

系统已自动将邮件发送配置改为 Gmail：

- **发件邮箱**: qsswgl@gmail.com
- **收件邮箱**: qsswgl@gmail.com
- **SMTP服务器**: smtp.gmail.com
- **SMTP端口**: 587 (TLS)

## ⚙️ 完成设置步骤

### 步骤 1：启用 Google 两步验证

1. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
2. 登录 `qsswgl@gmail.com` 账户
3. 在 "登录Google" 部分找到 **两步验证**
4. 点击启用并按照提示完成设置

### 步骤 2：生成应用专用密码（重要：不是通行密钥！）

**注意：应用专用密码 ≠ 通行密钥（Passkey）！我们需要的是App Password！**

#### 方法 1：直接访问（推荐）

1. 确保已启用两步验证（必需）
2. **直接访问此链接**：https://myaccount.google.com/apppasswords
3. 如果页面要求，输入你的Gmail账户密码
4. 在"应用专用密码"页面：
   - 在"选择应用"下拉菜单中选择：**邮件**
   - 在"选择设备"下拉菜单中选择：**Windows计算机**
   - 或者直接在顶部输入框输入自定义名称：如 "QT Trading Bot"
5. 点击 **生成** 按钮
6. 复制显示的 **16位密码**（格式如：`abcd efgh ijkl mnop`）
7. **重要**：去掉空格，变成：`abcdefghijklmnop`

#### 方法 2：从安全设置进入

1. 访问：https://myaccount.google.com/security
2. 滚动到"登录Google"部分
3. 找到并点击 **应用专用密码** (App passwords)
   - **注意**：不是"通行密钥"（Passkey）
   - 如果看不到"应用专用密码"选项，确保已启用两步验证
4. 按照上述方法1的步骤3-7操作

#### 如果找不到"应用专用密码"选项：

1. 确保已启用"两步验证"
2. 尝试从不同的浏览器访问（Chrome、Edge、Firefox）
3. 确保使用的是个人Gmail账户（不是Google Workspace账户）
4. 清除浏览器缓存后重试

### 步骤 3：填入应用专用密码

1. 打开配置文件：`src/notification/email_config.py`
2. 找到这一行：
   ```python
   sender_password: str = "YOUR_APP_PASSWORD_HERE"
   ```
3. 将 `YOUR_APP_PASSWORD_HERE` 替换为你生成的16位密码（**去掉空格**）
   ```python
   sender_password: str = "abcdefghijklmnop"  # 16位密码，去掉空格
   ```
4. 保存文件

### 步骤 4：测试邮件发送

运行测试脚本：
```powershell
python -m src.pipeline.test_daily_email
```

或直接运行日度策略检查：
```powershell
K:\QT\daily_strategy_check.bat
```

## 📌 重要提示

### Gmail 应用专用密码注意事项：

1. **16位密码**：生成的密码是16位字符，**去掉空格**后填入配置
2. **不是账户密码**：应用专用密码不是你的 Gmail 登录密码
3. **一次性显示**：密码只显示一次，请妥善保存
4. **可以重新生成**：如果忘记或泄露，可以删除旧密码并重新生成

### Gmail SMTP 限制：

- **发送限额**：每天最多 500 封邮件（个人账户）
- **频率限制**：建议发送间隔 > 1秒
- **安全检测**：首次发送可能触发安全警告，需登录确认

### 常见问题：

1. **错误：用户名和密码不正确**
   - 确保使用的是应用专用密码（16位），不是账户密码
   - 确保已启用两步验证

2. **错误：连接被拒绝**
   - 确保 SMTP 配置正确：smtp.gmail.com:587
   - 检查网络是否允许 SMTP 连接

3. **邮件进入垃圾箱**
   - 首次发送可能被标记为垃圾邮件
   - 手动将其标记为"非垃圾邮件"

## ✅ 配置文件位置

- **邮件配置**: `src/notification/email_config.py`
- **日度策略**: `src/pipeline/run_daily_check_email.py`
- **周度策略**: `src/pipeline/run_weekly_check_email.py`
- **批处理文件**: `daily_strategy_check.bat`, `weekly_strategy_check.bat`

## 🔐 安全建议

1. **不要分享**应用专用密码
2. **定期更换**应用专用密码（建议每季度）
3. **监控账户活动**：定期检查 [Google 账户活动](https://myaccount.google.com/notifications)
4. **使用环境变量**（可选）：可以将密码存储在环境变量中，而不是硬编码在配置文件

### 使用环境变量（高级选项）：

在 PowerShell 中设置：
```powershell
$env:GMAIL_APP_PASSWORD = "your_16_digit_password"
```

修改配置文件使用环境变量：
```python
import os
sender_password: str = os.getenv("GMAIL_APP_PASSWORD", "YOUR_APP_PASSWORD_HERE")
```

## 📞 获取帮助

- Google 帮助中心：https://support.google.com/accounts/answer/185833
- 应用专用密码管理：https://myaccount.google.com/apppasswords
- 账户安全设置：https://myaccount.google.com/security

---

**最后更新**: 2025-11-13
