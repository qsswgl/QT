# 多数据源配置指南

## 📊 概述

系统现在支持多个免费数据源，自动尝试备用源，提高数据获取的可靠性。

### 支持的数据源

| 数据源 | 优先级 | 需要API Key | 免费限额 | 速度 |
|--------|--------|-------------|----------|------|
| **Yahoo Finance** | 1 (最高) | ❌ 不需要 | 有频率限制 | ⚡ 快 |
| **Alpha Vantage** | 2 | ✅ 需要 | 500次/天 | 🐢 中等 |
| **Twelve Data** | 3 | ✅ 需要 | 800次/天 | 🚀 快 |

## 🚀 快速开始

### 1. 无需配置（仅使用Yahoo Finance）

如果你不想配置API密钥，系统会默认使用Yahoo Finance：

```powershell
# 直接使用（仅Yahoo Finance）
python -m src.pipeline.update_data_multi_source TSLA
```

### 2. 配置备用数据源（推荐）

为了提高可靠性，建议配置至少一个备用数据源。

## 🔑 获取免费API密钥

### Alpha Vantage

1. **访问**: https://www.alphavantage.co/support/#api-key
2. **填写信息**: 输入邮箱和简单信息
3. **获取密钥**: 立即获得免费API密钥
4. **限制**: 
   - 每天500次请求
   - 每分钟5次请求
   - 20年完整历史数据

**示例密钥格式**: `ABCD1234EFGH5678`

### Twelve Data

1. **访问**: https://twelvedata.com/pricing
2. **注册免费账户**: 选择"Free Plan"
3. **获取API Key**: 在控制台生成
4. **限制**:
   - 每天800次请求
   - 每分钟8次请求
   - 最多5000条历史数据

**示例密钥格式**: `1234567890abcdef1234567890abcdef`

## ⚙️ 配置方法

### 方法 1: 环境变量（推荐）

在PowerShell中设置环境变量：

```powershell
# 临时设置（当前会话有效）
$env:ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key"
$env:TWELVE_DATA_API_KEY = "your_twelve_data_key"

# 验证设置
echo $env:ALPHA_VANTAGE_API_KEY
```

永久设置（Windows系统环境变量）：

```powershell
# 以管理员身份运行PowerShell
[Environment]::SetEnvironmentVariable("ALPHA_VANTAGE_API_KEY", "your_key", "User")
[Environment]::SetEnvironmentVariable("TWELVE_DATA_API_KEY", "your_key", "User")
```

或通过Windows界面：
1. 右键"此电脑" → "属性"
2. "高级系统设置" → "环境变量"
3. 在"用户变量"中新建：
   - 变量名: `ALPHA_VANTAGE_API_KEY`
   - 变量值: 你的API密钥

### 方法 2: 在代码中直接使用

修改 `src/pipeline/update_data_multi_source.py`：

```python
from src.data.multi_providers import MultiSourceDataClient

client = MultiSourceDataClient(
    alpha_vantage_key="your_alpha_vantage_key",
    twelve_data_key="your_twelve_data_key"
)
```

## 📝 使用示例

### 基本使用

```powershell
# 更新TSLA数据（使用所有配置的数据源）
python -m src.pipeline.update_data_multi_source TSLA

# 更新最近60天数据
python -m src.pipeline.update_data_multi_source TSLA --days 60

# 指定输出路径
python -m src.pipeline.update_data_multi_source TSLA --output K:\QT\data\tsla.csv
```

### 在批处理文件中使用

修改 `daily_strategy_check.bat`：

```batch
@echo off
echo [步骤 1/3] 更新数据 (多数据源)...
python -m src.pipeline.update_data_multi_source TSLA --days 30
if errorlevel 1 (
    echo ⚠️ 数据更新失败，继续使用现有数据...
)
```

### 在Python代码中使用

