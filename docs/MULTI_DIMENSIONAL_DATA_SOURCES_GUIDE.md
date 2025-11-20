# 多维度数据源系统 - 完整指南

## 📚 概述

本系统已集成**7大类数据源**,提供股票投资的全方位数据支持:

1. **价格数据** - Yahoo Finance, Alpha Vantage, Twelve Data
2. **新闻情绪** - NewsAPI, Finnhub News
3. **基本面数据** - Financial Modeling Prep, Alpha Vantage
4. **期权数据** - Tradier, Yahoo Finance Options
5. **宏观经济** - FRED (美联储经济数据), World Bank
6. **社交媒体** - Reddit, StockTwits
7. **内部人交易** - SEC EDGAR, Financial Modeling Prep

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

requirements.txt需包含:
```
yfinance>=0.2
requests>=2.31
pandas>=2.2
```

### 2. 配置API密钥

在系统环境变量中设置以下API密钥:

```bash
# Windows PowerShell
$env:NEWS_API_KEY="your_newsapi_key"
$env:FINNHUB_API_KEY="your_finnhub_key"
$env:FMP_API_KEY="your_fmp_key"
$env:ALPHAVANTAGE_API_KEY="your_alphavantage_key"
$env:TRADIER_API_KEY="your_tradier_key"
$env:FRED_API_KEY="your_fred_key"
$env:TWELVE_DATA_KEY="your_twelvedata_key"
```

### 3. 使用统一接口

```python
from src.data.unified_provider import UnifiedDataProvider

# 初始化数据源
provider = UnifiedDataProvider()

# 获取TSLA综合分析
analysis = provider.get_comprehensive_analysis('TSLA')

# 生成报告
report = provider.generate_report('TSLA', save_path='TSLA_report.md')
```

---

## 📊 数据源详解

### 1️⃣ 价格数据源

#### Yahoo Finance (主要)
- **文件**: `src/data/providers.py`
- **优点**: 免费,无需API密钥,数据质量高
- **限制**: 有访问频率限制
- **使用**:
```python
from src.data.providers import YFinanceClient

client = YFinanceClient()
data = client.fetch_daily_history('TSLA', '2024-01-01', '2024-12-31')
```

#### Alpha Vantage (备用)
- **文件**: `src/data/alphavantage.py`
- **API申请**: https://www.alphavantage.co/support/#api-key
- **限制**: 500次/天, 5次/分钟
- **使用**:
```python
from src.data.alphavantage import AlphaVantageClient

client = AlphaVantageClient()
data = client.fetch_daily_history('TSLA', '2024-01-01', '2024-12-31')
```

---

### 2️⃣ 新闻情绪数据源

#### NewsAPI
- **文件**: `src/data/news_sentiment.py`
- **API申请**: https://newsapi.org/
- **免费版**: 100次/天
- **功能**: 获取英文新闻,支持关键词搜索
- **使用**:
```python
from src.data.news_sentiment import NewsDataManager

manager = NewsDataManager()
result = manager.get_stock_sentiment('TSLA', days_back=7)

print(f"整体情绪: {result['overall_sentiment']['sentiment']}")
print(f"新闻总数: {result['overall_sentiment']['total_news']}")
```

#### Finnhub News
- **API申请**: https://finnhub.io/
- **免费版**: 60次/分钟
- **功能**: 公司新闻、市场新闻
- **特点**: 数据更新快,专注金融新闻

**情绪分析**: 自动分析新闻标题和内容,计算情绪得分(-1到1)

---

### 3️⃣ 基本面数据源

#### Financial Modeling Prep
- **文件**: `src/data/fundamentals.py`
- **API申请**: https://site.financialmodelingprep.com/developer/docs/
- **免费版**: 250次/天
- **提供数据**:
  - 公司概况
  - 利润表 (Income Statement)
  - 资产负债表 (Balance Sheet)
  - 现金流量表 (Cash Flow)
  - 关键财务指标 (PE, ROE, ROA等)
  - 财报发布日历

**使用示例**:
```python
from src.data.fundamentals import FundamentalsDataManager

manager = FundamentalsDataManager()
analysis = manager.get_comprehensive_analysis('TSLA')

# 查看财务健康度
health = manager.calculate_financial_health_score(analysis)
print(f"财务评分: {health['score']}/100")
print(f"评级: {health['grade']}")
```

#### Alpha Vantage基本面
- **功能**: 公司概况、盈利数据
- **优点**: 数据详细,包含TTM指标
- **限制**: 与价格数据共享API配额

