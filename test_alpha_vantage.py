"""测试Alpha Vantage基本面数据"""
import sys
import os
from pathlib import Path

# 加载环境变量
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# 测试基本面数据
from src.utils.fundamentals_manager import FundamentalsManager

mgr = FundamentalsManager()
overview = mgr.get_company_overview('NVDA')

print("✅ NVDA基本面数据:")
print(f"  公司: {overview.get('Name')}")
print(f"  PE: {overview.get('PERatio')}")
print(f"  ROE: {float(overview.get('ReturnOnEquityTTM', 0))*100:.2f}%")
print(f"  市值: ${float(overview.get('MarketCapitalization', 0))/1e9:.2f}B")

health = mgr.calculate_financial_health('NVDA')
print(f"  评分: {health['score']}/100 ({health['grade']})")