```python
from src.data.multi_providers import create_multi_source_client
import datetime as dt

# 创建客户端（自动读取环境变量中的API密钥）
client = create_multi_source_client()

# 获取数据
data = client.fetch_daily_history(
    symbol="TSLA",
    start=dt.date(2024, 1, 1),
    end=dt.date(2024, 12, 31)
)

print(f"获取到 {len(data)} 条数据")
```

## 🔄 数据源切换逻辑

系统会按以下顺序尝试数据源：

1. **Yahoo Finance** (优先级1)
   - 免费，快速，无需注册
   - 如果成功，直接返回
   - 如果失败（频率限制），尝试下一个

2. **Alpha Vantage** (优先级2)
   - 需要API密钥
   - 如果配置且成功，返回数据
   - 如果失败，尝试下一个

3. **Twelve Data** (优先级3)
   - 需要API密钥
   - 作为最后的备用方案

**每个数据源最多重试2次**，失败后自动切换到下一个。

## 📊 工作流程示例

```
开始获取TSLA数据
    ↓
尝试 Yahoo Finance
    ├─ 成功 → 返回数据 ✅
    └─ 失败 (Too Many Requests)
        ↓
    尝试 Alpha Vantage
        ├─ 成功 → 返回数据 ✅
        └─ 失败 (Rate Limit)
            ↓
        尝试 Twelve Data
            ├─ 成功 → 返回数据 ✅
            └─ 失败 → 报错 ❌
```

## ⚡ 性能对比

### 获取3个月数据 (TSLA)

| 数据源 | 响应时间 | 数据完整性 | 稳定性 |
|--------|----------|-----------|--------|
| Yahoo Finance | ~1-2秒 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (有限制) |
| Alpha Vantage | ~2-3秒 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Twelve Data | ~1-2秒 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🐛 故障排除

### 问题 1: "No API key provided"

**原因**: 未配置API密钥，但Yahoo Finance失败了。

**解决**:
```powershell
# 配置至少一个备用数据源
$env:ALPHA_VANTAGE_API_KEY = "your_key"
```

### 问题 2: "Failed to fetch data from all available sources"

**原因**: 所有数据源都失败了。

**解决**:
1. 检查网络连接
2. 等待15-30分钟（可能遇到频率限制）
3. 验证API密钥是否正确
4. 尝试使用缓存的数据

### 问题 3: "Rate limit exceeded"

**原因**: 超过了某个数据源的频率限制。

**解决**:
1. 等待一段时间（Alpha Vantage: 1分钟，Twelve Data: 1分钟）
2. 系统会自动切换到备用数据源
3. 考虑配置多个数据源分散请求

## 📈 最佳实践

### 1. 配置多个数据源

```powershell
# 配置所有可用的数据源
$env:ALPHA_VANTAGE_API_KEY = "your_alpha_key"
$env:TWELVE_DATA_API_KEY = "your_twelve_key"
```

### 2. 使用增量更新

```powershell
# 只更新缺失的数据，减少API调用
python -m src.pipeline.update_data_multi_source TSLA --days 7
```

### 3. 在批处理中优雅处理失败

```batch
python -m src.pipeline.update_data_multi_source TSLA
if errorlevel 1 (
    echo ⚠️ 数据更新失败，使用现有数据
) else (
    echo ✅ 数据更新成功
)
```

### 4. 监控API使用量

Alpha Vantage和Twelve Data都有每日限额，建议：
- 每天只运行一次完整更新
- 使用增量更新减少请求次数
- 缓存数据，避免重复请求

## 🔐 安全建议

1. **不要在代码中硬编码API密钥**
2. **使用环境变量存储密钥**
3. **不要将.env文件提交到Git**
4. **定期更换API密钥**
5. **监控API使用情况**

## 📚 相关文档

- [Yahoo Finance API](https://github.com/ranaroussi/yfinance)
- [Alpha Vantage文档](https://www.alphavantage.co/documentation/)
- [Twelve Data文档](https://twelvedata.com/docs)

## 🆘 获取帮助

如果遇到问题：
1. 查看日志输出
2. 检查API密钥配置
3. 验证网络连接
4. 查看数据源官方文档

---

**最后更新**: 2025-11-13