---

### 4️⃣ 期权数据源

#### Tradier
- **文件**: `src/data/options_data.py`
- **API申请**: https://developer.tradier.com/
- **沙盒环境**: 免费,无限制
- **生产环境**: 需付费
- **提供数据**:
  - 期权链 (Option Chains)
  - 期权报价
  - 到期日列表

#### Yahoo Finance Options
- **优点**: 完全免费
- **功能**: 期权链、Greeks
- **使用**:
```python
from src.data.options_data import OptionsDataManager

manager = OptionsDataManager()
analysis = manager.get_options_analysis('TSLA')

# 查看期权情绪
sentiment = analysis['sentiment_analysis']
print(f"Put/Call比率: {sentiment['put_call_ratio']}")
print(f"市场情绪: {sentiment['sentiment']}")
print(f"Max Pain: ${sentiment['max_pain']}")
```

**期权指标**:
- **Put/Call Ratio**: >1.2看跌, <0.8看涨
- **Max Pain**: 期权卖方损失最小的价格
- **未平仓合约**: 市场关注度指标

---

### 5️⃣ 宏观经济数据源

#### FRED (美联储经济数据)
- **文件**: `src/data/macro_data.py`
- **API申请**: https://fred.stlouisfed.org/docs/api/api_key.html
- **免费版**: 无限制
- **提供数据**:
  - 联邦基金利率 (DFF)
  - 10年期-2年期国债利差 (T10Y2Y)
  - CPI消费者物价指数 (CPIAUCSL)
  - 失业率 (UNRATE)
  - GDP数据

**使用示例**:
```python
from src.data.macro_data import MacroDataManager

manager = MacroDataManager()
snapshot = manager.get_macro_snapshot()

# 查看经济健康度
health = snapshot['health_score']
print(f"经济评分: {health['score']}/100")
print(f"评级: {health['grade']}")
```

**关键指标解读**:
- **收益率曲线倒挂** (10Y-2Y<0): 衰退预警信号
- **高通胀** (CPI>5%): 央行可能加息,利空股市
- **低失业率** (<4%): 经济强劲,利好股市

#### World Bank
- **功能**: 全球经济数据
- **优点**: 无需API密钥
- **数据**: GDP、通胀率、失业率(各国)

---

### 6️⃣ 社交媒体情绪

#### Reddit
- **文件**: `src/data/social_sentiment.py`
- **数据来源**: r/wallstreetbets, 股票专属板块
- **免费**: 无需API密钥
- **指标**: 帖子数、点赞数、评论数、情绪分析

#### StockTwits
- **功能**: 股票讨论流
- **特点**: 自带情绪标签 (Bullish/Bearish)
- **API**: 免费,无需密钥

**使用示例**:
```python
from src.data.social_sentiment import SocialMediaDataManager

manager = SocialMediaDataManager()
result = manager.get_social_sentiment('TSLA')

# 查看综合情绪
combined = result['combined_metrics']
print(f"整体情绪: {combined['overall_sentiment']}")
print(f"看涨比例: {combined['bullish_ratio']*100:.1f}%")
print(f"讨论总数: {combined['total_posts']}")
```

**情绪关键词**:
- **看涨**: moon, rocket, bull, buy, hold, diamond hands
- **看跌**: bear, puts, sell, short, crash, dump

---

### 7️⃣ 内部人交易数据

#### SEC EDGAR
- **文件**: `src/data/insider_trading.py`
- **数据来源**: SEC官方Form 4报告
- **免费**: 需提供User-Agent
- **注意**: 数据需要XML解析

#### Financial Modeling Prep
- **优点**: 数据已结构化
- **功能**: 内部人交易记录、持股名单
- **使用**:
```python
from src.data.insider_trading import InsiderDataManager

manager = InsiderDataManager()
analysis = manager.get_insider_analysis('TSLA', days=90)

# 查看内部人情绪
sentiment = analysis['sentiment']
print(f"买入比例: {sentiment['buy_ratio']*100:.1f}%")
print(f"情绪: {sentiment['sentiment']}")
```

**解读**:
- **买入比例>70%**: 强烈看涨信号
- **买入比例<30%**: 看跌信号
- **重大交易** (>$1M): 特别关注

---

## 🎯 综合评分系统

统一数据源管理器会自动整合所有数据,计算**综合投资评分**(0-100):

