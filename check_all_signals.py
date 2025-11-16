import pandas as pd
from pathlib import Path

def check_signals(symbol, base_path):
    """检查指定股票的信号数据"""
    signals_file = base_path / "backtest_results" / "daily" / "signals_daily.csv"
    
    if not signals_file.exists():
        print(f"{symbol}: 信号文件不存在!")
        return
    
    df = pd.read_csv(signals_file)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"\n{'='*60}")
    print(f"📊 {symbol} 信号统计")
    print(f"{'='*60}")
    print(f"总信号数: {len(df)}")
    print(f"最早日期: {df['date'].min()}")
    print(f"最晚日期: {df['date'].max()}")
    
    # 统计BUY和SELL
    buy_count = len(df[df['action'].str.contains('BUY')])
    sell_count = len(df[df['action'].str.contains('SELL')])
    print(f"BUY信号: {buy_count}")
    print(f"SELL信号: {sell_count}")
    
    # 最近10条信号
    print(f"\n最近10条信号:")
    recent = df.tail(10)[['date', 'action', 'price', 'quantity', 'reason']]
    for idx, row in recent.iterrows():
        action = row['action'].replace('TradeAction.', '')
        print(f"  {row['date'].strftime('%Y-%m-%d')} | {action:4s} | ${row['price']:7.2f} | {row['quantity']:4.0f} | {row['reason']}")
    
    # 2025年11月的信号
    nov_2025 = df[(df['date'] >= '2025-11-01') & (df['date'] <= '2025-11-30')]
    print(f"\n2025年11月信号数: {len(nov_2025)}")
    if len(nov_2025) > 0:
        for idx, row in nov_2025.iterrows():
            action = row['action'].replace('TradeAction.', '')
            print(f"  {row['date'].strftime('%Y-%m-%d')} | {action:4s} | ${row['price']:7.2f} | {row['quantity']:4.0f} | {row['reason']}")
    else:
        print("  (无11月信号)")

# 检查三支股票
print("检查所有股票的日度策略信号")
print("="*60)

# TSLA
check_signals("TSLA", Path("K:/QT"))

# NVDA
check_signals("NVDA", Path("K:/QT/NVDA"))

# INTC
check_signals("INTC", Path("K:/QT/INTC"))

print(f"\n{'='*60}")
print("✅ 检查完成!")
print("="*60)
