"""
市场环境管理器
整合宏观经济、市场情绪、技术指标等多维度环境分析
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class MarketEnvironmentManager:
    """市场环境综合分析"""
    
    def __init__(self):
        self.fred_api_key = self._load_env('FRED_API_KEY')
        self.finnhub_api_key = self._load_env('FINNHUB_API_KEY')
        
    def _load_env(self, key: str) -> Optional[str]:
        """从.env文件手动加载API密钥"""
        env_file = project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == key:
                            return v.strip()
        return os.getenv(key)
    
    def get_macro_environment(self) -> Dict:
        """获取宏观经济环境评估
        
        Returns:
            {
                'fed_rate': float,          # 联邦基金利率
                'yield_curve': float,       # 10Y-2Y收益率差
                'inflation': float,         # CPI同比
                'unemployment': float,      # 失业率
                'environment': str,         # 'expansion', 'recession', 'neutral'
                'risk_level': str,          # 'low', 'medium', 'high'
                'recommendation': str       # 市场环境建议
            }
        """
        try:
            from src.data.macro_data import MacroDataManager
            
            print("   📡 请求宏观经济数据...")
            macro_mgr = MacroDataManager()
            snapshot = macro_mgr.get_macro_snapshot()
            indicators = snapshot.get('indicators', {})
            
            # 分析经济环境
            fed_rate = indicators.get('fed_funds_rate', 0)
            yield_curve = indicators.get('yield_curve_spread', 0)
            inflation = indicators.get('cpi_change', 0)
            unemployment = indicators.get('unemployment_rate', 0)
            
            # 判断经济环境
            environment = self._classify_environment(
                yield_curve, inflation, unemployment
            )
            
            # 评估风险等级
            risk_level = self._assess_risk_level(
                fed_rate, yield_curve, inflation
            )
            
            # 生成建议
            recommendation = self._generate_macro_recommendation(
                environment, risk_level
            )
            
            print(f"   ✅ 宏观环境: {environment.upper()}, 风险: {risk_level.upper()}")
            
            return {
                'fed_rate': fed_rate,
                'yield_curve': yield_curve,
                'inflation': inflation,
                'unemployment': unemployment,
                'environment': environment,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"   ⚠️  宏观数据获取失败: {e}")
            return self._get_default_macro()
    
    def _classify_environment(
        self, 
        yield_curve: float, 
        inflation: float, 
        unemployment: float
    ) -> str:
        """分类经济环境"""
        
        # 收益率曲线倒挂 = 衰退信号
        if yield_curve < -0.5:
            return 'recession_warning'
        
        # 高通胀 + 高失业 = 滞胀
        if inflation > 5.0 and unemployment > 6.0:
            return 'stagflation'
        
        # 低失业 + 温和通胀 = 扩张
        if unemployment < 4.5 and 2.0 <= inflation <= 3.0:
            return 'expansion'
        
        # 高通胀
        if inflation > 4.0:
            return 'high_inflation'
        
        # 默认中性
        return 'neutral'
    
    def _assess_risk_level(
        self, 
        fed_rate: float, 
        yield_curve: float, 
        inflation: float
    ) -> str:
        """评估市场风险等级"""
        
        risk_score = 0
        
        # 收益率曲线倒挂 (+3分)
        if yield_curve < 0:
            risk_score += 3
        
        # 高利率 (+2分)
        if fed_rate > 5.0:
            risk_score += 2
        
        # 高通胀 (+2分)
        if inflation > 4.0:
            risk_score += 2
        
        # 极端通胀 (+1分)
        if inflation > 6.0:
            risk_score += 1
        
        if risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_macro_recommendation(
        self, 
        environment: str, 
        risk_level: str
    ) -> str:
        """生成宏观环境交易建议"""
        
        recommendations = {
            'expansion': {
                'low': '经济扩张,风险较低,适合积极配置成长股',
                'medium': '经济扩张但有风险,建议均衡配置',
                'high': '经济扩张但风险上升,注意防御'
            },
            'recession_warning': {
                'low': '衰退信号出现,建议降低仓位',
                'medium': '衰退风险较高,建议防御性配置',
                'high': '衰退风险极高,建议大幅降低仓位'
            },
            'high_inflation': {
                'low': '高通胀环境,关注能源和大宗商品',
                'medium': '高通胀+中等风险,建议谨慎',
                'high': '高通胀+高风险,建议防御'
            },
            'stagflation': {
                'low': '滞胀环境,建议防御性资产',
                'medium': '滞胀+中等风险,高度谨慎',
                'high': '滞胀+高风险,大幅降低仓位'
            },
            'neutral': {
                'low': '市场环境中性,正常交易',
                'medium': '市场中性但有风险,适度谨慎',
                'high': '虽然经济中性但风险较高,注意防御'
            }
        }
        
        return recommendations.get(environment, {}).get(
            risk_level, 
            '市场环境不明确,建议谨慎'
        )
    
    def _get_default_macro(self) -> Dict:
        """获取默认宏观数据(当API失败时)"""
        return {
            'fed_rate': 0,
            'yield_curve': 0,
            'inflation': 0,
            'unemployment': 0,
            'environment': 'unknown',
            'risk_level': 'medium',
            'recommendation': '宏观数据暂时不可用,建议中性策略',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_market_sentiment_summary(self, symbol: str) -> Dict:
        """获取市场情绪综合评分
        
        整合:
        - 新闻情绪 (NewsAPI)
        - 技术指标 (Finnhub可选)
        - 分析师评级 (Finnhub可选)
        
        Returns:
            {
                'news_sentiment': float,        # 新闻情绪 -100~100
                'overall_sentiment': str,       # 'bullish', 'bearish', 'neutral'
                'confidence': float,            # 置信度 0~100
                'sources': list                 # 数据来源
            }
        """
        try:
            from src.utils.news_manager import NewsManager
            from src.utils.alternative_data_manager import AlternativeDataManager
            
            print(f"   📡 综合市场情绪分析 ({symbol})...")
            
            # 1. 获取新闻情绪
            news_mgr = NewsManager()
            news_summary = news_mgr.get_news_summary(symbol, days=7)
            news_score = news_summary['sentiment']['score']
            
            # 2. 获取另类数据(VIX等)
            alt_mgr = AlternativeDataManager()
            market_indicators = alt_mgr.get_market_indicators()
            
            # 计算VIX情绪分 (VIX越高,情绪分越低)
            vix_score = 0
            vix_info = market_indicators.get('vix')
            if vix_info:
                vix_val = vix_info['price']
                # VIX 20为中性(0分), 10为极度乐观(+50分), 30为极度恐慌(-50分)
                vix_score = (20 - vix_val) * 5
                vix_score = max(-50, min(50, vix_score))
                print(f"   📊 VIX指数: {vix_val} (情绪贡献: {vix_score:.1f})")
            
            # 计算美债收益率影响 (新增)
            yield_score = 0
            yield_info = market_indicators.get('us10y')
            if yield_info:
                yield_val = yield_info['price']
                yield_change = yield_info.get('change_pct', 0)
                # 收益率快速上升对科技股是利空
                if yield_change > 2.0:
                    yield_score = -20
                    print(f"   ⚠️ 美债收益率飙升 ({yield_val}%, +{yield_change}%) -> 情绪扣分")
                elif yield_change < -2.0:
                    yield_score = 10
                    print(f"   📉 美债收益率回落 ({yield_val}%, {yield_change}%) -> 情绪加分")

            # 综合评分 (新闻 50% + VIX 30% + 收益率 20%)
            overall_score = (news_score * 0.5) + (vix_score * 0.3) + (yield_score)
            
            # 分类情绪
            if overall_score > 30:
                overall_sentiment = 'bullish'
            elif overall_score < -30:
                overall_sentiment = 'bearish'
            else:
                overall_sentiment = 'neutral'
            
            print(f"   ✅ 综合情绪: {overall_sentiment.upper()} ({overall_score:.1f}/100)")
            
            return {
                'news_sentiment': news_score,
                'vix_sentiment': vix_score,
                'market_indicators': market_indicators,
                'overall_sentiment': overall_sentiment,
                'overall_score': round(overall_score, 1),
                'confidence': news_summary['confidence'],
                'sources': ['NewsAPI', 'VIX'],
                'recommendation': news_summary['recommendation']
            }
            
        except Exception as e:
            print(f"   ⚠️  情绪分析失败: {e}")
            return {
                'news_sentiment': 0,
                'overall_sentiment': 'neutral',
                'overall_score': 0,
                'confidence': 0,
                'sources': [],
                'recommendation': '情绪数据暂时不可用'
            }
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """获取综合市场环境分析
        
        Returns:
            {
                'macro': dict,          # 宏观环境
                'sentiment': dict,      # 市场情绪
                'overall_risk': str,    # 综合风险等级
                'position_adjustment': float,  # 建议仓位调整 0.5-1.5
                'recommendation': str   # 综合建议
            }
        """
        print(f"\n{'='*60}")
        print(f"📊 市场环境综合分析 ({symbol})")
        print(f"{'='*60}")
        
        # 获取宏观环境
        print("\n[1/2] 宏观经济环境...")
        macro = self.get_macro_environment()
        
        # 获取市场情绪
        print(f"\n[2/2] 市场情绪分析...")
        sentiment = self.get_market_sentiment_summary(symbol)
        
        # 综合风险评估
        overall_risk = self._assess_overall_risk(macro, sentiment)
        
        # 仓位调整建议
        position_adj = self._calculate_position_adjustment(macro, sentiment)
        
        # 综合建议
        recommendation = self._generate_comprehensive_recommendation(
            macro, sentiment, overall_risk, position_adj
        )
        
        print(f"\n{'='*60}")
        print(f"✅ 综合分析完成")
        print(f"{'='*60}\n")
        
        return {
            'macro': macro,
            'sentiment': sentiment,
            'overall_risk': overall_risk,
            'position_adjustment': position_adj,
            'recommendation': recommendation,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _assess_overall_risk(self, macro: Dict, sentiment: Dict) -> str:
        """评估综合风险"""
        
        risk_score = 0
        
        # 宏观风险
        macro_risk = macro.get('risk_level', 'medium')
        if macro_risk == 'high':
            risk_score += 3
        elif macro_risk == 'medium':
            risk_score += 2
        else:
            risk_score += 1
        
        # 情绪风险
        sentiment_score = sentiment.get('overall_score', 0)
        if sentiment_score < -50:  # 极度悲观
            risk_score += 2
        elif sentiment_score < -20:  # 悲观
            risk_score += 1
        
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_position_adjustment(
        self, 
        macro: Dict, 
        sentiment: Dict
    ) -> float:
        """计算仓位调整系数
        
        Returns:
            0.5 = 减半仓位
            1.0 = 正常仓位
            1.5 = 增加50%仓位
        """
        adjustment = 1.0
        
        # 宏观环境调整
        env = macro.get('environment', 'neutral')
        if env == 'expansion':
            adjustment += 0.2
        elif env in ['recession_warning', 'stagflation']:
            adjustment -= 0.3
        elif env == 'high_inflation':
            adjustment -= 0.1
        
        # 情绪调整
        sentiment_score = sentiment.get('overall_score', 0)
        if sentiment_score > 50:  # 极度乐观
            adjustment += 0.1
        elif sentiment_score > 30:  # 乐观
            adjustment += 0.05
        elif sentiment_score < -50:  # 极度悲观
            adjustment -= 0.2
        elif sentiment_score < -30:  # 悲观
            adjustment -= 0.1
        
        # 限制在0.5-1.5范围
        return max(0.5, min(1.5, adjustment))
    
    def _generate_comprehensive_recommendation(
        self, 
        macro: Dict, 
        sentiment: Dict, 
        risk: str, 
        position_adj: float
    ) -> str:
        """生成综合交易建议"""
        
        lines = []
        
        # 宏观环境
        lines.append(f"宏观: {macro.get('recommendation', 'N/A')}")
        
        # 市场情绪
        vix_info = sentiment.get('market_indicators', {}).get('vix')
        if vix_info:
            vix_val = vix_info['price']
            if vix_val > 30:
                lines.append(f"⚠️ VIX恐慌({vix_val}),注意避险")
            elif vix_val < 13:
                lines.append(f"⚠️ VIX过低({vix_val}),警惕回调")
        
        lines.append(f"情绪: {sentiment.get('recommendation', 'N/A')}")
        
        # 综合建议
        if risk == 'high':
            lines.append("⚠️ 综合风险较高,建议降低仓位,等待更好时机")
        elif risk == 'medium':
            lines.append("⚡ 风险适中,可正常交易但需谨慎")
        else:
            lines.append("✅ 风险较低,可积极寻找机会")
        
        # 仓位建议
        if position_adj > 1.2:
            lines.append(f"建议仓位: 增加至{position_adj:.1%}")
        elif position_adj < 0.8:
            lines.append(f"建议仓位: 减少至{position_adj:.1%}")
        else:
            lines.append(f"建议仓位: 维持正常水平")
        
        return " | ".join(lines)
    
    def get_sector_analysis(self, symbol: str) -> Dict:
        """获取板块相对强度分析"""
        try:
            from src.utils.alternative_data_manager import AlternativeDataManager
            alt_mgr = AlternativeDataManager()
            
            # 默认假设是科技股，使用XLK作为基准
            # 实际应用中应该根据symbol查找对应板块
            benchmark = 'XLK'
            if symbol in ['XOM', 'CVX']: benchmark = 'XLE'
            elif symbol in ['JPM', 'BAC']: benchmark = 'XLF'
            elif symbol in ['TSLA', 'AMZN', 'HD']: benchmark = 'XLY'  # 消费类 (TSLA属于非必需消费品)
            
            rs_score = alt_mgr.get_relative_strength(symbol, benchmark)
            
            status = 'neutral'
            if rs_score > 0.05: status = 'leading'
            elif rs_score < -0.05: status = 'lagging'
            
            print(f"   💪 相对强度 ({symbol} vs {benchmark}): {rs_score:+.2%} ({status})")
            
            return {
                'relative_strength': rs_score,
                'benchmark': benchmark,
                'status': status
            }
        except Exception as e:
            print(f"   ⚠️ 板块分析失败: {e}")
            return {'relative_strength': 0, 'status': 'neutral'}
        

# 测试代码
if __name__ == "__main__":
    print("=" * 80)
    print("📊 市场环境管理器测试")
    print("=" * 80)
    print()
    
    mgr = MarketEnvironmentManager()
    
    # 测试单独功能
    print("\n【测试1: 宏观环境】")
    print("-" * 80)
    macro = mgr.get_macro_environment()
    print(f"\n联邦基金利率: {macro['fed_rate']:.2f}%")
    print(f"收益率曲线: {macro['yield_curve']:.2f}")
    print(f"通胀率: {macro['inflation']:.2f}%")
    print(f"失业率: {macro['unemployment']:.2f}%")
    print(f"经济环境: {macro['environment']}")
    print(f"风险等级: {macro['risk_level']}")
    print(f"建议: {macro['recommendation']}")
    
    # 测试综合分析
    print("\n【测试2: NVDA综合分析】")
    print("-" * 80)
    analysis = mgr.get_comprehensive_analysis('NVDA')
    
    print(f"\n📊 综合评估:")
    print(f"  宏观环境: {analysis['macro']['environment']} ({analysis['macro']['risk_level']} risk)")
    print(f"  市场情绪: {analysis['sentiment']['overall_sentiment']} ({analysis['sentiment']['overall_score']}/100)")
    print(f"  综合风险: {analysis['overall_risk'].upper()}")
    print(f"  仓位调整: {analysis['position_adjustment']:.1%}")
    print(f"\n💡 建议:")
    print(f"  {analysis['recommendation']}")
    
    # 测试板块分析
    print("\n【测试3: 板块相对强度分析】")
    print("-" * 80)
    sector_analysis = mgr.get_sector_analysis('NVDA')
    print(f"\n相对强度: {sector_analysis['relative_strength']:+.2%}")
    print(f"状态: {sector_analysis['status']}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成!")
    print("=" * 80)
