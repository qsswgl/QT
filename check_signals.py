import pandas as pd
from pathlib import Path

# 读取信号数据
signals_file = Path("backtest_results/daily/signals_daily.csv")
df = pd.read_csv(signals_file)
df['date'] = pd.to_datetime(df['date'])

print(f"总信号数: {len(df)}")
print(f"\n最早日期: {df['date'].min()}")
print(f"最晚日期: {df['date'].max()}")

print(f"\n最近20条信号:")
recent = df.tail(20)[['date', 'action', 'price', 'quantity', 'reason']]
for idx, row in recent.iterrows():
    print(f"{row['date'].strftime('%Y-%m-%d')} | {row['action']:4s} | ${row['price']:7.2f} | {row['quantity']:3.0f} | {row['reason']}")

print(f"\n2025年11月的信号:")
nov_2025 = df[(df['date'] >= '2025-11-01') & (df['date'] <= '2025-11-30')]
print(f"数量: {len(nov_2025)}")
if len(nov_2025) > 0:
    for idx, row in nov_2025.iterrows():
        print(f"{row['date'].strftime('%Y-%m-%d')} | {row['action']:4s} | ${row['price']:7.2f} | {row['quantity']:3.0f} | {row['reason']}")
else:
    print("没有找到2025年11月的信号数据")
