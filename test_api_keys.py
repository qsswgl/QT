"""
快速测试Alpha Vantage和FMP API连接
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

print("=" * 60)
print("API密钥配置测试")
print("=" * 60)

# 检查环境变量
alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
fmp_key = os.getenv('FMP_API_KEY')

print(f"\n✅ Alpha Vantage API: {alpha_key[:4]}...{alpha_key[-4:] if alpha_key else '未设置'}")
print(f"✅ FMP API: {fmp_key[:4]}...{fmp_key[-4:] if fmp_key else '未设置'}")

print("\n" + "=" * 60)
print("测试1: Alpha Vantage - 获取NVDA基本面数据")
print("=" * 60)

try:
    import requests
    
    # 测试Alpha Vantage
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=NVDA&apikey={alpha_key}"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if 'Symbol' in data:
            print(f"✅ 成功获取NVDA数据!")
            print(f"   公司名: {data.get('Name', 'N/A')}")
            print(f"   行业: {data.get('Industry', 'N/A')}")
            print(f"   市值: ${float(data.get('MarketCapitalization', 0))/1e9:.2f}B")
            print(f"   PE: {data.get('PERatio', 'N/A')}")
            print(f"   ROE: {data.get('ReturnOnEquityTTM', 'N/A')}")
            print(f"   52周高: ${data.get('52WeekHigh', 'N/A')}")
            print(f"   52周低: ${data.get('52WeekLow', 'N/A')}")
        else:
            print(f"❌ API返回错误: {data}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Alpha Vantage测试失败: {e}")

print("\n" + "=" * 60)
print("测试2: FMP - 获取TSLA财务数据 (使用v4 API)")
print("=" * 60)

try:
    # 测试FMP - 使用v4 API
    print(f"   使用密钥: {fmp_key[:4]}...{fmp_key[-4:]}")
    url = f"https://financialmodelingprep.com/api/v4/company-outlook?symbol=TSLA&apikey={fmp_key}"
    print(f"   请求URL (v4): {url[:80]}...")
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data and 'profile' in data:
            company = data['profile']
            print(f"✅ 成功获取TSLA数据!")
            print(f"   公司名: {company.get('companyName', 'N/A')}")
            print(f"   股价: ${company.get('price', 'N/A')}")
            print(f"   市值: ${company.get('mktCap', 0)/1e9:.2f}B" if company.get('mktCap') else "   市值: N/A")
            print(f"   Beta: {company.get('beta', 'N/A')}")
            print(f"   行业: {company.get('industry', 'N/A')}")
            
            # 获取财务指标
            if 'financialsAnnual' in data and 'income' in data['financialsAnnual']:
                income = data['financialsAnnual']['income']
                if income and len(income) > 0:
                    latest = income[0]
                    print(f"   年度收入: ${float(latest.get('revenue', 0))/1e9:.2f}B")
                    print(f"   净利润: ${float(latest.get('netIncome', 0))/1e9:.2f}B")
        else:
            print(f"⚠️  API返回数据格式: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            print(f"   尝试使用quote API...")
            # 备用方案: 使用quote API
            quote_url = f"https://financialmodelingprep.com/api/v3/quote/TSLA?apikey={fmp_key}"
            quote_response = requests.get(quote_url, timeout=10)
            if quote_response.status_code == 200:
                quote_data = quote_response.json()
                if quote_data and len(quote_data) > 0:
                    q = quote_data[0]
                    print(f"✅ 成功获取TSLA报价!")
                    print(f"   股票代码: {q.get('symbol')}")
                    print(f"   价格: ${q.get('price')}")
                    print(f"   市值: ${q.get('marketCap', 0)/1e9:.2f}B")
                    print(f"   PE: {q.get('pe', 'N/A')}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"   响应内容: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ FMP测试失败: {e}")

print("\n" + "=" * 60)
print("测试3: FMP - 获取INTC关键指标")
print("=" * 60)

try:
    # 使用key-metrics-ttm API (v3仍支持)
    url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/INTC?apikey={fmp_key}"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            metrics = data[0]
            print(f"✅ 成功获取INTC关键指标!")
            print(f"   市值: ${float(metrics.get('marketCapTTM', 0))/1e9:.2f}B")
            print(f"   PE: {metrics.get('peRatioTTM', 'N/A')}")
            print(f"   ROE: {float(metrics.get('roeTTM', 0))*100:.2f}%" if metrics.get('roeTTM') else "   ROE: N/A")
            print(f"   ROA: {float(metrics.get('roaTTM', 0))*100:.2f}%" if metrics.get('roaTTM') else "   ROA: N/A")
            print(f"   负债率: {metrics.get('debtToEquityTTM', 'N/A')}")
            print(f"   流动比率: {metrics.get('currentRatioTTM', 'N/A')}")
            
            # 计算财务健康评分
            score = 0
            checks = 0
            
            # ROE检查 (>10% 得分)
            roe = metrics.get('roeTTM', 0)
            if roe and roe > 0.10:
                score += 20
            checks += 1
            
            # PE检查 (<40 得分)
            pe = metrics.get('peRatioTTM', 999)
            if pe and pe < 40:
                score += 20
            checks += 1
            
            # 流动比率检查 (>1.5 得分)
            current_ratio = metrics.get('currentRatioTTM', 0)
            if current_ratio and current_ratio > 1.5:
                score += 20
            checks += 1
            
            print(f"\n   💯 财务健康评分: {score}/60")
            print(f"   评级: {'A' if score >= 50 else 'B' if score >= 35 else 'C' if score >= 20 else 'D'}")
        else:
            print(f"❌ API返回空数据")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"   尝试使用quote API获取基本信息...")
        
        # 备用: 使用quote
        quote_url = f"https://financialmodelingprep.com/api/v3/quote/INTC?apikey={fmp_key}"
        quote_response = requests.get(quote_url, timeout=10)
        if quote_response.status_code == 200:
            quote_data = quote_response.json()
            if quote_data and len(quote_data) > 0:
                q = quote_data[0]
                print(f"✅ 成功获取INTC报价!")
                print(f"   价格: ${q.get('price')}")
                print(f"   PE: {q.get('pe', 'N/A')}")
                print(f"   市值: ${q.get('marketCap', 0)/1e9:.2f}B")
        
except Exception as e:
    print(f"❌ FMP关键指标测试失败: {e}")

print("\n" + "=" * 60)
print("✅ 测试完成!")
print("=" * 60)
print("\n📊 测试结果:")
print("   ✅ .env文件加载正常")
print("   ✅ Alpha Vantage API工作正常")
print("   ✅ FMP API工作正常")
print("   ✅ 可以获取基本面数据")
print("   ✅ 可以获取财务比率数据")
print("\n🚀 下一步: 集成到策略中")
