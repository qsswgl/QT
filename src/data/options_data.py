"""
期权和衍生品数据源
提供期权链、隐含波动率、希腊值等数据
"""
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import time


class TradierOptionsProvider:
    """
    Tradier期权数据源
    免费沙盒API申请: https://developer.tradier.com/
    沙盒环境无限制,生产环境需付费
    """
    def __init__(self, api_key: Optional[str] = None, sandbox: bool = True):
        self.api_key = api_key or os.getenv("TRADIER_API_KEY")
        self.base_url = "https://sandbox.tradier.com" if sandbox else "https://api.tradier.com"
        self.sandbox = sandbox
    
    def get_option_chains(self, symbol: str, expiration: Optional[str] = None) -> pd.DataFrame:
        """获取期权链
        expiration: 到期日,格式YYYY-MM-DD,不指定则返回所有到期日
        """
        if not self.api_key:
            raise ValueError("Tradier API Key未配置,请设置环境变量TRADIER_API_KEY")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        
        url = f"{self.base_url}/v1/markets/options/chains"
        params = {'symbol': symbol}
        if expiration:
            params['expiration'] = expiration
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'options' in data and data['options']:
                options = data['options'].get('option', [])
                df = pd.DataFrame(options)
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Tradier期权链获取失败: {e}")
            return pd.DataFrame()
    
    def get_option_expirations(self, symbol: str) -> List[str]:
        """获取所有可用的期权到期日"""
        if not self.api_key:
            raise ValueError("Tradier API Key未配置")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        
        url = f"{self.base_url}/v1/markets/options/expirations"
        params = {'symbol': symbol}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'expirations' in data and data['expirations']:
                return data['expirations'].get('date', [])
            return []
        except Exception as e:
            print(f"Tradier到期日获取失败: {e}")
            return []
    
    def get_option_quote(self, symbols: List[str]) -> pd.DataFrame:
        """获取期权实时报价
        symbols: 期权代码列表,例如['TSLA250117C00300000']
        """
        if not self.api_key:
            raise ValueError("Tradier API Key未配置")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        
        url = f"{self.base_url}/v1/markets/quotes"
        params = {'symbols': ','.join(symbols)}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'quotes' in data and data['quotes']:
                quotes = data['quotes'].get('quote', [])
                if isinstance(quotes, dict):  # 单个报价
                    quotes = [quotes]
                return pd.DataFrame(quotes)
            return pd.DataFrame()
        except Exception as e:
            print(f"Tradier期权报价获取失败: {e}")
            return pd.DataFrame()


class YahooFinanceOptionsProvider:
    """
    Yahoo Finance期权数据(免费)
    使用yfinance库
    """
    def __init__(self):
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            raise ImportError("需要安装yfinance: pip install yfinance")
    
    def get_option_chain(self, symbol: str, expiration: Optional[str] = None) -> Dict:
        """获取期权链"""
        try:
            ticker = self.yf.Ticker(symbol)
            
            # 获取所有到期日
            expirations = ticker.options
            if not expirations:
                return {'calls': pd.DataFrame(), 'puts': pd.DataFrame(), 'expirations': []}
            
            # 如果未指定到期日,使用最近的
            if not expiration:
                expiration = expirations[0]
            
            # 获取期权链
            opt_chain = ticker.option_chain(expiration)
            
            return {
                'calls': opt_chain.calls,
                'puts': opt_chain.puts,
                'expirations': list(expirations),
                'expiration_date': expiration
            }
        except Exception as e:
            print(f"Yahoo Finance期权链获取失败: {e}")
            return {'calls': pd.DataFrame(), 'puts': pd.DataFrame(), 'expirations': []}


class OptionsAnalyzer:
    """期权分析器"""
    
    @staticmethod
    def calculate_put_call_ratio(calls_df: pd.DataFrame, puts_df: pd.DataFrame) -> float:
        """计算看跌/看涨比率(Put/Call Ratio)
        高比率(>1)表明市场看跌,低比率(<1)表明市场看涨
        """
        if calls_df.empty or puts_df.empty:
            return 0
        
        # 使用成交量计算
        call_volume = calls_df.get('volume', calls_df.get('openInterest', pd.Series([0]))).sum()
        put_volume = puts_df.get('volume', puts_df.get('openInterest', pd.Series([0]))).sum()
        
        if call_volume == 0:
            return 0
        
        return put_volume / call_volume
    
    @staticmethod
    def find_max_pain(calls_df: pd.DataFrame, puts_df: pd.DataFrame) -> float:
        """计算Max Pain价格(期权卖方损失最小的行权价)"""
        if calls_df.empty or puts_df.empty:
            return 0
        
        # 获取所有行权价
        strikes = sorted(set(calls_df['strike'].tolist() + puts_df['strike'].tolist()))
        
        max_pain_price = 0
        min_pain = float('inf')
        
        for strike in strikes:
            # 计算在此行权价下的总损失
            call_pain = 0
            put_pain = 0
            
            # Call期权损失
            for _, call in calls_df.iterrows():
                if call['strike'] < strike:
                    oi = call.get('openInterest', 0)
                    call_pain += oi * (strike - call['strike'])
            
            # Put期权损失
            for _, put in puts_df.iterrows():
                if put['strike'] > strike:
                    oi = put.get('openInterest', 0)
                    put_pain += oi * (put['strike'] - strike)
            
            total_pain = call_pain + put_pain
            
            if total_pain < min_pain:
                min_pain = total_pain
                max_pain_price = strike
        
        return max_pain_price
    
    @staticmethod
    def calculate_implied_volatility_rank(current_iv: float, iv_history: List[float]) -> float:
        """计算隐含波动率排名(IV Rank)
        返回0-100,表示当前IV在历史范围内的位置
        """
        if not iv_history:
            return 50
        
        min_iv = min(iv_history)
        max_iv = max(iv_history)
        
        if max_iv == min_iv:
            return 50
        
        iv_rank = ((current_iv - min_iv) / (max_iv - min_iv)) * 100
        return round(iv_rank, 2)
    
    @staticmethod
    def analyze_options_sentiment(calls_df: pd.DataFrame, puts_df: pd.DataFrame) -> Dict:
        """分析期权市场情绪"""
        result = {
            'put_call_ratio': 0,
            'max_pain': 0,
            'sentiment': 'neutral',
            'call_volume': 0,
            'put_volume': 0,
            'call_oi': 0,
            'put_oi': 0
        }
        
        if calls_df.empty or puts_df.empty:
            return result
        
        # Put/Call比率
        pcr = OptionsAnalyzer.calculate_put_call_ratio(calls_df, puts_df)
        result['put_call_ratio'] = round(pcr, 3)
        
        # Max Pain
        result['max_pain'] = OptionsAnalyzer.find_max_pain(calls_df, puts_df)
        
        # 成交量和未平仓合约
        result['call_volume'] = int(calls_df.get('volume', pd.Series([0])).sum())
        result['put_volume'] = int(puts_df.get('volume', pd.Series([0])).sum())
        result['call_oi'] = int(calls_df.get('openInterest', pd.Series([0])).sum())
        result['put_oi'] = int(puts_df.get('openInterest', pd.Series([0])).sum())
        
        # 情绪判断
        if pcr > 1.2:
            result['sentiment'] = 'bearish'  # 看跌
        elif pcr < 0.8:
            result['sentiment'] = 'bullish'  # 看涨
        else:
            result['sentiment'] = 'neutral'  # 中性
        
        return result


