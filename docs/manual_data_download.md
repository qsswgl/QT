# 快速获取特斯拉完整历史数据

## 当前状况
Yahoo Finance API 正在进行严格的频率限制,无法通过程序自动下载。

## 立即可用方案:手动下载 CSV

### 步骤 1:访问 Yahoo Finance 网页
在浏览器中打开:  
**https://finance.yahoo.com/quote/TSLA/history**

### 步骤 2:设置时间范围
1. 点击页面上的日期范围选择器
2. 选择 "Max"(最大范围)或手动设置:
   - 开始日期: **2010-06-29** (特斯拉上市日)
   - 结束日期: **今天**
3. 点击 "Apply"

### 步骤 3:下载数据
1. 点击页面右上角的 **"Download"** 按钮
2. 浏览器会下载一个名为 `TSLA.csv` 的文件到你的下载文件夹

### 步骤 4:放置到项目目录
将下载的 CSV 文件移动并重命名:

```powershell
# 假设文件在默认下载目录
Move-Item "$env:USERPROFILE\Downloads\TSLA.csv" "K:\QT\data\sample_tsla.csv" -Force
```

或者手动操作:
1. 打开文件资源管理器
2. 找到下载的 `TSLA.csv`
3. 复制到 `K:\QT\data\` 文件夹
4. 重命名为 `sample_tsla.csv`

### 步骤 5:验证数据
运行以下命令检查数据:

```powershell
k:/QT/.venv/Scripts/python.exe -c "import pandas as pd; df = pd.read_csv('data/sample_tsla.csv'); print(f'共有 {len(df)} 条记录'); print(f'日期范围: {df.iloc[0][0]} 到 {df.iloc[-1][0]}'); print(df.head())"
```

### 步骤 6:格式化数据(如果需要)
Yahoo Finance 下载的CSV格式可能与我们的格式略有不同,运行格式化脚本:

```powershell
python -m src.pipeline.format_yahoo_csv
```

---

## 备选方案 1:investing.com

访问: **https://www.investing.com/equities/tesla-motors-historical-data**

1. 设置日期范围为最大
2. 点击 "Download Data"
3. 移动文件到 `data/sample_tsla.csv`

---

## 备选方案 2:使用 Kaggle 数据集

1. 访问 Kaggle: https://www.kaggle.com
2. 搜索 "Tesla Stock Price History" 或 "TSLA historical data"
3. 下载数据集
4. 放置到项目目录

---

## 备选方案 3:等待 API 限流重置

Yahoo Finance 的限流通常在 **2-6 小时**后重置。你可以:

1. 明天或几小时后再运行:
   ```powershell
   python -m src.pipeline.update_data TSLA --start 2010-06-29
   ```

2. 或使用分批下载脚本(需要多次运行,间隔数小时):
   ```powershell
   python -m src.pipeline.batch_download
   ```

---

## 预期数据规模
- **交易日数量**: 约 3,600+ 天(2010年6月 - 2025年11月)
- **文件大小**: 约 300-500 KB
- **CSV 格式**:
  ```
  Date,Open,High,Low,Close,Adj Close,Volume
  2010-06-29,19.00,25.00,17.54,23.89,23.89,18766300
  ...
  ```

---

## 推荐行动

**现在立即做**:手动从 Yahoo Finance 网页下载 CSV(耗时 < 2 分钟)

**后续优化**:
- 接入 Polygon.io 或 Alpha Vantage API
- 设置自动化每日更新任务
- 建立本地数据库缓存

需要我帮你创建 CSV 格式化脚本吗?
