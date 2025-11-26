# 🔑 API密钥申请与配置完整指南

**更新时间**: 2025-11-25  
**预计完成时间**: 30-60分钟  
**难度等级**: ⭐⭐ 中等

---

## 📋 概览

本指南将帮助您申请并配置6个数据源的API密钥:

| 数据源 | 优先级 | 申请难度 | 配置时间 | 免费额度 |
|--------|--------|----------|----------|----------|
| 1. Alpha Vantage | 🔴 高 | ⭐ 简单 | 2分钟 | 500次/天 |
| 2. Financial Modeling Prep | 🔴 高 | ⭐ 简单 | 3分钟 | 250次/天 |
| 3. NewsAPI | 🟡 中 | ⭐ 简单 | 2分钟 | 100次/天 |
| 4. Finnhub | 🟡 中 | ⭐⭐ 中等 | 3分钟 | 60次/分钟 |
| 5. FRED | 🟡 中 | ⭐⭐ 中等 | 5分钟 | 无限制 |
| 6. Tradier | 🟢 低 | ⭐⭐⭐ 复杂 | 10分钟 | 沙盒免费 |

**总计时间**: 约25分钟

---

## 🎯 快速开始(推荐路径)

### 方案A: 全部申请(推荐)
```
第1步: Alpha Vantage (2分钟) ✓
第2步: FMP (3分钟) ✓
第3步: NewsAPI (2分钟) ✓
第4步: Finnhub (3分钟) ✓
第5步: FRED (5分钟) ✓
第6步: Tradier (10分钟,可选) ✓
```

### 方案B: 优先核心(快速)
```
只申请前3个:
- Alpha Vantage (基本面+备用价格)
- FMP (财报数据)
- NewsAPI (新闻情绪)

15分钟完成核心功能!
```

---

## 📝 详细申请步骤

### 1️⃣ Alpha Vantage API (基本面+备用价格)

#### 申请步骤:
1. **访问网站**: https://www.alphavantage.co/support/#api-key
2. **填写信息**:
   ```
   Email: qsswgl@gmail.com (您的邮箱)
   First Name: (您的名字)
   Last Name: (您的姓氏)
   Organization: Personal (个人使用)
   Purpose: Stock trading analysis (股票交易分析)
   ```
3. **提交表单**: 点击 "GET FREE API KEY"
4. **获取密钥**: 页面会立即显示您的API密钥
   ```
   示例: ABCD1234EFGH5678
   ```
5. **保存密钥**: 复制到安全的地方
欢迎使用 Alpha Vantage！您的 API 密钥是：NC5N04GG5LICDE26。请将此 API 密钥记录在安全的地方，以便将来访问数据

#### 免费额度:
- ✅ 500次请求/天
- ✅ 5次请求/分钟
- ✅ 无需信用卡
- ✅ 永久免费

#### 测试命令:
```bash
# Windows PowerShell
$env:ALPHA_VANTAGE_API_KEY="NC5N04GG5LICDE26"
python -c "import os; from src.data.alphavantage import AlphaVantageClient; client = AlphaVantageClient(); print(client.fetch_daily('TSLA', lookback_days=10))"
```

#### 常见问题:
- **Q: 没收到邮件?**  
  A: API密钥会直接显示在网页上,不会发邮件

- **Q: 密钥格式?**  
  A: 通常是16位大写字母+数字组合

---

### 2️⃣ Financial Modeling Prep API (财报数据)

#### 申请步骤:
1. **访问网站**: https://site.financialmodelingprep.com/developer/docs/pricing
2. **选择免费计划**: 
   - 点击 "Free Plan"
   - 或直接访问: https://site.financialmodelingprep.com/register
3. **注册账户**:
   ```
   Email: qsswgl@gmail.com
   Password: qsswgl_5988856
   First Name: (您的名字)
   Last Name: (您的姓氏)
   ```
4. **验证邮箱**: 检查邮箱并点击验证链接
5. **登录Dashboard**: https://site.financialmodelingprep.com/developer
6. **复制API密钥**: 在Dashboard首页可以看到您的API Key
   ```
   示例: a1b2c3d4e5f6g7h8i9j0
   ```