### 评分权重
- 基本面: 25%
- 新闻情绪: 15%
- 社交媒体: 15%
- 期权情绪: 15%
- 内部人交易: 15%
- 宏观环境: 15%

### 评级标准
- **A (80-100)**: 强烈买入
- **B (70-79)**: 买入
- **C (60-69)**: 持有
- **D (50-59)**: 观望
- **F (0-49)**: 谨慎

---

## 🔧 API密钥申请指南

### 1. NewsAPI
1. 访问 https://newsapi.org/
2. 点击"Get API Key"
3. 注册账号
4. 复制API密钥
5. 免费版: 100次/天

### 2. Finnhub
1. 访问 https://finnhub.io/
2. 注册账号
3. 在Dashboard找到API Key
4. 免费版: 60次/分钟

### 3. Financial Modeling Prep
1. 访问 https://site.financialmodelingprep.com/developer/docs/
2. 注册账号
3. 获取API Key
4. 免费版: 250次/天

### 4. Alpha Vantage
1. 访问 https://www.alphavantage.co/support/#api-key
2. 填写邮箱获取密钥
3. 免费版: 500次/天, 5次/分钟

### 5. Tradier
1. 访问 https://developer.tradier.com/
2. 注册账号
3. 创建沙盒应用
4. 获取API Token
5. 沙盒环境免费

### 6. FRED
1. 访问 https://fred.stlouisfed.org/docs/api/api_key.html
2. 创建账号
3. 申请API Key
4. 完全免费,无限制

---

## 📈 使用示例

### 示例1: 生成综合分析报告

```python
from src.data.unified_provider import UnifiedDataProvider

provider = UnifiedDataProvider()

# 生成TSLA综合报告
report = provider.generate_report(
    symbol='TSLA',
    save_path='reports/TSLA_analysis.md'
)

print(report)
```

### 示例2: 单独使用某个数据源

```python
# 只获取新闻情绪
from src.data.news_sentiment import NewsDataManager

manager = NewsDataManager()
result = manager.get_stock_sentiment('NVDA', days_back=7)

# 只获取基本面
from src.data.fundamentals import FundamentalsDataManager

manager = FundamentalsDataManager()
analysis = manager.get_comprehensive_analysis('INTC')
health = manager.calculate_financial_health_score(analysis)
```

### 示例3: 批量分析多只股票

```python
from src.data.unified_provider import UnifiedDataProvider

provider = UnifiedDataProvider()
symbols = ['TSLA', 'NVDA', 'INTC', 'AAPL', 'MSFT']

for symbol in symbols:
    print(f"\n分析{symbol}...")
    analysis = provider.get_comprehensive_analysis(symbol)
    score = analysis['综合评分']
    print(f"{symbol}: {score['score']}/100 - {score['recommendation']}")
```

---

## ⚠️ 注意事项

### API限制
1. **合理使用**: 遵守各API的调用频率限制
2. **缓存数据**: 对于不经常变化的数据(如基本面),建议本地缓存
3. **错误处理**: 所有数据源都有failover机制,自动切换备用源

### 数据质量
1. **新闻情绪**: 基于关键词分析,可能不如深度学习模型准确
2. **社交媒体**: 存在噪音和操纵,需结合其他指标
3. **内部人交易**: 存在滞后性,需定期更新

### 成本控制
1. **免费版限制**: 大部分API都有免费版,足够个人使用
2. **付费升级**: 如需高频交易或大量数据,考虑付费版本
3. **混合策略**: 优先使用免费数据源,付费源作为补充

---

## 🔄 后续优化方向

### 1. 数据缓存
- 实现Redis/SQLite缓存
- 减少重复API调用
- 提高响应速度

### 2. 深度学习
- 使用BERT进行情绪分析
- 提高新闻/社交媒体情绪准确度

### 3. 实时数据
- 集成Websocket实时行情
- 实时新闻流
- 实时社交媒体监控

### 4. 可视化
- 创建Web Dashboard
- 实时数据可视化
- 交互式图表

### 5. 策略集成
- 将多维度数据融入现有策略
- 基于综合评分的自动交易
- 风险管理优化

---

## 📞 技术支持

如有问题,请查看:
- 各数据源官方文档
- 项目GitHub Issues
- 联系: qsswgl@gmail.com

---

## 📄 许可证

本项目仅供学习和研究使用,不构成投资建议。使用本系统产生的任何投资损失,开发者不承担责任。

**投资有风险,决策需谨慎!**
