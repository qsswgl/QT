# Gmail 应用专用密码生成步骤（图文说明）

## ⚠️ 重要提示

**应用专用密码（App Password）≠ 通行密钥（Passkey）**

- ✅ 我们需要：**应用专用密码**（App Password）
- ❌ 不是：**通行密钥**（Passkey）

你刚才看到的"通行密钥和安全密钥"页面是错误的页面！

---

## 📝 正确步骤

### 第一步：确保启用两步验证

1. 访问：https://myaccount.google.com/security
2. 找到"登录Google"部分
3. 点击"两步验证"
4. 如果未启用，按提示启用（需要手机验证）

### 第二步：生成应用专用密码

#### 🎯 快速方法（直接访问）

**直接复制此链接到浏览器地址栏**：
```
https://myaccount.google.com/apppasswords
```

如果能打开，你会看到：
- 页面标题："应用专用密码" 或 "App passwords"
- 顶部有输入框，可以输入应用名称
- 或者有两个下拉菜单："选择应用"和"选择设备"

#### 📋 填写信息

**方式A：自定义名称（推荐）**
- 在顶部输入框输入：`QT Trading Bot` 或 `TSLA Strategy`
- 点击"生成"

**方式B：使用下拉菜单**
- 选择应用：`邮件` (Mail)
- 选择设备：`Windows计算机` (Windows Computer)
- 点击"生成"

### 第三步：复制密码

生成后会显示一个黄色框，里面有16位密码：
```
abcd efgh ijkl mnop
```

**重要操作**：
1. 完整复制这16位字符
2. 去掉所有空格
3. 最终结果：`abcdefghijklmnop`

### 第四步：填入配置文件

1. 打开文件：`K:\QT\src\notification\email_config.py`

2. 找到这一行：
```python
sender_password: str = "YOUR_APP_PASSWORD_HERE"
```

3. 替换为你的16位密码（去掉空格）：
```python
sender_password: str = "abcdefghijklmnop"  # 替换为你的实际密码
```

4. 保存文件（Ctrl+S）

---

## 🔍 常见问题

### Q1：找不到"应用专用密码"选项？

**原因和解决方案**：

1. **未启用两步验证**
   - 解决：先启用两步验证
   - 网址：https://myaccount.google.com/signinoptions/two-step-verification

2. **使用的是工作/学校账户**
   - Google Workspace账户可能被管理员禁用了此功能
   - 解决：使用个人Gmail账户

3. **浏览器缓存问题**
   - 解决：清除浏览器缓存，或使用无痕/隐私模式

4. **页面未加载完成**
   - 解决：刷新页面，或换一个浏览器（Chrome/Edge/Firefox）

### Q2：我进入了"通行密钥"页面怎么办？

**这是错误的页面！** 通行密钥（Passkey）不是我们需要的。

正确做法：
1. 点击浏览器的后退按钮
2. 或者直接访问：https://myaccount.google.com/apppasswords

### Q3：生成后忘记复制密码怎么办？

1. 返回应用专用密码页面
2. 删除刚才创建的密码
3. 重新生成一个新的

### Q4：一个账户可以生成多个应用专用密码吗？

可以！每个应用可以使用不同的密码，便于管理和撤销。

---

## ✅ 验证设置

完成配置后，运行测试：

```powershell
# 进入项目目录
cd K:\QT

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 运行测试
python -m src.pipeline.test_daily_email
```

成功的话会显示：
```
✅ 测试邮件发送成功!
```

并且你会在 `qsswgl@gmail.com` 收到测试邮件。

---

## 📞 需要帮助？

如果按照以上步骤仍然无法生成应用专用密码：

1. 确认账户类型（个人Gmail vs Google Workspace）
2. 确认两步验证已启用
3. 尝试不同浏览器
4. 访问 Google 帮助中心：https://support.google.com/accounts/answer/185833

---

## 🔗 快速链接

- **应用专用密码生成**：https://myaccount.google.com/apppasswords
- **两步验证设置**：https://myaccount.google.com/signinoptions/two-step-verification
- **账户安全设置**：https://myaccount.google.com/security
- **Google 帮助文档**：https://support.google.com/accounts/answer/185833

---

**创建日期**：2025-11-13  
**提示**：应用专用密码只显示一次，请妥善保存！
