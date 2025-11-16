import pandas as pd
import numpy as np
from pathlib import Path

# 读取数据
data_file = Path("data/sample_tsla.csv")
df = pd.read_csv(data_file)
df['date'] = pd.to_datetime(df['date'])

# 获取11月的数据
nov_data = df[df['date'] >= '2025-11-01'].copy()

print(f"11月数据行数: {len(nov_data)}")
print(f"日期范围: {nov_data['date'].min()} 至 {nov_data['date'].max()}")
print("\n11月每日数据:")
print(nov_data[['date', 'close', 'volume']].to_string())

# 计算每日的关键指标
print("\n\n分析11月数据是否满足买入条件:")
print("=" * 80)

for idx in nov_data.index:
    # 需要至少20天历史数据
    if idx < 20:
        continue
    
    date = df.loc[idx, 'date']
    close = df.loc[idx, 'close']
    volume = df.loc[idx, 'volume']
    
    # 计算5日动量
    if idx >= 5:
        prev_close = df.loc[idx-5, 'close']
        momentum = (close - prev_close) / prev_close
    else:
        momentum = 0
    
    # 计算20日均线
    if idx >= 20:
        ma20 = df.loc[idx-20:idx, 'close'].mean()
        is_uptrend = close > ma20
    else:
        ma20 = 0
        is_uptrend = False
    
    # 计算20日平均成交量
    if idx >= 20:
        avg_volume = df.loc[idx-20:idx, 'volume'].mean()
        volume_ratio = volume / avg_volume
        volume_surge = volume_ratio > 1.3
    else:
        avg_volume = 0
        volume_ratio = 0
        volume_surge = False
    
    # 判断是否满足买入条件
    buy_signal = is_uptrend and momentum > 0.03 and volume_surge
    
    print(f"\n日期: {date.strftime('%Y-%m-%d')}")
    print(f"  收盘价: ${close:.2f}")
    print(f"  5日动量: {momentum:.2%} (需要>3%: {'✓' if momentum > 0.03 else '✗'})")
    print(f"  20日均线: ${ma20:.2f}")
    print(f"  趋势: {'上升' if is_uptrend else '下降'} (需要在均线上方: {'✓' if is_uptrend else '✗'})")
    print(f"  成交量: {volume:,}")
    print(f"  20日均量: {avg_volume:,.0f}")
    print(f"  成交量比: {volume_ratio:.2f}x (需要>1.3x: {'✓' if volume_surge else '✗'})")
    print(f"  【买入信号: {'✓ 是' if buy_signal else '✗ 否'}】")
