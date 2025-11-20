"""
统一数据源管理器
整合所有类型的数据源,提供一站式数据访问接口
"""
import pandas as pd
from typing import Dict, Optional
from datetime import datetime
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入各数据源管理器
try:
    from data.providers import YFinanceClient
    from data.alphavantage import AlphaVantageClient
    from data.news_sentiment import NewsDataManager
    from data.fundamentals import FundamentalsDataManager
    from data.options_data import OptionsDataManager
    from data.macro_data import MacroDataManager
    from data.social_sentiment import SocialMediaDataManager
    from data.insider_trading import InsiderDataManager
except ImportError as e:
    print(f"导入数据源模块失败: {e}")


class UnifiedDataProvider:
    """
    统一数据源提供器
    整合所有数据源,提供一站式访问接口
    """
    
    def __init__(self):
        """初始化所有数据源"""
        self.data_sources = {}
        
        # 1. 价格数据源
        print("初始化价格数据源...")
        try:
            self.data_sources['yahoo'] = YFinanceClient()
            print("  ✓ Yahoo Finance")
        except Exception as e:
            print(f"  ✗ Yahoo Finance失败: {e}")
        
        try:
            self.data_sources['alphavantage'] = AlphaVantageClient()
            print("  ✓ Alpha Vantage")
        except Exception as e:
            print(f"  ✗ Alpha Vantage失败: {e}")
        
        # 2. 新闻情绪数据源
        print("初始化新闻情绪数据源...")
        try:
            self.data_sources['news'] = NewsDataManager()
            print("  ✓ 新闻情绪分析")
        except Exception as e:
            print(f"  ✗ 新闻情绪分析失败: {e}")
        
        # 3. 基本面数据源
        print("初始化基本面数据源...")
        try:
            self.data_sources['fundamentals'] = FundamentalsDataManager()
            print("  ✓ 基本面数据")
        except Exception as e:
            print(f"  ✗ 基本面数据失败: {e}")
        
        # 4. 期权数据源
        print("初始化期权数据源...")
        try:
            self.data_sources['options'] = OptionsDataManager()
            print("  ✓ 期权数据")
        except Exception as e:
            print(f"  ✗ 期权数据失败: {e}")
        
        # 5. 宏观经济数据源
        print("初始化宏观经济数据源...")
        try:
            self.data_sources['macro'] = MacroDataManager()
            print("  ✓ 宏观经济数据")
        except Exception as e:
            print(f"  ✗ 宏观经济数据失败: {e}")
        
        # 6. 社交媒体数据源
        print("初始化社交媒体数据源...")
        try:
            self.data_sources['social'] = SocialMediaDataManager()
            print("  ✓ 社交媒体情绪")
        except Exception as e:
            print(f"  ✗ 社交媒体情绪失败: {e}")
        
        # 7. 内部人交易数据源
        print("初始化内部人交易数据源...")
        try:
            self.data_sources['insider'] = InsiderDataManager()
            print("  ✓ 内部人交易")
        except Exception as e:
            print(f"  ✗ 内部人交易失败: {e}")
        
        print(f"\n数据源初始化完成,已激活{len(self.data_sources)}个数据源")
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        获取股票的全方位综合分析
        整合所有数据源的信息
        """
        print(f"\n{'='*60}")
        print(f"正在获取{symbol}的全方位分析...")
        print(f"{'='*60}\n")
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price_data': {},
            'news_sentiment': {},
            'fundamentals': {},
            'options_sentiment': {},
            'macro_environment': {},
            'social_sentiment': {},
            'insider_activity': {},
            '综合评分': {}
        }
        
        # 1. 获取价格数据
        if 'yahoo' in self.data_sources:
            try:
                print("📈 获取价格数据...")
                ticker = self.data_sources['yahoo'].yf.Ticker(symbol)
                info = ticker.info
                result['price_data'] = {
                    'current_price': info.get('currentPrice', 0),
                    'previous_close': info.get('previousClose', 0),
                    'day_change': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('volume', 0),
                    '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                    '52_week_low': info.get('fiftyTwoWeekLow', 0),
                }
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 2. 获取新闻情绪
        if 'news' in self.data_sources:
            try:
                print("📰 获取新闻情绪...")
                news_result = self.data_sources['news'].get_stock_sentiment(symbol, days_back=7)
                result['news_sentiment'] = news_result.get('overall_sentiment', {})
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 3. 获取基本面
        if 'fundamentals' in self.data_sources:
            try:
                print("📊 获取基本面数据...")
                fund_analysis = self.data_sources['fundamentals'].get_comprehensive_analysis(symbol)
                result['fundamentals'] = {
                    'company_profile': fund_analysis.get('company_profile', {}),
                    'financial_health': self.data_sources['fundamentals'].calculate_financial_health_score(fund_analysis)
                }
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 4. 获取期权情绪
        if 'options' in self.data_sources:
            try:
                print("📉 获取期权数据...")
                opt_analysis = self.data_sources['options'].get_options_analysis(symbol)
                result['options_sentiment'] = opt_analysis.get('sentiment_analysis', {})
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 5. 获取宏观环境
        if 'macro' in self.data_sources:
            try:
                print("🌍 获取宏观经济数据...")
                macro_snapshot = self.data_sources['macro'].get_macro_snapshot()
                result['macro_environment'] = macro_snapshot.get('health_score', {})
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 6. 获取社交媒体情绪
        if 'social' in self.data_sources:
            try:
                print("💬 获取社交媒体情绪...")
                social_result = self.data_sources['social'].get_social_sentiment(symbol)
                result['social_sentiment'] = social_result.get('combined_metrics', {})
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 7. 获取内部人交易
        if 'insider' in self.data_sources:
            try:
                print("👔 获取内部人交易...")
                insider_analysis = self.data_sources['insider'].get_insider_analysis(symbol)
                result['insider_activity'] = insider_analysis.get('sentiment', {})
                print("  ✓ 完成")
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        # 8. 计算综合评分
        result['综合评分'] = self._calculate_综合_score(result)
        
        print(f"\n{'='*60}")
        print("数据获取完成!")
        print(f"{'='*60}\n")
        
        return result
    
    def _calculate_综合_score(self, analysis: Dict) -> Dict:
        """计算综合评分(0-100)"""
        score = 50  # 基准分
        factors = []
        weights = {
            'fundamentals': 0.25,
            'news': 0.15,
            'social': 0.15,
            'options': 0.15,
            'insider': 0.15,
            'macro': 0.15
        }
        
        # 基本面评分
        if analysis.get('fundamentals', {}).get('financial_health'):
            fund_score = analysis['fundamentals']['financial_health'].get('score', 50)
            contribution = (fund_score - 50) * weights['fundamentals']
            score += contribution
            factors.append(f"基本面: {fund_score}/100")
        
        # 新闻情绪
        if analysis.get('news_sentiment', {}).get('sentiment'):
            news_sent = analysis['news_sentiment']['sentiment']
            if news_sent == 'positive':
                score += 10 * weights['news']
                factors.append("新闻情绪: 正面")
            elif news_sent == 'negative':
                score -= 10 * weights['news']
                factors.append("新闻情绪: 负面")
        
        # 社交媒体情绪
        if analysis.get('social_sentiment', {}).get('overall_sentiment'):
            social_sent = analysis['social_sentiment']['overall_sentiment']
            if social_sent == 'bullish':
                score += 15 * weights['social']
                factors.append("社交情绪: 看涨")
            elif social_sent == 'bearish':
                score -= 15 * weights['social']
                factors.append("社交情绪: 看跌")
        
        # 期权情绪
        if analysis.get('options_sentiment', {}).get('sentiment'):
            opt_sent = analysis['options_sentiment']['sentiment']
            if opt_sent == 'bullish':
                score += 10 * weights['options']
                factors.append("期权情绪: 看涨")
            elif opt_sent == 'bearish':
                score -= 10 * weights['options']
                factors.append("期权情绪: 看跌")
        
        # 内部人交易
        if analysis.get('insider_activity', {}).get('sentiment'):
            insider_sent = analysis['insider_activity']['sentiment']
            if 'bullish' in insider_sent:
                score += 15 * weights['insider']
                factors.append("内部人: 净买入")
            elif 'bearish' in insider_sent:
                score -= 15 * weights['insider']
                factors.append("内部人: 净卖出")
        
        # 宏观环境
        if analysis.get('macro_environment', {}).get('score'):
            macro_score = analysis['macro_environment']['score']
            contribution = (macro_score - 50) * weights['macro']
            score += contribution
            factors.append(f"宏观环境: {macro_score}/100")
        
        # 限制在0-100范围
        score = max(0, min(100, score))
        
        # 评级
        if score >= 80:
            grade = 'A - 强烈买入'
            recommendation = 'STRONG BUY'
        elif score >= 70:
            grade = 'B - 买入'
            recommendation = 'BUY'
        elif score >= 60:
            grade = 'C - 持有'
            recommendation = 'HOLD'
        elif score >= 50:
            grade = 'D - 观望'
            recommendation = 'WATCH'
        else:
            grade = 'F - 谨慎'
            recommendation = 'CAUTION'
        
        return {
            'score': round(score, 1),
            'grade': grade,
            'recommendation': recommendation,
            'contributing_factors': factors,
            'weights': weights
        }
    
    def generate_report(self, symbol: str, save_path: Optional[str] = None) -> str:
        """生成综合分析报告"""
        analysis = self.get_comprehensive_analysis(symbol)
        
        # 生成Markdown报告
        report = f"""# {symbol} 综合投资分析报告

