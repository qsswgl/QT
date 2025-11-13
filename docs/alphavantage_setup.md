# Alpha Vantage 数据接入指南

## 简介
Alpha Vantage 提供免费的股票市场数据 API,非常适合量化交易系统使用。

### 优势
✅ **完全免费** - 每天 500 次 API 调用  
✅ **完整历史** - 提供 20+ 年的日线历史数据  
✅ **稳定可靠** - 官方支持,无突然限流  
✅ **无需信用卡** - 注册即可使用  

### 限制
⚠️ 免费版每分钟最多 5 次调用(我们已内置自动限速)  
⚠️ 每天最多 500 次调用(对日线数据完全够用)  

---

## 快速开始

### 步骤 1: 获取免费 API Key

1. 访问 Alpha Vantage 官网:  
   **https://www.alphavantage.co/support/#api-key**

2. 填写表单(仅需邮箱):
   - Email Address: 你的邮箱
   - Organization (optional): 可不填
   - 点击 "GET FREE API KEY"

3. API Key 会立即显示在页面上,并发送到你的邮箱,格式类似:
   ```
   YOUR_API_KEY_EXAMPLE_1234567890
   ```

### 步骤 2: 配置环境变量

在 PowerShell 中设置环境变量(推荐):

```powershell
# 临时设置(当前会话有效)
$env:ALPHAVANTAGE_API_KEY = "YOUR_API_KEY_HERE"

# 永久设置(所有会话有效)
[System.Environment]::SetEnvironmentVariable('ALPHAVANTAGE_API_KEY', 'YOUR_API_KEY_HERE', 'User')
```

或者创建 `.env` 文件:

```bash
# 在项目根目录创建 .env 文件
ALPHAVANTAGE_API_KEY=YOUR_API_KEY_HERE
```

### 步骤 3: 安装依赖

```powershell
pip install -r requirements.txt
```

### 步骤 4: 获取 TSLA 完整历史数据

```powershell
# 使用环境变量中的 API Key
python -m src.pipeline.fetch_alphavantage TSLA

# 或直接传递 API Key
python -m src.pipeline.fetch_alphavantage TSLA --api-key YOUR_API_KEY

# 仅获取最近 100 天
python -m src.pipeline.fetch_alphavantage TSLA --outputsize compact
```

**预期输出**:
```
2025-11-10 19:30:00,000 INFO __main__ - Fetching TSLA data (outputsize=full) to data\sample_tsla.csv
2025-11-10 19:30:02,500 INFO src.data.alphavantage - Fetching TSLA data from Alpha Vantage (attempt 1/3)
2025-11-10 19:30:05,200 INFO src.data.alphavantage - Parsed 3650 records from 2010-06-29 to 2025-11-08
2025-11-10 19:30:05,300 INFO __main__ - ✓ Success! Saved 3650 rows
2025-11-10 19:30:05,301 INFO __main__ -   Date range: 2010-06-29 → 2025-11-08
2025-11-10 19:30:05,302 INFO __main__ -   Output: data\sample_tsla.csv
```

---

## 使用示例

### Python 脚本中使用

```python
from src.data.alphavantage import AlphaVantageClient, AlphaVantageConfig

# 方式 1: 使用环境变量
client = AlphaVantageClient()

# 方式 2: 显式传递 API Key
config = AlphaVantageConfig(api_key="YOUR_API_KEY")
client = AlphaVantageClient(config)

# 获取完整历史数据
df = client.fetch_daily_history("TSLA", outputsize="full")
print(f"获取 {len(df)} 条记录")
print(df.head())
```

### 获取多个股票

```python
from pathlib import Path
from src.data.alphavantage import AlphaVantageClient, AlphaVantageIngestor

client = AlphaVantageClient()

symbols = ["TSLA", "AAPL", "MSFT"]
for symbol in symbols:
    output_path = Path(f"data/{symbol.lower()}_history.csv")
    ingestor = AlphaVantageIngestor(client=client, output_path=output_path)
    result = ingestor.run(symbol, outputsize="full")
    print(f"{symbol}: {result['rows_written']} rows, {result['min_date']} to {result['max_date']}")
```

---

## 数据格式

返回的 CSV 文件格式:

```csv
date,open,high,low,close,volume
2010-06-29,19.00,25.00,17.54,23.89,18766300
2010-06-30,25.79,30.42,23.30,23.83,17187100
...
2025-11-08,345.20,352.80,343.10,350.45,25431200
```

---

## 常见问题

### Q: 如何查看剩余调用次数?
A: Alpha Vantage 免费版不提供配额查询,建议自己记录调用次数。我们的实现已内置速率限制(每 12 秒一次调用)。

### Q: 超过每天 500 次限制怎么办?
A: 对于日线数据,通常不会超限。如果需要更多调用:
- 付费升级($49.99/月,75 次/分钟)
- 或使用多个免费 API Key 轮换

### Q: 数据有延迟吗?
A: 免费版通常延迟 15-20 分钟,适合日线级别策略。

### Q: 支持实时数据吗?
A: 免费版不支持真正的实时流数据,但可以频繁调用获取近实时报价。

### Q: 能获取期权/期货数据吗?
A: Alpha Vantage 主要提供股票和外汇数据,期权数据需要付费版。

---

## 与 Yahoo Finance 对比

| 特性 | Alpha Vantage | Yahoo Finance |
|------|---------------|---------------|
| 免费额度 | 500 次/天 | 无限制(但限流) |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 历史数据 | 20+ 年 | 完整历史 |
| 注册要求 | 需要邮箱 | 不需要 |
| 官方支持 | 有 | 无 |
| 商业使用 | 允许 | 灰色地带 |
| 推荐度 | **生产环境推荐** | 开发测试可用 |

---

## 下一步

1. ✅ 获取 API Key 并配置环境变量
2. ✅ 运行 `python -m src.pipeline.fetch_alphavantage TSLA` 获取数据
3. ✅ 运行策略: `python -m src.pipeline.run_once`
4. 🔜 根据需要添加更多股票或因子数据

---

## 故障排查

### 错误: "API key required"
确保已设置环境变量:
```powershell
echo $env:ALPHAVANTAGE_API_KEY
```

### 错误: "Rate limit exceeded"
等待 1 分钟后重试,或检查是否超过每天 500 次限制。

### 错误: "Invalid API key"
检查 API Key 是否正确复制,没有多余空格。

### 超时错误
检查网络连接,Alpha Vantage 服务器在美国,国内访问可能较慢。

---

## 相关资源

- [Alpha Vantage 官方文档](https://www.alphavantage.co/documentation/)
- [API 参数说明](https://www.alphavantage.co/documentation/#daily)
- [支持论坛](https://www.alphavantage.co/support/)

需要帮助? 查看项目的 [数据获取策略文档](data_acquisition.md)。
