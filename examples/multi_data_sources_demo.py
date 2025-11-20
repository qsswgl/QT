"""
多维度数据源使用示例
演示如何使用所有7类数据源进行综合分析
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime


def example_1_price_data():
    """示例1: 获取价格数据"""
    print("\n" + "="*60)
    print("示例1: 价格数据获取")
    print("="*60)
    
    from src.data.providers import YFinanceClient
    
    client = YFinanceClient()
    symbol = 'TSLA'
    
    # 获取历史数据
    ticker = client.yf.Ticker(symbol)
    hist = ticker.history(period='1mo')
    
    print(f"\n{symbol} 最近1个月价格数据:")
    print(hist.tail())
    
    # 获取实时信息
    info = ticker.info
    print(f"\n{symbol} 实时信息:")
    print(f"当前价格: ${info.get('currentPrice', 'N/A')}")
    print(f"市值: ${info.get('marketCap', 0):,.0f}")
    print(f"52周最高: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
    print(f"52周最低: ${info.get('fiftyTwoWeekLow', 'N/A')}")


def example_2_news_sentiment():
    """示例2: 新闻情绪分析"""
    print("\n" + "="*60)
    print("示例2: 新闻情绪分析")
    print("="*60)
    
    from src.data.news_sentiment import NewsDataManager
    
    manager = NewsDataManager()
    symbol = 'TSLA'
    
    result = manager.get_stock_sentiment(symbol, days_back=7)
    
    if result['overall_sentiment']:
        sentiment = result['overall_sentiment']
        print(f"\n{symbol} 新闻情绪 (最近7天):")
        print(f"整体情绪: {sentiment['sentiment'].upper()}")
        print(f"平均得分: {sentiment['avg_score']}")
        print(f"正面新闻: {sentiment['positive_ratio']*100:.1f}%")
        print(f"负面新闻: {sentiment['negative_ratio']*100:.1f}%")
        print(f"新闻总数: {sentiment['total_news']}")
        
        if not result['news_df'].empty:
            print(f"\n最新3条新闻:")
            for idx, row in result['news_df'].head(3).iterrows():
                print(f"\n[{row['sentiment'].upper()}] {row['title'][:80]}")
                print(f"来源: {row['source']} | 得分: {row['sentiment_score']}")
    else:
        print("⚠️ 新闻数据获取失败,请检查API配置")


def example_3_fundamentals():
    """示例3: 基本面分析"""
    print("\n" + "="*60)
    print("示例3: 基本面数据分析")
    print("="*60)
    
    from src.data.fundamentals import FundamentalsDataManager
    
    manager = FundamentalsDataManager()
    symbol = 'TSLA'
    
    analysis = manager.get_comprehensive_analysis(symbol)
    
    if analysis['company_profile']:
        profile = analysis['company_profile']
        print(f"\n{symbol} 公司概况:")
        print(f"名称: {profile.get('name') or profile.get('company_name', 'N/A')}")
        print(f"行业: {profile.get('sector', 'N/A')} - {profile.get('industry', 'N/A')}")
        print(f"市值: ${profile.get('market_cap', 0):,.0f}")
        
        # 关键指标
        print(f"\n关键财务指标:")
        print(f"PE比率: {profile.get('pe_ratio') or profile.get('PERatio', 'N/A')}")
        print(f"ROE: {(profile.get('roe', 0)*100):.2f}%")
        print(f"利润率: {(profile.get('profit_margin', 0)*100):.2f}%")
        
        # 财务健康度评分
        health = manager.calculate_financial_health_score(analysis)
        print(f"\n财务健康度:")
        print(f"评分: {health['score']}/100")
        print(f"评级: {health['grade']}")
    else:
        print("⚠️ 基本面数据获取失败,请检查API配置")


def example_4_options():
    """示例4: 期权市场分析"""
    print("\n" + "="*60)
    print("示例4: 期权市场分析")
    print("="*60)
    
    from src.data.options_data import OptionsDataManager
    
    manager = OptionsDataManager()
    symbol = 'TSLA'
    
    analysis = manager.get_options_analysis(symbol)
    
    if not analysis['calls'].empty and not analysis['puts'].empty:
        print(f"\n{symbol} 期权数据:")
        print(f"到期日: {analysis['expiration']}")
        print(f"Call期权数: {len(analysis['calls'])}")
        print(f"Put期权数: {len(analysis['puts'])}")
        
        if analysis['sentiment_analysis']:
            sentiment = analysis['sentiment_analysis']
            print(f"\n期权市场情绪:")
            print(f"Put/Call比率: {sentiment['put_call_ratio']}")
            print(f"市场情绪: {sentiment['sentiment'].upper()}")
            print(f"Max Pain: ${sentiment['max_pain']:.2f}")
            print(f"Call成交量: {sentiment['call_volume']:,}")
            print(f"Put成交量: {sentiment['put_volume']:,}")
    else:
        print("⚠️ 期权数据获取失败,请检查API配置")


def example_5_macro():
    """示例5: 宏观经济分析"""
    print("\n" + "="*60)
    print("示例5: 宏观经济环境分析")
    print("="*60)
    
    from src.data.macro_data import MacroDataManager
    
    manager = MacroDataManager()
    
    snapshot = manager.get_macro_snapshot()
    
    if snapshot['indicators']:
        print(f"\n关键宏观指标:")
        indicators = snapshot['indicators']
        print(f"联邦基金利率: {indicators.get('fed_funds_rate', 'N/A'):.2f}%")
        print(f"10Y-2Y国债利差: {indicators.get('yield_curve_spread', 'N/A'):.2f}%")
        print(f"失业率: {indicators.get('unemployment_rate', 'N/A'):.2f}%")
        if 'cpi_change' in indicators:
            print(f"CPI同比变化: {indicators['cpi_change']:.2f}%")
        
        if snapshot['health_score']:
            health = snapshot['health_score']
            print(f"\n经济健康度:")
            print(f"评分: {health['score']}/100")
            print(f"评级: {health['grade']}")
    else:
        print("⚠️ 宏观数据获取失败,请检查API配置")


def example_6_social():
    """示例6: 社交媒体情绪"""
    print("\n" + "="*60)
    print("示例6: 社交媒体情绪分析")
    print("="*60)
    
    from src.data.social_sentiment import SocialMediaDataManager
    
    manager = SocialMediaDataManager()
    symbol = 'TSLA'
    
    result = manager.get_social_sentiment(symbol)
    
    if result['reddit_metrics']:
        print(f"\n{symbol} Reddit情绪:")
        metrics = result['reddit_metrics']
        print(f"帖子总数: {metrics['total_posts']}")
        print(f"看涨比例: {metrics['bullish_ratio']*100:.1f}%")
        print(f"看跌比例: {metrics['bearish_ratio']*100:.1f}%")
        print(f"整体情绪: {metrics['overall_sentiment'].upper()}")
    
    if result['stocktwits_metrics']:
        print(f"\n{symbol} StockTwits情绪:")
        metrics = result['stocktwits_metrics']
        print(f"消息总数: {metrics['total_posts']}")
        print(f"看涨比例: {metrics['bullish_ratio']*100:.1f}%")
        print(f"整体情绪: {metrics['overall_sentiment'].upper()}")
    
    if result['combined_metrics']:
        print(f"\n{symbol} 综合社交情绪:")
        combined = result['combined_metrics']
        print(f"总讨论数: {combined['total_posts']}")
        print(f"综合得分: {combined['avg_sentiment_score']:.3f}")
        print(f"整体情绪: {combined['overall_sentiment'].upper()}")
    
    if not result['reddit_metrics'] and not result['stocktwits_metrics']:
        print("⚠️ 社交媒体数据获取失败")


def example_7_insider():
    """示例7: 内部人交易分析"""
    print("\n" + "="*60)
    print("示例7: 内部人交易分析")
    print("="*60)
    
    from src.data.insider_trading import InsiderDataManager
    
    manager = InsiderDataManager()
    symbol = 'TSLA'
    
    analysis = manager.get_insider_analysis(symbol, days=90)
    
    if not analysis['transactions'].empty:
        print(f"\n{symbol} 内部人交易 (最近90天):")
        print(f"记录总数: {len(analysis['transactions'])}")
        
        if analysis['sentiment']:
            sentiment = analysis['sentiment']
            print(f"\n内部人情绪:")
            print(f"总交易次数: {sentiment['total_transactions']}")
            print(f"买入次数: {sentiment['buy_count']}")
            print(f"卖出次数: {sentiment['sell_count']}")
            print(f"买入比例: {sentiment['buy_ratio']*100:.1f}%")
            print(f"情绪: {sentiment['sentiment'].upper()}")
    else:
        print("⚠️ 内部人交易数据获取失败,请检查API配置")


def example_8_comprehensive():
    """示例8: 综合分析报告"""
    print("\n" + "="*60)
    print("示例8: 生成综合分析报告")
    print("="*60)
    
    from src.data.unified_provider import UnifiedDataProvider
    
    provider = UnifiedDataProvider()
    symbol = 'TSLA'
    
    # 获取综合分析
    analysis = provider.get_comprehensive_analysis(symbol)
    
    # 显示综合评分
    score = analysis['综合评分']
    print(f"\n{symbol} 综合投资评分:")
    print(f"评分: {score['score']}/100")
    print(f"评级: {score['grade']}")
    print(f"建议: {score['recommendation']}")
    
    print(f"\n评分因素:")
    for factor in score['contributing_factors']:
        print(f"  - {factor}")
    
    # 生成报告
    report_dir = 'k:/QT/reports'
    os.makedirs(report_dir, exist_ok=True)
    
    report_path = f"{report_dir}/{symbol}_综合分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report = provider.generate_report(symbol, save_path=report_path)
    
    print(f"\n✓ 报告已保存到: {report_path}")


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*60)
    print("多维度数据源系统使用示例")
    print("="*60)
    print("\n本脚本将演示7类数据源的使用方法:")
    print("1. 价格数据 (Yahoo Finance)")
    print("2. 新闻情绪 (NewsAPI, Finnhub)")
    print("3. 基本面数据 (FMP, Alpha Vantage)")
    print("4. 期权数据 (Tradier, Yahoo Finance)")
    print("5. 宏观经济 (FRED, World Bank)")
    print("6. 社交媒体 (Reddit, StockTwits)")
    print("7. 内部人交易 (SEC EDGAR, FMP)")
    print("8. 综合分析 (整合所有数据源)")
    
    print("\n⚠️ 注意: 部分数据源需要API密钥才能使用")
    print("如果某些示例失败,请检查API密钥配置")
    
    input("\n按Enter键开始演示...")
    
    # 运行所有示例
    try:
        example_1_price_data()
        input("\n按Enter继续下一个示例...")
        
        example_2_news_sentiment()
        input("\n按Enter继续下一个示例...")
        
        example_3_fundamentals()
        input("\n按Enter继续下一个示例...")
        
        example_4_options()
        input("\n按Enter继续下一个示例...")
        
        example_5_macro()
        input("\n按Enter继续下一个示例...")
        
        example_6_social()
        input("\n按Enter继续下一个示例...")
        
        example_7_insider()
        input("\n按Enter继续最后一个示例...")
        
        example_8_comprehensive()
        
        print("\n" + "="*60)
        print("所有示例演示完成!")
        print("="*60)
        print("\n更多信息请查看:")
        print("- 完整文档: docs/MULTI_DIMENSIONAL_DATA_SOURCES_GUIDE.md")
        print("- 各数据源代码: src/data/")
        
    except KeyboardInterrupt:
        print("\n\n用户中断,演示结束")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
