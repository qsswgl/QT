# 特斯拉历史数据获取指南

## 当前状况
Yahoo Finance API 存在严格的频率限制(Rate Limiting),在短时间内无法下载 2010-至今的完整历史数据(约 3600+ 交易日)。

## 解决方案

### 方案 1:分批次手动下载(推荐)
在不同时间段分多次运行更新脚本,Yahoo Finance 通常会在几小时后重置限额:

```powershell
# 第一批:2010-2015
python -m src.pipeline.update_data TSLA --start 2010-06-29 --end 2015-12-31

# 等待 2-4 小时后,第二批:2016-2020
python -m src.pipeline.update_data TSLA --start 2016-01-01 --end 2020-12-31

# 再等待后,第三批:2021-至今
python -m src.pipeline.update_data TSLA --start 2021-01-01
```

### 方案 2:使用专业数据供应商
建议升级到专业数据源以获得稳定、高质量的历史数据:

| 供应商 | 特点 | 费用 |
|--------|------|------|
| **Polygon.io** | 免费层提供 2 年历史,付费层提供完整历史 | 免费/$99/月起 |
| **Alpha Vantage** | 免费 API 每天 500 次调用 | 免费/$50/月起 |
| **IBKR (Interactive Brokers)** | 账户持有者可免费获取历史数据 | 需开户 |
| **Quandl/Nasdaq Data Link** | 金融数据平台 | 按数据集计费 |
| **EOD Historical Data** | 专注历史数据 | $20/月起 |

### 方案 3:下载 CSV 文件
从第三方平台直接下载 TSLA 历史 CSV:

1. **Yahoo Finance 网页版**  
   访问 https://finance.yahoo.com/quote/TSLA/history  
   设置时间范围 → 点击 "Download" → 保存为 `data/sample_tsla.csv`

2. **Kaggle 数据集**  
   搜索 "Tesla Stock Price" 数据集,下载后替换本地文件。

3. **investing.com**  
   访问 https://www.investing.com/equities/tesla-motors-historical-data  
   下载历史数据 CSV。

### 方案 4:使用 yfinance 的缓存/Cookies(高级)
某些情况下设置浏览器 cookies 可以绕过部分限制:

```python
import yfinance as yf
ticker = yf.Ticker("TSLA")
# 设置 session cookies
hist = ticker.history(period="max")  # 尝试一次性拉取全部
hist.to_csv("data/sample_tsla.csv")
```

## 临时方案:使用近期数据
如果只是测试策略逻辑,可以先用近期数据(如最近 1-2 年):

```powershell
python -m src.pipeline.update_data TSLA --period 2y
```

## 推荐实施步骤(今天)
1. **立即可用**:先拉取最近 1 年数据用于开发测试  
   ```powershell
   python -m src.pipeline.update_data TSLA --period 1y
   ```

2. **明天/后天**:等待 API 限额重置后,分批补充 2010-2023 历史数据

3. **长期规划**:评估接入 Polygon 或 Alpha Vantage 等专业数据源

---

**注意**: 本项目的 `src/data/providers.py` 已内置重试逻辑和错误处理,在 API 恢复后会自动去重并合并历史数据。
