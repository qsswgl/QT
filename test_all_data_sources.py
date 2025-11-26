"""
数据源全面测试脚本
测试所有已配置的API密钥和数据源
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ 已从 .env 文件加载配置\n")
except ImportError:
    print("⚠️  未安装 python-dotenv,尝试从系统环境变量读取\n")

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_alpha_vantage():
    """测试 Alpha Vantage"""
    print_section("测试 Alpha Vantage API")
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == 'YOUR_KEY_HERE':
        print("❌ Alpha Vantage API密钥未配置")
        return False
    
    try:
        from src.data.alphavantage import AlphaVantageClient
        
        client = AlphaVantageClient()
        print(f"✓ Alpha Vantage客户端初始化成功")
        print(f"  API密钥: {api_key[:4]}...{api_key[-4:]}")
        
        # 测试获取数据
        print("\n测试获取TSLA历史数据...")
        data = client.fetch_daily('TSLA', lookback_days=5)
        
        if data is not None and not data.empty:
            print(f"✓ 成功获取 {len(data)} 条记录")
            print(f"  最新日期: {data['date'].iloc[-1]}")
            print(f"  最新收盘价: ${data['close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ 未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ Alpha Vantage测试失败: {e}")
        return False

def test_fmp():
    """测试 Financial Modeling Prep"""
    print_section("测试 Financial Modeling Prep API")
    
    api_key = os.environ.get('FMP_API_KEY')
    if not api_key or api_key == 'YOUR_KEY_HERE':
        print("❌ FMP API密钥未配置")
        return False
    
    try:
        from src.data.fundamentals import FundamentalsDataManager
        
        manager = FundamentalsDataManager()
        print(f"✓ FMP数据管理器初始化成功")
        print(f"  API密钥: {api_key[:4]}...{api_key[-4:]}")
        
        # 测试获取公司概况
        print("\n测试获取NVDA公司概况...")
        overview = manager.get_company_overview('NVDA')
        
        if overview:
            print(f"✓ 成功获取公司信息")
            print(f"  公司名称: {overview.get('company_name', 'N/A')}")
            print(f"  市值: ${overview.get('market_cap', 0)/1e9:.2f}B")
            print(f"  PE比率: {overview.get('pe_ratio', 'N/A')}")
            
            # 测试财务健康评分
            print("\n测试财务健康评分...")
            health = manager.get_financial_health('NVDA')
            if health:
                print(f"✓ 财务健康评分: {health.get('score', 'N/A')}/100")
                print(f"  评级: {health.get('grade', 'N/A')}")
            
            return True
        else:
            print("❌ 未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ FMP测试失败: {e}")
        return False

def test_newsapi():
    """测试 NewsAPI"""
    print_section("测试 NewsAPI")
    
    api_key = os.environ.get('NEWS_API_KEY')
    if not api_key or api_key == 'YOUR_KEY_HERE':
        print("❌ NewsAPI密钥未配置")
        return False
    
    try:
        from src.data.news_sentiment import NewsDataManager
        
        manager = NewsDataManager()
        print(f"✓ NewsAPI数据管理器初始化成功")
        print(f"  API密钥: {api_key[:4]}...{api_key[-4:]}")
        
        # 测试获取新闻
        print("\n测试获取TSLA最近1天新闻...")
        news = manager.get_news_with_sentiment('TSLA', days_back=1)
        
        if news and len(news) > 0:
            print(f"✓ 成功获取 {len(news)} 条新闻")
            
            # 显示第一条新闻
            first_news = news[0]
            print(f"\n示例新闻:")
            print(f"  标题: {first_news.get('title', 'N/A')[:60]}...")
            print(f"  情绪: {first_news.get('sentiment', 'N/A')}")
            print(f"  得分: {first_news.get('sentiment_score', 'N/A')}")
            
            # 整体情绪
            summary = manager.get_overall_sentiment('TSLA', days_back=1)
            if summary:
                print(f"\n整体情绪:")
                print(f"  情绪倾向: {summary.get('overall_sentiment', 'N/A')}")
                print(f"  情绪得分: {summary.get('sentiment_score', 'N/A')}")
            
            return True
        else:
            print("⚠️  未获取到新闻(可能是周末或节假日)")
            return True  # 不算失败
            
    except Exception as e:
        print(f"❌ NewsAPI测试失败: {e}")
        return False

def test_finnhub():
    """测试 Finnhub"""
    print_section("测试 Finnhub API")
    
    api_key = os.environ.get('FINNHUB_API_KEY')
    if not api_key or api_key == 'YOUR_KEY_HERE':
        print("❌ Finnhub API密钥未配置")
        return False
    
    try:
        from src.data.news_sentiment import FinnhubNewsProvider
        
        provider = FinnhubNewsProvider()
        print(f"✓ Finnhub数据提供器初始化成功")
        print(f"  API密钥: {api_key[:4]}...{api_key[-4:]}")
        
        # 测试获取公司新闻
        print("\n测试获取NVDA公司新闻...")
        news = provider.get_company_news('NVDA')
        
        if news and len(news) > 0:
            print(f"✓ 成功获取 {len(news)} 条新闻")
            
            # 显示第一条新闻
            first_news = news[0]
            print(f"\n示例新闻:")
            print(f"  标题: {first_news.get('headline', 'N/A')[:60]}...")
            print(f"  来源: {first_news.get('source', 'N/A')}")
            print(f"  日期: {first_news.get('datetime', 'N/A')}")
            
            return True
        else:
            print("⚠️  未获取到新闻")
            return True
            
    except Exception as e:
        print(f"❌ Finnhub测试失败: {e}")
        return False

def test_fred():
    """测试 FRED"""
    print_section("测试 FRED API")
    
    api_key = os.environ.get('FRED_API_KEY')
    if not api_key or api_key == 'YOUR_KEY_HERE':
        print("❌ FRED API密钥未配置")
        return False
    
    try:
        from src.data.macro_data import MacroDataManager
        
        manager = MacroDataManager()
        print(f"✓ FRED数据管理器初始化成功")
        print(f"  API密钥: {api_key[:4]}...{api_key[-4:]}")
        
        # 测试获取关键指标
        print("\n测试获取宏观经济指标...")
        indicators = manager.get_key_indicators()
        
        if indicators:
            print(f"✓ 成功获取宏观指标")
            
            # 显示关键指标
            if 'interest_rates' in indicators:
                rates = indicators['interest_rates']
                print(f"\n利率数据:")
                print(f"  联邦基金利率: {rates.get('federal_funds_rate', 'N/A')}%")
                print(f"  10年期国债: {rates.get('treasury_10y', 'N/A')}%")
            
            if 'inflation' in indicators:
                inflation = indicators['inflation']
                print(f"\n通胀数据:")
                print(f"  CPI: {inflation.get('cpi', 'N/A')}%")
            
            # 经济健康评分
            print("\n测试经济健康评分...")
            health = manager.get_economic_health()
            if health:
                print(f"✓ 经济健康评分: {health.get('score', 'N/A')}/100")
                print(f"  衰退风险: {health.get('recession_risk', 'N/A')}")
            
            return True
        else:
            print("❌ 未获取到数据")
            return False
            
    except Exception as e:
        print(f"❌ FRED测试失败: {e}")
        return False

def test_options():
    """测试期权数据(Yahoo Finance,无需API密钥)"""
    print_section("测试期权数据 (Yahoo Finance)")
    
    try:
        from src.data.options_data import OptionsDataManager
        
        manager = OptionsDataManager()
        print(f"✓ 期权数据管理器初始化成功")
        print(f"  使用Yahoo Finance(无需API密钥)")
        
        # 测试获取期权分析
        print("\n测试获取TSLA期权分析...")
        analysis = manager.get_options_analysis('TSLA')
        
        if analysis:
            print(f"✓ 成功获取期权数据")
            print(f"  Put/Call比率: {analysis.get('put_call_ratio', 'N/A')}")
            print(f"  市场情绪: {analysis.get('market_sentiment', 'N/A')}")
            
            if 'max_pain' in analysis:
                print(f"  Max Pain价格: ${analysis.get('max_pain', 'N/A')}")
            
            return True
        else:
            print("⚠️  未获取到期权数据")
            return True  # Yahoo Finance可能暂时不可用,不算失败
            
    except Exception as e:
        print(f"❌ 期权数据测试失败: {e}")
        return False

def test_unified_provider():
    """测试统一数据提供器"""
    print_section("测试统一数据提供器")
    
    try:
        from src.data.unified_provider import UnifiedDataProvider
        
        provider = UnifiedDataProvider()
        print(f"✓ 统一数据提供器初始化成功")
        
        # 测试综合分析
        print("\n测试获取NVDA综合分析...")
        analysis = provider.get_comprehensive_analysis('NVDA')
        
        if analysis:
            print(f"✓ 成功获取综合分析")
            print(f"\n数据维度:")
            
            data_count = 0
            for key, value in analysis.items():
                if value and isinstance(value, dict):
                    data_count += 1
                    print(f"  ✓ {key}")
            
            print(f"\n总计: {data_count} 个数据维度可用")
            
            if 'comprehensive_score' in analysis:
                print(f"\n综合评分: {analysis.get('comprehensive_score', 'N/A')}/100")
                print(f"投资建议: {analysis.get('recommendation', 'N/A')}")
                print(f"置信度: {analysis.get('confidence', 'N/A')}")
            
            return True
        else:
            print("❌ 未获取到综合分析")
            return False
            
    except Exception as e:
        print(f"❌ 统一数据提供器测试失败: {e}")
        return False

def generate_report(results):
    """生成测试报告"""
    print_section("测试总结报告")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"\n总测试项: {total}")
    print(f"✓ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for name, result in results.items():
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    # 建议
    print("\n📊 建议:")
    if failed == 0:
        print("  ✓ 所有数据源测试通过!")
        print("  ✓ 可以开始启用数据源到策略中")
        print("  ✓ 参考: ENABLE_DATA_SOURCES_GUIDE.md")
    elif passed >= total * 0.5:
        print(f"  ⚠️  {failed} 个数据源测试失败")
        print("  建议:")
        print("  1. 检查失败的API密钥是否正确")
        print("  2. 确认网络连接正常")
        print("  3. 查看错误信息排查问题")
    else:
        print(f"  ❌ 多个数据源测试失败 ({failed}/{total})")
        print("  建议:")
        print("  1. 重新检查API密钥配置")
        print("  2. 参考 API_KEYS_SETUP_GUIDE.md")
        print("  3. 运行 setup_api_keys.py 重新配置")
    
    # 保存报告
    report_file = project_root / "data_sources_test_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("QT量化交易系统 - 数据源测试报告\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"总测试项: {total}\n")
        f.write(f"通过: {passed}\n")
        f.write(f"失败: {failed}\n")
        f.write(f"成功率: {passed/total*100:.1f}%\n\n")
        
        f.write("详细结果:\n")
        for name, result in results.items():
            status = "PASS" if result else "FAIL"
            f.write(f"  [{status}] {name}\n")
    
    print(f"\n✓ 测试报告已保存: {report_file}")

def main():
    """主函数"""
    print("=" * 70)
    print("  QT量化交易系统 - 数据源全面测试")
    print("=" * 70)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 测试各个数据源
    print("\n开始测试...\n")
    
    results['Alpha Vantage'] = test_alpha_vantage()
    results['Financial Modeling Prep'] = test_fmp()
    results['NewsAPI'] = test_newsapi()
    results['Finnhub'] = test_finnhub()
    results['FRED'] = test_fred()
    results['期权数据 (Yahoo)'] = test_options()
    results['统一数据提供器'] = test_unified_provider()
    
    # 生成报告
    generate_report(results)
    
    print("\n" + "=" * 70)
    print("测试完成!按任意键退出...")
    input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消测试")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
