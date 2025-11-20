"""
社交媒体情绪数据源
分析Reddit、Twitter(X)、StockTwits等平台的投资者情绪
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re


class RedditSentimentProvider:
    """
    Reddit情绪分析数据源
    免费API,无需API Key
    使用pushshift.io或Reddit官方API
    """
    def __init__(self):
        # 使用Reddit JSON API(无需认证)
        self.base_url = "https://www.reddit.com"
    
    def get_wallstreetbets_posts(self, symbol: str, limit: int = 100) -> List[Dict]:
        """获取WallStreetBets板块的股票讨论"""
        subreddit = "wallstreetbets"
        url = f"{self.base_url}/r/{subreddit}/search.json"
        
        params = {
            'q': symbol,
            'restrict_sr': 1,
            'limit': limit,
            'sort': 'new'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for post in data.get('data', {}).get('children', []):
                post_data = post['data']
                posts.append({
                    'title': post_data['title'],
                    'text': post_data.get('selftext', ''),
                    'score': post_data['score'],
                    'num_comments': post_data['num_comments'],
                    'created_utc': datetime.fromtimestamp(post_data['created_utc']),
                    'url': f"https://www.reddit.com{post_data['permalink']}"
                })
            
            return posts
        except Exception as e:
            print(f"Reddit数据获取失败: {e}")
            return []
    
    def get_stock_subreddit_posts(self, symbol: str, limit: int = 50) -> List[Dict]:
        """获取股票专属板块的讨论"""
        subreddit = f"{symbol.lower()}"  # 很多股票有专属板块,如tsla
        url = f"{self.base_url}/r/{subreddit}/hot.json"
        
        params = {'limit': limit}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for post in data.get('data', {}).get('children', []):
                post_data = post['data']
                posts.append({
                    'title': post_data['title'],
                    'text': post_data.get('selftext', ''),
                    'score': post_data['score'],
                    'num_comments': post_data['num_comments'],
                    'created_utc': datetime.fromtimestamp(post_data['created_utc']),
                    'url': f"https://www.reddit.com{post_data['permalink']}"
                })
            
            return posts
        except Exception as e:
            # 如果没有专属板块,返回空列表
            return []


class StockTwitsProvider:
    """
    StockTwits情绪数据源
    免费API,无需API Key
    """
    def __init__(self):
        self.base_url = "https://api.stocktwits.com/api/2"
    
    def get_streams(self, symbol: str, limit: int = 30) -> List[Dict]:
        """获取股票讨论流"""
        url = f"{self.base_url}/streams/symbol/{symbol}.json"
        params = {'limit': limit}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            messages = []
            for msg in data.get('messages', []):
                sentiment = msg.get('entities', {}).get('sentiment', {})
                
                messages.append({
                    'id': msg['id'],
                    'body': msg['body'],
                    'created_at': datetime.strptime(msg['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                    'sentiment': sentiment.get('basic') if sentiment else None,
                    'likes': msg.get('likes', {}).get('total', 0),
                    'user': msg['user']['username']
                })
            
            return messages
        except Exception as e:
            print(f"StockTwits数据获取失败: {e}")
            return []
    
    def get_trending(self) -> List[Dict]:
        """获取热门股票"""
        url = f"{self.base_url}/trending/symbols.json"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('symbols', [])
        except Exception as e:
            print(f"StockTwits热门股票获取失败: {e}")
            return []


class SocialSentimentAnalyzer:
    """社交媒体情绪分析器"""
    
    # 情绪关键词
    BULLISH_KEYWORDS = {
        'moon', 'rocket', 'bull', 'calls', 'buy', 'long', 'hold', 'diamond hands',
        'to the moon', 'bullish', 'pump', 'rally', 'tendies', 'stonks'
    }
    
    BEARISH_KEYWORDS = {
        'bear', 'puts', 'sell', 'short', 'dump', 'crash', 'bearish', 
        'bubble', 'overvalued', 'rug pull'
    }
    
    @staticmethod
    def analyze_text_sentiment(text: str) -> Dict:
        """分析文本情绪"""
        text_lower = text.lower()
        
        bullish_count = sum(1 for word in SocialSentimentAnalyzer.BULLISH_KEYWORDS 
                           if word in text_lower)
        bearish_count = sum(1 for word in SocialSentimentAnalyzer.BEARISH_KEYWORDS 
                           if word in text_lower)
        
        total = bullish_count + bearish_count
        if total == 0:
            score = 0
            sentiment = 'neutral'
        else:
            score = (bullish_count - bearish_count) / total
            if score > 0.3:
                sentiment = 'bullish'
            elif score < -0.3:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
        
        return {
            'score': round(score, 3),
            'sentiment': sentiment,
            'bullish_words': bullish_count,
            'bearish_words': bearish_count
        }
    
    @staticmethod
    def analyze_reddit_posts(posts: List[Dict]) -> pd.DataFrame:
        """分析Reddit帖子情绪"""
        results = []
        
        for post in posts:
            text = f"{post['title']} {post.get('text', '')}"
            sentiment = SocialSentimentAnalyzer.analyze_text_sentiment(text)
            
            results.append({
                'title': post['title'][:100],
                'score': post['score'],
                'comments': post['num_comments'],
                'created': post['created_utc'],
                'sentiment': sentiment['sentiment'],
                'sentiment_score': sentiment['score'],
                'url': post['url']
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def analyze_stocktwits_messages(messages: List[Dict]) -> pd.DataFrame:
        """分析StockTwits消息情绪"""
        results = []
        
        for msg in messages:
            # StockTwits已经提供了情绪标签
            if msg.get('sentiment'):
                sentiment = msg['sentiment']
                score = 1 if sentiment == 'Bullish' else -1
            else:
                # 如果没有标签,使用关键词分析
                analysis = SocialSentimentAnalyzer.analyze_text_sentiment(msg['body'])
                sentiment = analysis['sentiment']
                score = analysis['score']
            
            results.append({
                'body': msg['body'][:100],
                'user': msg['user'],
                'likes': msg['likes'],
                'created': msg['created_at'],
                'sentiment': sentiment,
                'sentiment_score': score
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def calculate_social_metrics(df: pd.DataFrame) -> Dict:
        """计算社交媒体指标"""
        if df.empty:
            return {
                'total_posts': 0,
                'bullish_ratio': 0,
                'bearish_ratio': 0,
                'neutral_ratio': 0,
                'avg_sentiment_score': 0,
                'engagement_score': 0,
                'overall_sentiment': 'neutral'
            }
        
        total = len(df)
        sentiment_counts = df['sentiment'].value_counts()
        
        # 计算各情绪比例
        bullish_ratio = sentiment_counts.get('bullish', sentiment_counts.get('Bullish', 0)) / total
        bearish_ratio = sentiment_counts.get('bearish', sentiment_counts.get('Bearish', 0)) / total
        neutral_ratio = sentiment_counts.get('neutral', 0) / total
        
        # 平均情绪得分
        avg_score = df['sentiment_score'].mean()
        
        # 互动分数(基于点赞/评论数)
        if 'score' in df.columns:
            engagement = df['score'].sum()
        elif 'likes' in df.columns:
            engagement = df['likes'].sum()
        else:
            engagement = 0
        
        # 综合判断
        if avg_score > 0.3 or bullish_ratio > 0.6:
            overall = 'bullish'
        elif avg_score < -0.3 or bearish_ratio > 0.6:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        return {
            'total_posts': total,
            'bullish_ratio': round(bullish_ratio, 3),
            'bearish_ratio': round(bearish_ratio, 3),
            'neutral_ratio': round(neutral_ratio, 3),
            'avg_sentiment_score': round(avg_score, 3),
            'engagement_score': int(engagement),
            'overall_sentiment': overall
        }


class SocialMediaDataManager:
    """社交媒体数据管理器"""
    def __init__(self):
        self.reddit = RedditSentimentProvider()
        self.stocktwits = StockTwitsProvider()
        self.analyzer = SocialSentimentAnalyzer()
    
    def get_social_sentiment(self, symbol: str) -> Dict:
        """获取综合社交媒体情绪"""
        result = {
            'symbol': symbol,
            'reddit_data': pd.DataFrame(),
            'stocktwits_data': pd.DataFrame(),
            'reddit_metrics': {},
            'stocktwits_metrics': {},
            'combined_metrics': {}
        }
        
        # 获取Reddit数据
        try:
            wsb_posts = self.reddit.get_wallstreetbets_posts(symbol)
            stock_posts = self.reddit.get_stock_subreddit_posts(symbol)
            all_reddit_posts = wsb_posts + stock_posts
            
            if all_reddit_posts:
                result['reddit_data'] = self.analyzer.analyze_reddit_posts(all_reddit_posts)
                result['reddit_metrics'] = self.analyzer.calculate_social_metrics(
                    result['reddit_data']
                )
                print(f"✓ Reddit获取到{len(all_reddit_posts)}条帖子")
        except Exception as e:
            print(f"✗ Reddit获取失败: {e}")
        
        # 获取StockTwits数据
        try:
            messages = self.stocktwits.get_streams(symbol)
            if messages:
                result['stocktwits_data'] = self.analyzer.analyze_stocktwits_messages(messages)
                result['stocktwits_metrics'] = self.analyzer.calculate_social_metrics(
                    result['stocktwits_data']
                )
                print(f"✓ StockTwits获取到{len(messages)}条消息")
        except Exception as e:
            print(f"✗ StockTwits获取失败: {e}")
        
        # 合并指标
        if result['reddit_metrics'] and result['stocktwits_metrics']:
            reddit_m = result['reddit_metrics']
            stocktwits_m = result['stocktwits_metrics']
            
            # 加权平均(Reddit权重60%,StockTwits权重40%)
            total_posts = reddit_m['total_posts'] + stocktwits_m['total_posts']
            reddit_weight = reddit_m['total_posts'] / total_posts if total_posts > 0 else 0.5
            stocktwits_weight = 1 - reddit_weight
            
            combined_score = (reddit_m['avg_sentiment_score'] * reddit_weight + 
                            stocktwits_m['avg_sentiment_score'] * stocktwits_weight)
            
            combined_bullish = (reddit_m['bullish_ratio'] * reddit_weight + 
                               stocktwits_m['bullish_ratio'] * stocktwits_weight)
            
            result['combined_metrics'] = {
                'total_posts': total_posts,
                'avg_sentiment_score': round(combined_score, 3),
                'bullish_ratio': round(combined_bullish, 3),
                'overall_sentiment': 'bullish' if combined_score > 0.3 else 
                                   ('bearish' if combined_score < -0.3 else 'neutral'),
                'reddit_weight': round(reddit_weight, 2),
                'stocktwits_weight': round(stocktwits_weight, 2)
            }
        
        return result


if __name__ == "__main__":
    # 测试代码
    manager = SocialMediaDataManager()
    
    print(f"\n{'='*60}")
    print("获取TSLA社交媒体情绪...")
    print(f"{'='*60}")
    
    result = manager.get_social_sentiment('TSLA')
    
    if result['reddit_metrics']:
        print(f"\n【Reddit情绪】")
        metrics = result['reddit_metrics']
        print(f"帖子总数: {metrics['total_posts']}")
        print(f"看涨比例: {metrics['bullish_ratio']*100:.1f}%")
        print(f"看跌比例: {metrics['bearish_ratio']*100:.1f}%")
        print(f"平均情绪: {metrics['avg_sentiment_score']:.3f}")
        print(f"互动分数: {metrics['engagement_score']:,}")
        print(f"整体情绪: {metrics['overall_sentiment'].upper()}")
    
    if result['stocktwits_metrics']:
        print(f"\n【StockTwits情绪】")
        metrics = result['stocktwits_metrics']
        print(f"消息总数: {metrics['total_posts']}")
        print(f"看涨比例: {metrics['bullish_ratio']*100:.1f}%")
        print(f"看跌比例: {metrics['bearish_ratio']*100:.1f}%")
        print(f"整体情绪: {metrics['overall_sentiment'].upper()}")
    
    if result['combined_metrics']:
        print(f"\n【综合情绪】")
        combined = result['combined_metrics']
        print(f"总帖子数: {combined['total_posts']}")
        print(f"综合情绪得分: {combined['avg_sentiment_score']:.3f}")
        print(f"看涨比例: {combined['bullish_ratio']*100:.1f}%")
        print(f"整体情绪: {combined['overall_sentiment'].upper()}")
