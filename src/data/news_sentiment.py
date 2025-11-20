"""
新闻情绪分析数据源
支持从多个来源获取实时新闻并进行情绪分析
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class NewsAPIProvider:
    """
    NewsAPI新闻数据源
    免费API Key申请: https://newsapi.org/
    免费版限制: 100次请求/天, 延迟最多1小时
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_stock_news(self, symbol: str, days_back: int = 7) -> List[Dict]:
        """获取股票相关新闻"""
        if not self.api_key:
            raise ValueError("NewsAPI Key未配置,请设置环境变量NEWS_API_KEY")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/everything"
        params = {
            'q': f"{symbol} stock OR {symbol} shares",
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'publishedAt',
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                return [
                    {
                        'source': article['source']['name'],
                        'title': article['title'],
                        'description': article.get('description', ''),
                        'url': article['url'],
                        'published_at': article['publishedAt'],
                        'content': article.get('content', '')
                    }
                    for article in articles
                ]
            return []
        except Exception as e:
            print(f"NewsAPI获取失败: {e}")
            return []


class FinnhubNewsProvider:
    """
    Finnhub新闻数据源
    免费API Key申请: https://finnhub.io/
    免费版限制: 60次请求/分钟
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        self.base_url = "https://finnhub.io/api/v1"
        
    def fetch_company_news(self, symbol: str, days_back: int = 30) -> List[Dict]:
        """获取公司新闻"""
        if not self.api_key:
            raise ValueError("Finnhub API Key未配置,请设置环境变量FINNHUB_API_KEY")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/company-news"
        params = {
            'symbol': symbol,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'token': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()
            
            return [
                {
                    'source': article.get('source', 'Finnhub'),
                    'headline': article['headline'],
                    'summary': article.get('summary', ''),
                    'url': article['url'],
                    'datetime': datetime.fromtimestamp(article['datetime']).isoformat(),
                    'related': article.get('related', symbol)
                }
                for article in articles
            ]
        except Exception as e:
            print(f"Finnhub新闻获取失败: {e}")
            return []
    
    def fetch_market_news(self, category: str = 'general') -> List[Dict]:
        """获取市场新闻
        category: general, forex, crypto, merger
        """
        if not self.api_key:
            raise ValueError("Finnhub API Key未配置")
        
        url = f"{self.base_url}/news"
        params = {
            'category': category,
            'token': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Finnhub市场新闻获取失败: {e}")
            return []


class SentimentAnalyzer:
    """
    情绪分析器
    使用简单的关键词分析(可后续升级为BERT等深度学习模型)
    """
    POSITIVE_KEYWORDS = {
        'surge', 'soar', 'rally', 'gain', 'rise', 'up', 'high', 'beat', 
        'outperform', 'profit', 'growth', 'bullish', 'strong', 'positive',
        'upgrade', 'buy', 'acquisition', 'innovation', 'breakthrough'
    }
    
    NEGATIVE_KEYWORDS = {
        'plunge', 'crash', 'fall', 'drop', 'down', 'low', 'miss', 
        'underperform', 'loss', 'decline', 'bearish', 'weak', 'negative',
        'downgrade', 'sell', 'lawsuit', 'investigation', 'scandal', 'crisis'
    }
    
    def analyze_text(self, text: str) -> Dict:
        """分析文本情绪"""
        if not text:
            return {'score': 0, 'sentiment': 'neutral'}
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        # 计算情绪得分 (-1到1之间)
        total = positive_count + negative_count
        if total == 0:
            score = 0
        else:
            score = (positive_count - negative_count) / total
        
        # 分类
        if score > 0.3:
            sentiment = 'positive'
        elif score < -0.3:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'score': round(score, 3),
            'sentiment': sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def analyze_news_batch(self, news_list: List[Dict]) -> pd.DataFrame:
        """批量分析新闻情绪"""
        results = []
        
        for news in news_list:
            text = f"{news.get('title', '')} {news.get('headline', '')} {news.get('description', '')} {news.get('summary', '')}"
            sentiment_result = self.analyze_text(text)
            
            results.append({
                'source': news.get('source', ''),
                'title': news.get('title') or news.get('headline', ''),
                'url': news.get('url', ''),
                'published_at': news.get('published_at') or news.get('datetime', ''),
                'sentiment_score': sentiment_result['score'],
                'sentiment': sentiment_result['sentiment'],
                'positive_words': sentiment_result['positive_count'],
                'negative_words': sentiment_result['negative_count']
            })
        
        return pd.DataFrame(results)
    
    def get_overall_sentiment(self, news_df: pd.DataFrame) -> Dict:
        """计算整体情绪指标"""
        if news_df.empty:
            return {
                'avg_score': 0,
                'sentiment': 'neutral',
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0,
                'total_news': 0
            }
        
        sentiment_counts = news_df['sentiment'].value_counts()
        total = len(news_df)
        
        return {
            'avg_score': round(news_df['sentiment_score'].mean(), 3),
            'sentiment': 'positive' if news_df['sentiment_score'].mean() > 0.2 else 
                        ('negative' if news_df['sentiment_score'].mean() < -0.2 else 'neutral'),
            'positive_ratio': round(sentiment_counts.get('positive', 0) / total, 3),
            'negative_ratio': round(sentiment_counts.get('negative', 0) / total, 3),
            'neutral_ratio': round(sentiment_counts.get('neutral', 0) / total, 3),
            'total_news': total
        }


class NewsDataManager:
    """新闻数据管理器"""
    def __init__(self):
        self.newsapi = None
        self.finnhub = None
        self.analyzer = SentimentAnalyzer()
        
        # 尝试初始化各个数据源
        try:
            self.newsapi = NewsAPIProvider()
        except:
            print("⚠️ NewsAPI未配置")
        
        try:
            self.finnhub = FinnhubNewsProvider()
        except:
            print("⚠️ Finnhub未配置")
    
    def get_stock_sentiment(self, symbol: str, days_back: int = 7) -> Dict:
        """获取股票情绪分析(多数据源聚合)"""
        all_news = []
        
        # 从NewsAPI获取
        if self.newsapi:
            try:
                news = self.newsapi.fetch_stock_news(symbol, days_back)
                all_news.extend(news)
                print(f"✓ NewsAPI获取到{len(news)}条新闻")
            except Exception as e:
                print(f"✗ NewsAPI失败: {e}")
        
        # 从Finnhub获取
        if self.finnhub:
            try:
                news = self.finnhub.fetch_company_news(symbol, days_back)
                all_news.extend(news)
                print(f"✓ Finnhub获取到{len(news)}条新闻")
            except Exception as e:
                print(f"✗ Finnhub失败: {e}")
        
        if not all_news:
            return {
                'symbol': symbol,
                'overall_sentiment': self.analyzer.get_overall_sentiment(pd.DataFrame()),
                'news_df': pd.DataFrame(),
                'error': '无法获取新闻数据'
            }
        
        # 情绪分析
        news_df = self.analyzer.analyze_news_batch(all_news)
        overall = self.analyzer.get_overall_sentiment(news_df)
        
        return {
            'symbol': symbol,
            'overall_sentiment': overall,
            'news_df': news_df,
            'total_sources': sum([1 for p in [self.newsapi, self.finnhub] if p])
        }


if __name__ == "__main__":
    # 测试代码
    manager = NewsDataManager()
    
    # 测试TSLA新闻情绪
    result = manager.get_stock_sentiment('TSLA', days_back=7)
    
    print(f"\n{'='*60}")
    print(f"股票: {result['symbol']}")
    print(f"{'='*60}")
    
    sentiment = result['overall_sentiment']
    print(f"\n整体情绪: {sentiment['sentiment'].upper()}")
    print(f"平均得分: {sentiment['avg_score']}")
    print(f"正面新闻: {sentiment['positive_ratio']*100:.1f}%")
    print(f"负面新闻: {sentiment['negative_ratio']*100:.1f}%")
    print(f"中性新闻: {sentiment['neutral_ratio']*100:.1f}%")
    print(f"新闻总数: {sentiment['total_news']}")
    
    if not result['news_df'].empty:
        print(f"\n最新5条新闻:")
        for idx, row in result['news_df'].head(5).iterrows():
            print(f"\n[{row['sentiment'].upper()}] {row['title'][:80]}")
            print(f"来源: {row['source']} | 得分: {row['sentiment_score']}")
