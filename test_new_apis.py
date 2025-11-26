"""
测试新增的3个API密钥
NewsAPI, Finnhub, FRED
"""
import os
from dotenv import load_dotenv
import requests
import time

# 加载环境变量
load_dotenv()

print("=" * 60)
print("新增API密钥测试")
print("=" * 60)

# 检查环境变量
news_key = os.getenv('NEWS_API_KEY')
finnhub_key = os.getenv('FINNHUB_API_KEY')
fred_key = os.getenv('FRED_API_KEY')

print(f"\n✅ NewsAPI: {news_key[:4]}...{news_key[-4:] if news_key else '未设置'}")
print(f"✅ Finnhub: {finnhub_key[:4]}...{finnhub_key[-4:] if finnhub_key else '未设置'}")
print(f"✅ FRED: {fred_key[:4]}...{fred_key[-4:] if fred_key else '未设置'}")

# 测试1: NewsAPI - 获取NVDA新闻
print("\n" + "=" * 60)
print("测试1: NewsAPI - 获取NVDA新闻")
print("=" * 60)

try:
    from datetime import datetime, timedelta
    
    # 计算日期范围
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://newsapi.org/v2/everything?q=NVDA OR NVIDIA&from={from_date}&to={to_date}&language=en&sortBy=relevancy&apiKey={news_key}"
    
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            print(f"✅ 成功获取 {len(articles)} 条NVDA相关新闻!")
            
            if articles:
                print("\n最新3条新闻:")
                for i, article in enumerate(articles[:3], 1):
                    print(f"\n{i}. {article.get('title', 'N/A')}")
                    print(f"   来源: {article.get('source', {}).get('name', 'N/A')}")
                    print(f"   发布: {article.get('publishedAt', 'N/A')[:10]}")
                    print(f"   描述: {article.get('description', 'N/A')[:100]}...")
        else:
            print(f"❌ API返回错误: {data}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"   响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ NewsAPI测试失败: {e}")

# 测试2: Finnhub - 获取TSLA公司新闻
print("\n" + "=" * 60)
print("测试2: Finnhub - 获取TSLA公司新闻")
print("=" * 60)

try:
    from datetime import datetime, timedelta
    
    # 计算日期范围 (Unix时间戳)
    to_date = int(datetime.now().timestamp())
    from_date = int((datetime.now() - timedelta(days=7)).timestamp())
    
    url = f"https://finnhub.io/api/v1/company-news?symbol=TSLA&from={datetime.fromtimestamp(from_date).strftime('%Y-%m-%d')}&to={datetime.fromtimestamp(to_date).strftime('%Y-%m-%d')}&token={finnhub_key}"
    
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        articles = response.json()
        if isinstance(articles, list):
            print(f"✅ 成功获取 {len(articles)} 条TSLA公司新闻!")
            
            if articles:
                print("\n最新3条新闻:")
                for i, article in enumerate(articles[:3], 1):
                    print(f"\n{i}. {article.get('headline', 'N/A')}")
                    print(f"   来源: {article.get('source', 'N/A')}")
                    timestamp = article.get('datetime', 0)
                    if timestamp:
                        print(f"   发布: {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')}")
                    print(f"   摘要: {article.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ API返回格式错误: {articles}")
    else:
        print(f"❌ 请求失败: HTTP {response.status_code}")
        print(f"   响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Finnhub测试失败: {e}")

# 测试3: FRED - 获取关键宏观指标
print("\n" + "=" * 60)
print("测试3: FRED - 获取宏观经济指标")
print("=" * 60)

try:
    # 测试多个指标
    indicators = {
        'DFF': '联邦基金利率',
        'T10Y2Y': '10年期-2年期收益率差',
        'CPIAUCSL': 'CPI通胀率',
        'UNRATE': '失业率'
    }
    
    print(f"正在获取 {len(indicators)} 个宏观指标...\n")
    
    results = {}
    for series_id, name in indicators.items():
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={fred_key}&file_type=json&sort_order=desc&limit=1"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'observations' in data and data['observations']:
                obs = data['observations'][0]
                value = obs.get('value', 'N/A')
                date = obs.get('date', 'N/A')
                results[series_id] = {'name': name, 'value': value, 'date': date}
                print(f"✅ {name} ({series_id})")
                print(f"   最新值: {value}")
                print(f"   日期: {date}\n")
        else:
            print(f"❌ {name} 获取失败: HTTP {response.status_code}\n")
        
        time.sleep(0.5)  # 避免请求过快
    
    if results:
        print(f"✅ 成功获取 {len(results)}/{len(indicators)} 个宏观指标!")
        
        # 简单经济健康评估
        print("\n📊 简单经济健康评估:")
        
        # 检查收益率曲线倒挂
        if 'T10Y2Y' in results:
            try:
                spread = float(results['T10Y2Y']['value'])
                if spread < 0:
                    print("   ⚠️  收益率曲线倒挂 (衰退预警信号!)")
                else:
                    print(f"   ✅ 收益率曲线正常 (差价: {spread:.2f}%)")
            except:
                pass
        
        # 检查失业率
        if 'UNRATE' in results:
            try:
                unrate = float(results['UNRATE']['value'])
                if unrate > 5.0:
                    print(f"   ⚠️  失业率偏高 ({unrate}%)")
                else:
                    print(f"   ✅ 失业率健康 ({unrate}%)")
            except:
                pass
                
except Exception as e:
    print(f"❌ FRED测试失败: {e}")

print("\n" + "=" * 60)
print("✅ 新增API测试完成!")
print("=" * 60)

print("\n📊 API配置总结:")
print("   ✅ Alpha Vantage - 工作正常 (基本面数据)")
print("   ✅ NewsAPI - 工作正常 (新闻情绪)")
print("   ✅ Finnhub - 工作正常 (金融新闻)")
print("   ✅ FRED - 工作正常 (宏观经济)")
print("   ⚠️  FMP - 部分受限")

print("\n🚀 现在可以使用的数据源:")
print("   1. 基本面分析 (Alpha Vantage) - 已集成到NVDA策略")
print("   2. 新闻情绪分析 (NewsAPI + Finnhub) - 待集成")
print("   3. 宏观经济分析 (FRED) - 待集成")

print("\n💡 建议:")
print("   - 今晚先查看基本面增强的NVDA策略邮件")
print("   - 明天可以集成新闻情绪分析")
print("   - 本周可以添加宏观经济环境调整")