#### 免费额度:
- ✅ 250次请求/天
- ✅ 实时股票数据
- ✅ 完整财报数据
- ✅ 无需信用卡

#### 测试命令:
```bash
# Windows PowerShell
$env:FMP_API_KEY="lUds2aNA8cqRjWukfsvb4TlgqvIvscrG"
python -c "from src.data.fundamentals import FundamentalsDataManager; mgr = FundamentalsDataManager(); print(mgr.get_company_overview('NVDA'))"
```

#### 常见问题:
- **Q: 找不到API密钥?**  
  A: 登录后在Dashboard首页,标题为 "Your API Key"

- **Q: 密钥不工作?**  
  A: 确保已验证邮箱,密钥需要验证后才激活

---

### 3️⃣ NewsAPI (新闻情绪)

#### 申请步骤:
1. **访问网站**: https://newsapi.org/register
2. **填写注册表单**:
   ```
   Email: qsswgl@gmail.com
   Password: (设置密码)
   First Name: (您的名字)
   ```
3. **选择用途**: 
   - 选择 "Personal Project" (个人项目)
   - 描述: "Stock market sentiment analysis"
4. **提交注册**: 点击 "Submit"
5. **查看邮箱**: 会收到包含API密钥的邮件
6. **或直接查看**: 登录后访问 https://newsapi.org/account
   ```
   示例: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
   ```

#### 免费额度:
- ✅ 100次请求/天
- ✅ 覆盖全球8万+新闻源
- ✅ 30天历史数据
- ❌ 仅供开发测试(不可商用)

#### 测试命令:
```bash
# Windows PowerShell
$env:NEWS_API_KEY="f104c471970142a0829943b3167138ac"
python -c "from src.data.news_sentiment import NewsDataManager; mgr = NewsDataManager(); news = mgr.get_news_with_sentiment('TSLA', days_back=1); print(f'获取到{len(news)}条新闻')"
```

#### 常见问题:
- **Q: 密钥格式?**  
  A: 32位小写字母+数字组合

- **Q: 商业使用?**  
  A: 需要付费计划,个人学习研究可以使用免费版

---

### 4️⃣ Finnhub API (金融新闻)

#### 申请步骤:
1. **访问网站**: https://finnhub.io/register
2. **注册账户**:
   ```
   Email: qsswgl@gmail.com
   Password: (qsswgl_5988856)
   Name: (您的名字)
   ```
3. **验证邮箱**: 点击邮件中的验证链接
4. **登录Dashboard**: https://finnhub.io/dashboard
5. **复制API密钥**: 在Dashboard页面可以看到 "API Key"
   ```
   示例: c123456789abcdef
   ```

#### 免费额度:
- ✅ 60次请求/分钟
- ✅ 实时股票数据
- ✅ 公司新闻
- ✅ 基本面数据
- ✅ 无需信用卡

#### 测试命令:
```bash
# Windows PowerShell
$env:FINNHUB_API_KEY="d4iqba1r01queuak46v0d4iqba1r01queuak46vg"
python -c "from src.data.news_sentiment import FinnhubNewsProvider; provider = FinnhubNewsProvider(); news = provider.get_company_news('TSLA'); print(f'获取到{len(news)}条新闻')"
```

#### 常见问题:
- **Q: 密钥在哪?**  
  A: 登录后Dashboard首页,大大的 "API Key" 区域

- **Q: 请求限制?**  
  A: 60次/分钟已经很充足,注意不要短时间大量请求

---

### 5️⃣ FRED API (宏观经济数据)

#### 申请步骤:
1. **访问网站**: https://fred.stlouisfed.org/
2. **创建账户**:
   - 点击右上角 "My Account" → "Create New Account"
   - 或直接访问: https://research.stlouisfed.org/useraccount/register
3. **填写注册表单**:
   ```
   Email: qsswgl@gmail.com
   Password: (设置密码)
   First Name: (您的名字)
   Last Name: (您的姓氏)
   ```
4. **验证邮箱**: 点击邮件中的验证链接
5. **申请API密钥**:
   - 登录后访问: https://fred.stlouisfed.org/docs/api/api_key.html
   - 点击 "Request API Key"
6. **填写API密钥申请表**:
   ```
   Purpose: Stock market research and analysis
   Application: Personal quantitative trading system
   ```
