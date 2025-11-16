import pandas as pd
from pathlib import Path

# 读取数据文件
data_file = Path("data/sample_tsla.csv")
df = pd.read_csv(data_file)

print(f"数据行数: {len(df)}")
print(f"列名: {df.columns.tolist()}")

# 假设第一列是日期
date_col = df.columns[0]
df['parsed_date'] = pd.to_datetime(df[date_col])

print(f"\n最早日期: {df['parsed_date'].min()}")
print(f"最晚日期: {df['parsed_date'].max()}")

print(f"\n最近10行:")
print(df.tail(10))