生成时间: {analysis['timestamp']}

---

## 📊 综合评分

**评分**: {analysis['综合评分']['score']}/100  
**评级**: {analysis['综合评分']['grade']}  
**建议**: {analysis['综合评分']['recommendation']}

### 评分因素
"""
        for factor in analysis['综合评分']['contributing_factors']:
            report += f"- {factor}\n"
        
        report += "\n---\n\n## 📈 价格数据\n\n"
        if analysis['price_data']:
            pd_data = analysis['price_data']
            report += f"- 当前价格: ${pd_data.get('current_price', 'N/A')}\n"
            report += f"- 昨日收盘: ${pd_data.get('previous_close', 'N/A')}\n"
            report += f"- 日涨跌幅: {pd_data.get('day_change', 0):.2f}%\n"
            report += f"- 成交量: {pd_data.get('volume', 0):,}\n"
            report += f"- 52周最高: ${pd_data.get('52_week_high', 'N/A')}\n"
            report += f"- 52周最低: ${pd_data.get('52_week_low', 'N/A')}\n"
        
        report += "\n---\n\n## 📰 新闻情绪\n\n"
        if analysis['news_sentiment']:
            ns = analysis['news_sentiment']
            report += f"- 整体情绪: **{ns.get('sentiment', 'N/A').upper()}**\n"
            report += f"- 平均得分: {ns.get('avg_score', 0):.3f}\n"
            report += f"- 正面新闻: {ns.get('positive_ratio', 0)*100:.1f}%\n"
            report += f"- 负面新闻: {ns.get('negative_ratio', 0)*100:.1f}%\n"
            report += f"- 新闻总数: {ns.get('total_news', 0)}\n"
        
        report += "\n---\n\n## 💼 基本面分析\n\n"
        if analysis['fundamentals'].get('financial_health'):
            fh = analysis['fundamentals']['financial_health']
            report += f"- 财务健康度: **{fh['score']}/100**\n"
            report += f"- 评级: {fh['grade']}\n"
            report += "\n评分详情:\n"
            for detail in fh.get('details', []):
                report += f"  - {detail}\n"
        
        report += "\n---\n\n## 📉 期权市场情绪\n\n"
        if analysis['options_sentiment']:
            opt = analysis['options_sentiment']
            report += f"- Put/Call比率: {opt.get('put_call_ratio', 'N/A')}\n"
            report += f"- 市场情绪: **{opt.get('sentiment', 'N/A').upper()}**\n"
            report += f"- Max Pain: ${opt.get('max_pain', 0):.2f}\n"
        
        report += "\n---\n\n## 🌍 宏观经济环境\n\n"
        if analysis['macro_environment']:
            macro = analysis['macro_environment']
            report += f"- 经济健康度: **{macro.get('score', 0)}/100**\n"
            report += f"- 评级: {macro.get('grade', 'N/A')}\n"
        
        report += "\n---\n\n## 💬 社交媒体情绪\n\n"
        if analysis['social_sentiment']:
            social = analysis['social_sentiment']
            report += f"- 整体情绪: **{social.get('overall_sentiment', 'N/A').upper()}**\n"
            report += f"- 情绪得分: {social.get('avg_sentiment_score', 0):.3f}\n"
            report += f"- 看涨比例: {social.get('bullish_ratio', 0)*100:.1f}%\n"
            report += f"- 讨论总数: {social.get('total_posts', 0)}\n"
        
        report += "\n---\n\n## 👔 内部人交易\n\n"
        if analysis['insider_activity']:
            insider = analysis['insider_activity']
            report += f"- 交易情绪: **{insider.get('sentiment', 'N/A').upper()}**\n"
            report += f"- 买入比例: {insider.get('buy_ratio', 0)*100:.1f}%\n"
            report += f"- 总交易次数: {insider.get('total_transactions', 0)}\n"
        
        report += "\n---\n\n## ⚠️ 免责声明\n\n"
        report += "本报告仅供参考,不构成投资建议。投资有风险,决策需谨慎。\n"
        
        # 保存报告
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n报告已保存到: {save_path}")
        
        return report


if __name__ == "__main__":
    # 测试统一数据源
    provider = UnifiedDataProvider()
    
    # 生成TSLA综合分析报告
    symbol = 'TSLA'
    report_path = f"k:/QT/reports/{symbol}_综合分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # 生成报告
    report = provider.generate_report(symbol, save_path=report_path)
    
    # 打印报告
    print(report)