7. **提交申请**: 点击 "Request API key"
8. **获取密钥**: 密钥会显示在页面上并发送到邮箱
   ```
   示例: 0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
   ```

#### 免费额度:
- ✅ 无限制请求
- ✅ 美联储官方数据
- ✅ 80万+经济时间序列
- ✅ 实时更新
- ✅ 完全免费

#### 测试命令:
```bash
# Windows PowerShell
$env:FRED_API_KEY="88bdf123e50af3b9491018ec16832716"
python -c "from src.data.macro_data import MacroDataManager; mgr = MacroDataManager(); indicators = mgr.get_key_indicators(); print(indicators)"
```

#### 常见问题:
- **Q: 申请需要审核吗?**  
  A: 通常立即批准,密钥会马上显示

- **Q: 密钥格式?**  
  A: 32位小写字母+数字组合

---

### 6️⃣ Tradier API (期权数据) - 可选

#### 申请步骤:
1. **访问网站**: https://developer.tradier.com/getting_started
2. **创建账户**:
   - 点击 "Create Account"
   - 选择 "Sandbox Account" (沙盒账户,免费)
3. **填写注册表单**:
   ```
   Email: qsswgl@gmail.com
   Password: (设置密码)
   First Name: (您的名字)
   Last Name: (您的姓氏)
   ```
4. **验证邮箱**: 点击邮件中的验证链接
5. **登录Dashboard**: https://developer.tradier.com/user/apps
6. **创建应用**:
   - 点击 "Create a new application"
   - Application Name: "QT Trading System"
   - Description: "Quantitative trading system"
7. **获取密钥**: 创建应用后会显示 "Access Token"
   ```
   示例: Bearer abc123def456ghi789
   ```

#### 免费额度:
- ✅ 沙盒环境无限请求
- ✅ 完整期权链数据
- ✅ 实时报价(延迟15分钟)
- ❌ 沙盒数据可能不是最新

#### 备选方案:
如果Tradier申请困难,可以使用Yahoo Finance期权数据(无需API密钥):
```python
from src.data.options_data import YahooFinanceOptionsProvider
provider = YahooFinanceOptionsProvider()
options = provider.get_option_chain('NVDA')
```

#### 测试命令:
```bash
# Windows PowerShell
$env:TRADIER_API_KEY="您的密钥"
python -c "from src.data.options_data import OptionsDataManager; mgr = OptionsDataManager(); chain = mgr.get_options_analysis('TSLA'); print(chain)"
```

---

## 🔧 API密钥配置方法

### 方法1: 环境变量(推荐) ✅

#### Windows PowerShell (临时):
```powershell
# 设置环境变量(当前会话有效)
$env:ALPHA_VANTAGE_API_KEY="您的Alpha Vantage密钥"
$env:FMP_API_KEY="您的FMP密钥"
$env:NEWS_API_KEY="您的NewsAPI密钥"
$env:FINNHUB_API_KEY="您的Finnhub密钥"
$env:FRED_API_KEY="您的FRED密钥"
$env:TRADIER_API_KEY="您的Tradier密钥"

# 验证设置
echo $env:ALPHA_VANTAGE_API_KEY
```

#### Windows 系统环境变量(永久):
```
1. Win + R 输入: sysdm.cpl
2. 点击"高级"选项卡
3. 点击"环境变量"
4. 在"用户变量"区域点击"新建"
5. 添加以下变量:
   - 变量名: ALPHA_VANTAGE_API_KEY
   - 变量值: 您的密钥
6. 对每个API密钥重复步骤4-5
7. 点击"确定"保存
8. 重启PowerShell生效
```

### 方法2: .env 配置文件 ✅

**创建配置文件**:
```bash
# 在项目根目录创建 .env 文件
# K:\QT\.env
```