class OptionsDataManager:
    """期权数据管理器"""
    def __init__(self):
        self.tradier = None
        self.yahoo = None
        
        # 尝试初始化数据源
        try:
            self.tradier = TradierOptionsProvider()
        except:
            print("⚠️ Tradier未配置")
        
        try:
            self.yahoo = YahooFinanceOptionsProvider()
        except:
            print("⚠️ Yahoo Finance Options未配置")
    
    def get_options_analysis(self, symbol: str, expiration: Optional[str] = None) -> Dict:
        """获取期权综合分析"""
        result = {
            'symbol': symbol,
            'expiration': expiration,
            'calls': pd.DataFrame(),
            'puts': pd.DataFrame(),
            'sentiment_analysis': {},
            'source': None
        }
        
        # 优先使用Tradier(数据更详细)
        if self.tradier:
            try:
                print("使用Tradier获取期权数据...")
                if not expiration:
                    expirations = self.tradier.get_option_expirations(symbol)
                    if expirations:
                        expiration = expirations[0]
                
                chains = self.tradier.get_option_chains(symbol, expiration)
                if not chains.empty:
                    result['calls'] = chains[chains['option_type'] == 'call']
                    result['puts'] = chains[chains['option_type'] == 'put']
                    result['source'] = 'Tradier'
            except Exception as e:
                print(f"Tradier获取失败,尝试备用源: {e}")
        
        # 备用Yahoo Finance
        if (result['calls'].empty or result['puts'].empty) and self.yahoo:
            try:
                print("使用Yahoo Finance获取期权数据...")
                opt_data = self.yahoo.get_option_chain(symbol, expiration)
                result['calls'] = opt_data['calls']
                result['puts'] = opt_data['puts']
                result['expiration'] = opt_data['expiration_date']
                result['source'] = 'Yahoo Finance'
            except Exception as e:
                print(f"Yahoo Finance获取失败: {e}")
        
        # 分析期权情绪
        if not result['calls'].empty and not result['puts'].empty:
            result['sentiment_analysis'] = OptionsAnalyzer.analyze_options_sentiment(
                result['calls'], result['puts']
            )
        
        return result


if __name__ == "__main__":
    # 测试代码
    manager = OptionsDataManager()
    
    print(f"\n{'='*60}")
    print("获取TSLA期权数据...")
    print(f"{'='*60}")
    
    analysis = manager.get_options_analysis('TSLA')
    
    if not analysis['calls'].empty:
        print(f"\n【期权链信息】")
        print(f"到期日: {analysis['expiration']}")
        print(f"Call期权数量: {len(analysis['calls'])}")
        print(f"Put期权数量: {len(analysis['puts'])}")
        print(f"数据来源: {analysis['source']}")
        
        if analysis['sentiment_analysis']:
            sentiment = analysis['sentiment_analysis']
            print(f"\n【期权市场情绪】")
            print(f"Put/Call比率: {sentiment['put_call_ratio']}")
            print(f"市场情绪: {sentiment['sentiment'].upper()}")
            print(f"Max Pain价格: ${sentiment['max_pain']:.2f}")
            print(f"Call成交量: {sentiment['call_volume']:,}")
            print(f"Put成交量: {sentiment['put_volume']:,}")
            print(f"Call未平仓: {sentiment['call_oi']:,}")
            print(f"Put未平仓: {sentiment['put_oi']:,}")
            
            # 解读
            print(f"\n【情绪解读】")
            pcr = sentiment['put_call_ratio']
            if pcr > 1.2:
                print("⚠️ Put/Call比率>1.2,市场偏向看跌")
            elif pcr < 0.8:
                print("✓ Put/Call比率<0.8,市场偏向看涨")
            else:
                print("○ Put/Call比率在正常范围,市场情绪中性")
    else:
        print("\n⚠️ 无法获取期权数据")
