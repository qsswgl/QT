"""
快速更新历史数据 - 使用Alpha Vantage API
2025-11-25
"""
import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

# 加载环境变量
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
if not API_KEY:
    print("❌ 未找到ALPHA_VANTAGE_API_KEY环境变量")
    exit(1)

print("=" * 80)
print("📊 快速更新历史数据 (Alpha Vantage)")
print("=" * 80)
print()

# 要更新的股票
symbols = ['NVDA', 'TSLA', 'INTC']
data_dir = Path('data/daily')
data_dir.mkdir(parents=True, exist_ok=True)

for idx, symbol in enumerate(symbols):
    print(f"[{symbol}] 开始更新...")
    
    try:
        # 调用Alpha Vantage API
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact',  # 最近100天数据(免费版)
            'apikey': API_KEY
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
            continue
        
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            if 'Note' in data:
                print(f"  ⚠️ API限流: {data['Note']}")
            elif 'Error Message' in data:
                print(f"  ❌ API错误: {data['Error Message']}")
            else:
                print(f"  ❌ 未获取到数据: {data}")
            continue
        
        # 解析数据
        time_series = data['Time Series (Daily)']
        rows = []
        
        for date_str, values in time_series.items():
            rows.append({
                'date': date_str,
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'volume': int(values['5. volume'])
            })
        
        # 创建DataFrame
        df = pd.DataFrame(rows)
        df = df.sort_values('date').reset_index(drop=True)
        
        # 创建DataFrame
        df = pd.DataFrame(rows)
        df = df.sort_values('date').reset_index(drop=True)
        
        if df.empty:
            print(f"  ❌ 未获取到数据")
            continue
        
        # 保存到CSV
        output_file = data_dir / f'{symbol.lower()}_daily.csv'
        df.to_csv(output_file, index=False)
        
        # 显示信息
        min_date = df['date'].min()
        max_date = df['date'].max()
        total_rows = len(df)
        
        print(f"  ✅ 成功更新 {total_rows} 条记录")
        print(f"  📅 日期范围: {min_date} → {max_date}")
        print(f"  💾 保存至: {output_file}")
        
        # 显示最新数据
        latest = df.iloc[-1]
        print(f"  📈 最新价格: ${latest['close']:.2f} (日期: {latest['date']})")
        print()
        
        # Alpha Vantage限流: 5次/分钟
        if idx < len(symbols) - 1:
            print(f"  ⏱️  等待15秒(API限流)...")
            time.sleep(15)
            print()
        
    except Exception as e:
        print(f"  ❌ 更新失败: {e}")
        print()

print("=" * 80)
print("✅ 数据更新完成!")
print("=" * 80)
print()
print("下一步:")
print("1. 检查data/daily/目录下的CSV文件")
print("2. 验证最新日期是否为2025-11-25或2025-11-22(最近交易日)")
print("3. 运行日度策略生成最新信号")