**文件内容**:
```ini
# API密钥配置文件
# 创建时间: 2025-11-25

# 1. Alpha Vantage (基本面+备用价格)
ALPHA_VANTAGE_API_KEY=您的密钥

# 2. Financial Modeling Prep (财报数据)
FMP_API_KEY=您的密钥

# 3. NewsAPI (新闻情绪)
NEWS_API_KEY=您的密钥

# 4. Finnhub (金融新闻)
FINNHUB_API_KEY=您的密钥

# 5. FRED (宏观经济)
FRED_API_KEY=您的密钥

# 6. Tradier (期权数据,可选)
TRADIER_API_KEY=您的密钥

# 社交媒体API(可选,暂不配置)
# REDDIT_CLIENT_ID=
# REDDIT_CLIENT_SECRET=
# STOCKTWITS_API_KEY=
```

**加载.env文件**:
```python
# 在代码中自动加载
from dotenv import load_dotenv
load_dotenv()  # 会自动读取.env文件
```

### 方法3: 配置文件(备选)

**创建 config.json**:
```json
{
  "api_keys": {
    "alpha_vantage": "您的密钥",
    "fmp": "您的密钥",
    "newsapi": "您的密钥",
    "finnhub": "您的密钥",
    "fred": "您的密钥",
    "tradier": "您的密钥"
  },
  "data_sources": {
    "enable_news": true,
    "enable_fundamentals": true,
    "enable_options": false,
    "enable_macro": true,
    "enable_social": false,
    "enable_insider": false
  }
}
```

---

## ✅ 配置验证

### 自动验证脚本:

我将创建一个自动化配置和测试脚本...

---

## 📊 申请进度追踪

### 申请清单:
```
□ Alpha Vantage    _____________________ (填写密钥)
□ FMP              _____________________ (填写密钥)
□ NewsAPI          _____________________ (填写密钥)
□ Finnhub          _____________________ (填写密钥)
□ FRED             _____________________ (填写密钥)
□ Tradier(可选)    _____________________ (填写密钥)
```

### 配置检查:
```
□ 环境变量已设置
□ .env文件已创建
□ 运行验证脚本
□ 所有数据源测试通过
```

---

## ⚠️ 安全注意事项

### 密钥安全:
1. **不要提交到Git**:
   ```bash
   # 确保 .env 在 .gitignore 中
   echo ".env" >> .gitignore
   ```

2. **不要分享密钥**:
   - 不要截图包含密钥的页面
   - 不要复制粘贴到公开聊天

3. **定期更换密钥**:
   - 每3-6个月更换一次
   - 如怀疑泄露,立即重置

4. **使用环境变量**:
   - 不要在代码中硬编码密钥
   - 使用 os.environ.get() 读取

---

## 🆘 常见问题

### Q1: 申请时需要信用卡吗?
A: 不需要!所有推荐的免费API都无需信用卡。

### Q2: 密钥会过期吗?
A: 大部分不会过期,但如果长期不用可能被停用。

### Q3: 超出免费额度怎么办?
A: 
- 增加缓存,减少重复请求
- 使用多个备用数据源
- 如确实需要,考虑付费计划

### Q4: 忘记密钥怎么办?
A: 登录各平台Dashboard即可查看,或重新生成。

### Q5: 所有密钥都必须申请吗?
A: 不是!可以根据需求只申请部分:
- 必需: Alpha Vantage, FMP
- 推荐: NewsAPI, FRED
- 可选: Finnhub, Tradier

---

## 📅 预估时间表

### 完整申请流程:
```
09:00 - 09:02  Alpha Vantage申请
09:02 - 09:05  FMP申请
09:05 - 09:07  NewsAPI申请
09:07 - 09:10  Finnhub申请
09:10 - 09:15  FRED申请
09:15 - 09:25  Tradier申请(可选)
09:25 - 09:30  配置环境变量
09:30 - 09:35  运行验证脚本
09:35 - 09:40  测试数据获取

总计: 30-40分钟
```

---

## 🎯 下一步

完成API密钥申请后:
1. ✅ 运行 `setup_api_keys.py` 配置脚本
2. ✅ 运行 `test_all_data_sources.py` 测试脚本
3. ✅ 查看 `ENABLE_DATA_SOURCES_GUIDE.md` 启用指南
4. ✅ 逐步启用各数据源到策略中

---

**文档版本**: v1.0  
**最后更新**: 2025-11-25  
**预计完成**: 30-60分钟  
**状态**: ✅ 完整指南

🔑 **准备好了吗?** 让我们开始申请API密钥吧!
