"""
内部人交易数据源
追踪公司高管和内部人的股票买卖行为
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class SECEdgarProvider:
    """
    SEC EDGAR内部人交易数据源
    使用SEC官方API,无需API Key,但需遵守访问限制
    """
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'QuantTrading qsswgl@gmail.com',  # SEC要求提供联系方式
            'Accept-Encoding': 'gzip, deflate'
        }
    
    def get_cik_by_ticker(self, ticker: str) -> Optional[str]:
        """通过股票代码获取CIK(公司识别号)"""
        url = f"{self.base_url}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'ticker': ticker,
            'output': 'xml'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 简单解析XML获取CIK
            import re
            cik_match = re.search(r'<CIK>(\d+)</CIK>', response.text)
            if cik_match:
                return cik_match.group(1).zfill(10)  # 补齐到10位
            return None
        except Exception as e:
            print(f"CIK获取失败: {e}")
            return None
    
    def get_insider_transactions(self, ticker: str, transaction_type: str = 'all') -> pd.DataFrame:
        """获取内部人交易记录
        transaction_type: 'all', 'purchase', 'sale'
        """
        cik = self.get_cik_by_ticker(ticker)
        if not cik:
            return pd.DataFrame()
        
        url = f"{self.base_url}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': cik,
            'type': '4',  # Form 4是内部人交易报告
            'dateb': '',
            'owner': 'only',
            'count': 100,
            'output': 'xml'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 这里需要解析XML数据
            # 由于XML解析较复杂,这里提供简化版本
            # 实际应用中建议使用专门的SEC数据包如sec-edgar-downloader
            
            return pd.DataFrame({
                'notice': ['SEC EDGAR数据需要复杂的XML解析,建议使用sec-api.io或OpenInsider']
            })
        except Exception as e:
            print(f"内部人交易获取失败: {e}")
            return pd.DataFrame()


class OpenInsiderProvider:
    """
    OpenInsider数据源(网页爬取)
    免费,但需要遵守爬虫规范
    """
    def __init__(self):
        self.base_url = "http://openinsider.com"
    
    def get_insider_purchases(self, ticker: str, days: int = 90) -> pd.DataFrame:
        """获取内部人购买记录"""
        url = f"{self.base_url}/screener"
        params = {
            's': ticker,
            'pl': '',  # 最小价格
            'ph': '',  # 最大价格
            'll': '',  # 最小股数
            'lh': '',  # 最大股数
            'fd': days,  # 天数
            'fdr': '',
            'td': '0',  # 交易类型:0=购买
            'tdr': '',
            'fdlyl': '',
            'fdlyh': '',
            'daysago': '',
            'xp': '1',
            'vl': '',
            'vh': '',
            'ocl': '',
            'och': '',
            'sic1': '-1',
            'sicl': '100',
            'sich': '9999',
            'grp': '0',
            'nfl': '',
            'nfh': '',
            'nil': '',
            'nih': '',
            'nol': '',
            'noh': '',
            'v2l': '',
            'v2h': '',
            'oc2l': '',
            'oc2h': '',
            'sortcol': '0',
            'cnt': '100',
            'page': '1'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 使用pandas读取HTML表格
            tables = pd.read_html(response.text)
            if tables:
                df = tables[0]
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"OpenInsider数据获取失败: {e}")
            return pd.DataFrame()


class FinancialModelingPrepInsiderProvider:
    """
    Financial Modeling Prep内部人交易数据
    需要API Key
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        self.base_url = "https://financialmodelingprep.com/api/v4"
    
    def get_insider_trading(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """获取内部人交易"""
        if not self.api_key:
            raise ValueError("FMP API Key未配置")
        
        url = f"{self.base_url}/insider-trading"
        params = {
            'symbol': symbol,
            'limit': limit,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            if not df.empty:
                # 选择关键列
                key_columns = [
                    'filingDate', 'transactionDate', 'reportingName', 
                    'typeOfOwner', 'transactionType', 'securitiesTransacted',
                    'price', 'securityName'
                ]
                df = df[[col for col in key_columns if col in df.columns]]
            
            return df
        except Exception as e:
            print(f"FMP内部人交易获取失败: {e}")
            return pd.DataFrame()
    
    def get_insider_roster(self, symbol: str) -> pd.DataFrame:
        """获取内部人名单"""
        if not self.api_key:
            raise ValueError("FMP API Key未配置")
        
        url = f"{self.base_url}/insider-roaster"
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"FMP内部人名单获取失败: {e}")
            return pd.DataFrame()


class InsiderTradingAnalyzer:
    """内部人交易分析器"""
    
    @staticmethod
    def calculate_insider_sentiment(df: pd.DataFrame) -> Dict:
        """计算内部人交易情绪"""
        if df.empty:
            return {
                'total_transactions': 0,
                'buy_count': 0,
                'sell_count': 0,
                'buy_ratio': 0,
                'net_shares': 0,
                'net_value': 0,
                'sentiment': 'neutral'
            }
        
        # 识别买入和卖出交易
        # 不同数据源的列名可能不同,需要灵活处理
        buy_keywords = ['purchase', 'buy', 'p - purchase', 'p']
        sell_keywords = ['sale', 'sell', 's - sale', 's']
        
        buy_count = 0
        sell_count = 0
        net_shares = 0
        net_value = 0
        
        if 'transactionType' in df.columns:
            for _, row in df.iterrows():
                trans_type = str(row['transactionType']).lower()
                shares = row.get('securitiesTransacted', 0)
                price = row.get('price', 0)
                
                if any(keyword in trans_type for keyword in buy_keywords):
                    buy_count += 1
                    net_shares += shares
                    net_value += shares * price
                elif any(keyword in trans_type for keyword in sell_keywords):
                    sell_count += 1
                    net_shares -= shares
                    net_value -= shares * price
        
        total = buy_count + sell_count
        buy_ratio = buy_count / total if total > 0 else 0
        
        # 情绪判断
        if buy_ratio > 0.7:
            sentiment = 'very_bullish'
        elif buy_ratio > 0.55:
            sentiment = 'bullish'
        elif buy_ratio < 0.3:
            sentiment = 'very_bearish'
        elif buy_ratio < 0.45:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'
        
        return {
            'total_transactions': total,
            'buy_count': buy_count,
            'sell_count': sell_count,
            'buy_ratio': round(buy_ratio, 3),
            'net_shares': int(net_shares),
            'net_value': round(net_value, 2),
            'sentiment': sentiment
        }
    
    @staticmethod
    def identify_significant_trades(df: pd.DataFrame, threshold_value: float = 1000000) -> pd.DataFrame:
        """识别重大交易(超过阈值的交易)"""
        if df.empty:
            return df
        
        if 'securitiesTransacted' in df.columns and 'price' in df.columns:
            df['trade_value'] = df['securitiesTransacted'] * df['price']
            significant = df[df['trade_value'] >= threshold_value].copy()
            return significant.sort_values('trade_value', ascending=False)
        
        return pd.DataFrame()
    
    @staticmethod
    def analyze_insider_trends(df: pd.DataFrame, window_days: int = 30) -> Dict:
        """分析内部人交易趋势"""
        if df.empty:
            return {}
        
        # 按时间窗口分组统计
        if 'transactionDate' in df.columns:
            df['transactionDate'] = pd.to_datetime(df['transactionDate'])
            cutoff_date = datetime.now() - timedelta(days=window_days)
            recent_trades = df[df['transactionDate'] >= cutoff_date]
            
            recent_sentiment = InsiderTradingAnalyzer.calculate_insider_sentiment(recent_trades)
            all_sentiment = InsiderTradingAnalyzer.calculate_insider_sentiment(df)
            
            return {
                'recent_period': f'{window_days}天',
                'recent_sentiment': recent_sentiment,
                'overall_sentiment': all_sentiment,
                'trend': 'increasing' if recent_sentiment['buy_ratio'] > all_sentiment['buy_ratio'] 
                        else 'decreasing'
            }
        
        return {}


class InsiderDataManager:
    """内部人交易数据管理器"""
    def __init__(self):
        self.sec = SECEdgarProvider()
        self.openinsider = OpenInsiderProvider()
        self.fmp = None
        
        try:
            self.fmp = FinancialModelingPrepInsiderProvider()
        except:
            print("⚠️ FMP内部人交易未配置")
    
    def get_insider_analysis(self, symbol: str, days: int = 90) -> Dict:
        """获取内部人交易综合分析"""
        result = {
            'symbol': symbol,
            'transactions': pd.DataFrame(),
            'sentiment': {},
            'significant_trades': pd.DataFrame(),
            'trends': {},
            'source': None
        }
        
        # 优先使用FMP(数据最完整)
        if self.fmp:
            try:
                print("使用FMP获取内部人交易数据...")
                df = self.fmp.get_insider_trading(symbol, limit=100)
                if not df.empty:
                    result['transactions'] = df
                    result['source'] = 'FMP'
            except Exception as e:
                print(f"FMP获取失败: {e}")
        
        # 备用OpenInsider
        if result['transactions'].empty:
            try:
                print("使用OpenInsider获取内部人交易数据...")
                df = self.openinsider.get_insider_purchases(symbol, days)
                if not df.empty:
                    result['transactions'] = df
                    result['source'] = 'OpenInsider'
            except Exception as e:
                print(f"OpenInsider获取失败: {e}")
        
        # 分析交易数据
        if not result['transactions'].empty:
            analyzer = InsiderTradingAnalyzer()
            result['sentiment'] = analyzer.calculate_insider_sentiment(result['transactions'])
            result['significant_trades'] = analyzer.identify_significant_trades(result['transactions'])
            result['trends'] = analyzer.analyze_insider_trends(result['transactions'])
        
        return result


if __name__ == "__main__":
    # 测试代码
    manager = InsiderDataManager()
    
    print(f"\n{'='*60}")
    print("获取TSLA内部人交易数据...")
    print(f"{'='*60}")
    
    analysis = manager.get_insider_analysis('TSLA', days=90)
    
    print(f"\n数据来源: {analysis['source']}")
    
    if not analysis['transactions'].empty:
        print(f"\n【交易记录】")
        print(f"记录总数: {len(analysis['transactions'])}")
        
        if analysis['sentiment']:
            sentiment = analysis['sentiment']
            print(f"\n【内部人情绪】")
            print(f"总交易次数: {sentiment['total_transactions']}")
            print(f"买入次数: {sentiment['buy_count']}")
            print(f"卖出次数: {sentiment['sell_count']}")
            print(f"买入比例: {sentiment['buy_ratio']*100:.1f}%")
            print(f"净股数: {sentiment['net_shares']:,}")
            print(f"净价值: ${sentiment['net_value']:,.2f}")
            print(f"情绪: {sentiment['sentiment'].upper()}")
        
        if not analysis['significant_trades'].empty:
            print(f"\n【重大交易】(>$1M)")
            print(f"重大交易数量: {len(analysis['significant_trades'])}")
        
        if analysis['trends']:
            trends = analysis['trends']
            print(f"\n【趋势分析】")
            print(f"分析周期: {trends['recent_period']}")
            print(f"趋势: {trends['trend'].upper()}")
    else:
        print("\n⚠️ 无法获取内部人交易数据")
