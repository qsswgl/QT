"""
新闻情绪分析管理器 - 使用NewsAPI
用于获取股票新闻并计算情绪评分
"""
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

class NewsManager:
    """新闻情绪分析管理器"""
    
    def __init__(self):
        """初始化管理器"""
        # 加载环境变量
        self._load_env()
        
        self.api_key = os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("❌ 未找到NEWS_API_KEY环境变量")
        
        self.base_url = "https://newsapi.org/v2/everything"
        self.cache = {}  # 简单缓存避免重复请求
        
        # 情绪关键词字典
        self.positive_keywords = [
            'surge', 'jump', 'soar', 'rally', 'gain', 'rise', 'up', 'bullish', 
            'strong', 'beat', 'exceed', 'growth', 'profit', 'record', 'high',
            'breakthrough', 'innovation', 'success', 'win', 'positive', 'upgrade',
            'outperform', 'buy', 'optimistic', 'momentum'
        ]
        
        self.negative_keywords = [
            'fall', 'drop', 'plunge', 'crash', 'decline', 'down', 'bearish',
            'weak', 'miss', 'loss', 'cut', 'low', 'concern', 'risk', 'fear',
            'sell', 'downgrade', 'underperform', 'warning', 'caution', 'negative',
            'pressure', 'threat', 'crisis', 'lawsuit', 'investigation'
        ]
    
    def _load_env(self):
        """加载.env环境变量"""
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def get_recent_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        获取最近N天的新闻
        
        Args:
            symbol: 股票代码 (如 'NVDA')
            days: 回溯天数 (默认7天)
        
        Returns:
            list: 新闻列表,每个新闻包含:
                - title: 标题
                - source: 来源
                - publishedAt: 发布时间
                - description: 描述
                - url: 链接
        """
        # 检查缓存
        cache_key = f"news_{symbol}_{days}"
        if cache_key in self.cache:
            print(f"   💾 使用缓存的新闻数据: {symbol}")
            return self.cache[cache_key]
        
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 公司名称映射
            company_names = {
                'NVDA': 'Nvidia',
                'TSLA': 'Tesla',
                'INTC': 'Intel'
            }
            company_name = company_names.get(symbol, symbol)
            
            # 构建查询
            query = f"{symbol} OR {company_name}"
            
            params = {
                'q': query,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.api_key
            }
            
            print(f"   📡 请求 {symbol} 新闻 (最近{days}天)...")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
                return []
            
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"   ❌ API错误: {data.get('message', 'Unknown error')}")
                return []
            
            articles = data.get('articles', [])
            
            # 简化新闻数据
            news_list = []
            for article in articles[:50]:  # 最多取50条
                news_list.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'publishedAt': article.get('publishedAt', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', '')
                })
            
            # 缓存结果
            self.cache[cache_key] = news_list
            
            print(f"   ✅ 成功获取 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            print(f"   ❌ 获取新闻失败: {e}")
            return []
    
    def calculate_sentiment_score(self, articles: List[Dict]) -> Dict:
        """
        计算新闻情绪评分
        
        Args:
            articles: 新闻列表
        
        Returns:
            dict: {
                'score': -100到+100的评分,
                'positive': 正面新闻数,
                'negative': 负面新闻数,
                'neutral': 中性新闻数,
                'total': 总新闻数,
                'sentiment': '正面'/'负面'/'中性',
                'confidence': 0-1的置信度
            }
        """
        if not articles:
            return {
                'score': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'total': 0,
                'sentiment': '中性',
                'confidence': 0
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in articles:
            # 合并标题和描述
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            # 计算正面和负面关键词数量
            pos_score = sum(1 for word in self.positive_keywords if word in text)
            neg_score = sum(1 for word in self.negative_keywords if word in text)
            
            # 判断情绪
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(articles)
        
        # 计算综合评分 (-100 到 +100)
        if total > 0:
            score = ((positive_count - negative_count) / total) * 100
        else:
            score = 0
        
        # 判断整体情绪
        if score > 20:
            sentiment = '正面'
        elif score < -20:
            sentiment = '负面'
        else:
            sentiment = '中性'
        
        # 计算置信度 (基于新闻数量)
        confidence = min(total / 50, 1.0)  # 50条新闻达到最高置信度
        
        return {
            'score': round(score, 2),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count,
            'total': total,
            'sentiment': sentiment,
            'confidence': round(confidence, 2)
        }
    
    def get_risk_adjustment(self, sentiment_score: float) -> float:
        """
        根据新闻情绪调整风险系数
        
        Args:
            sentiment_score: 情绪评分 (-100到+100)
        
        Returns:
            float: 风险调整系数
                - < -50: 1.5 (高风险,建议减仓)
                - -50 ~ -20: 1.2 (偏高风险)
                - -20 ~ 20: 1.0 (正常)
                - 20 ~ 50: 0.9 (偏低风险)
                - > 50: 0.8 (低风险,可增仓)
        """
        if sentiment_score < -50:
            return 1.5  # 极度负面,提高风险权重
        elif sentiment_score < -20:
            return 1.2  # 偏负面
        elif sentiment_score > 50:
            return 0.8  # 极度正面,降低风险权重
        elif sentiment_score > 20:
            return 0.9  # 偏正面
        else:
            return 1.0  # 中性
    
    def get_news_summary(self, symbol: str, days: int = 7) -> Dict:
        """
        获取新闻摘要(包含情绪分析)
        
        Args:
            symbol: 股票代码
            days: 回溯天数
        
        Returns:
            dict: 包含新闻和情绪分析的完整摘要
        """
        articles = self.get_recent_news(symbol, days)
        sentiment = self.calculate_sentiment_score(articles)
        risk_adjustment = self.get_risk_adjustment(sentiment['score'])
        
        # 提取最新3条新闻标题
        latest_headlines = [
            {
                'title': article['title'][:80],
                'source': article['source'],
                'time': article['publishedAt']
            }
            for article in articles[:3]
        ]
        
        # 计算置信度 (基于新闻数量)
        confidence = min(100, len(articles) * 2)  # 50条新闻 = 100%置信度
        
        return {
            'symbol': symbol,
            'days': days,
            'sentiment': sentiment,
            'risk_adjustment': risk_adjustment,
            'confidence': confidence,
            'latest_headlines': latest_headlines,
            'recommendation': self._get_recommendation(sentiment['score'], risk_adjustment)
        }
    
    def _get_recommendation(self, score: float, risk_adj: float) -> str:
        """根据情绪评分生成建议"""
        if score > 50:
            return f"新闻情绪极度正面(+{score:.0f}),市场乐观,可考虑增仓"
        elif score > 20:
            return f"新闻情绪偏正面(+{score:.0f}),市场稳定,建议持有"
        elif score > -20:
            return f"新闻情绪中性({score:.0f}),市场观望,维持当前仓位"
        elif score > -50:
            return f"新闻情绪偏负面({score:.0f}),注意风险,考虑减仓"
        else:
            return f"新闻情绪极度负面({score:.0f}),高风险,建议大幅减仓或离场"


# 测试代码
if __name__ == "__main__":
    print("=" * 80)
    print("📰 NewsAPI 新闻情绪分析测试")
    print("=" * 80)
    print()
    
    try:
        manager = NewsManager()
        
        # 测试NVDA
        print("[测试 1/3] NVDA 新闻情绪分析")
        print("-" * 80)
        summary = manager.get_news_summary('NVDA', days=7)
        
        print(f"股票: {summary['symbol']}")
        print(f"时间范围: 最近{summary['days']}天")
        print()
        print("情绪分析:")
        print(f"  综合评分: {summary['sentiment']['score']}/100")
        print(f"  情绪倾向: {summary['sentiment']['sentiment']}")
        print(f"  正面新闻: {summary['sentiment']['positive']} 条")
        print(f"  负面新闻: {summary['sentiment']['negative']} 条")
        print(f"  中性新闻: {summary['sentiment']['neutral']} 条")
        print(f"  置信度: {summary['sentiment']['confidence']*100:.0f}%")
        print()
        print(f"风险调整: {summary['risk_adjustment']}x")
        print(f"建议: {summary['recommendation']}")
        print()
        
        if summary['latest_headlines']:
            print("最新新闻:")
            for i, headline in enumerate(summary['latest_headlines'], 1):
                print(f"  {i}. {headline['title']}")
                print(f"     来源: {headline['source']} | 时间: {headline['time']}")
        
        print()
        print("✅ 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print()
    print("=" * 80)
