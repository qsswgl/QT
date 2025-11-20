"""
基本面和财报数据源
提供企业财务数据、估值指标、盈利报告等
"""
import os
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import time


class FinancialModelingPrepProvider:
    """
    Financial Modeling Prep数据源
    免费API Key申请: https://site.financialmodelingprep.com/developer/docs/
    免费版限制: 250次请求/天
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
    def get_company_profile(self, symbol: str) -> Dict:
        """获取公司概况"""
        if not self.api_key:
            raise ValueError("FMP API Key未配置,请设置环境变量FMP_API_KEY")
        
        url = f"{self.base_url}/profile/{symbol}"
        params = {'apikey': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                company = data[0]
                return {
                    'symbol': company['symbol'],
                    'company_name': company['companyName'],
                    'sector': company.get('sector', ''),
                    'industry': company.get('industry', ''),
                    'market_cap': company.get('mktCap', 0),
                    'price': company.get('price', 0),
                    'beta': company.get('beta', 0),
                    'description': company.get('description', '')
                }
            return {}
        except Exception as e:
            print(f"FMP公司概况获取失败: {e}")
            return {}
    
    def get_income_statement(self, symbol: str, period: str = 'annual', limit: int = 5) -> pd.DataFrame:
        """获取利润表
        period: annual(年报) 或 quarter(季报)
        """
        if not self.api_key:
            raise ValueError("FMP API Key未配置")
        
        url = f"{self.base_url}/income-statement/{symbol}"
        params = {
            'period': period,
            'limit': limit,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            if not df.empty:
                # 选择关键指标
                key_columns = [
                    'date', 'revenue', 'grossProfit', 'operatingIncome',
                    'netIncome', 'eps', 'epsdiluted'
                ]
                df = df[[col for col in key_columns if col in df.columns]]
            
            return df
        except Exception as e:
            print(f"FMP利润表获取失败: {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, symbol: str, period: str = 'annual', limit: int = 5) -> pd.DataFrame:
        """获取资产负债表"""
        if not self.api_key:
            raise ValueError("FMP API Key未配置")
        
        url = f"{self.base_url}/balance-sheet-statement/{symbol}"
        params = {
            'period': period,
            'limit': limit,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            if not df.empty:
                key_columns = [
                    'date', 'totalAssets', 'totalLiabilities', 
                    'totalStockholdersEquity', 'cashAndCashEquivalents'
                ]
                df = df[[col for col in key_columns if col in df.columns]]
            
            return df
        except Exception as e:
            print(f"FMP资产负债表获取失败: {e}")
            return pd.DataFrame()
    
    def get_key_metrics(self, symbol: str, period: str = 'annual', limit: int = 5) -> pd.DataFrame:
        """获取关键财务指标"""
        if not self.api_key:
            raise ValueError("FMP API Key未配置")
        
        url = f"{self.base_url}/key-metrics/{symbol}"
        params = {
            'period': period,
            'limit': limit,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data)
            if not df.empty:
                key_columns = [
                    'date', 'revenuePerShare', 'netIncomePerShare', 'peRatio',
                    'priceToSalesRatio', 'pbRatio', 'debtToEquity', 'roe', 'roa'
                ]
                df = df[[col for col in key_columns if col in df.columns]]
            
            return df
        except Exception as e:
            print(f"FMP关键指标获取失败: {e}")
            return pd.DataFrame()
    
    def get_earnings_calendar(self, symbol: str) -> List[Dict]:
        """获取财报发布日历"""
        if not self.api_key:
            raise ValueError("FMP API Key未配置")
        
        url = f"{self.base_url}/historical/earning_calendar/{symbol}"
        params = {'apikey': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"FMP财报日历获取失败: {e}")
            return []


class AlphaVantageFundamentalsProvider:
    """
    Alpha Vantage基本面数据源
    使用已有的ALPHAVANTAGE_API_KEY
    免费版限制: 500次请求/天, 5次/分钟
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        self.last_call_time = 0
        self.min_interval = 12  # 12秒间隔,确保不超过5次/分钟
    
    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()
    
    def get_company_overview(self, symbol: str) -> Dict:
        """获取公司概况"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API Key未配置")
        
        self._rate_limit()
        
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'symbol': data.get('Symbol', ''),
                'name': data.get('Name', ''),
                'sector': data.get('Sector', ''),
                'industry': data.get('Industry', ''),
                'market_cap': float(data.get('MarketCapitalization', 0)),
                'pe_ratio': float(data.get('PERatio', 0)),
                'peg_ratio': float(data.get('PEGRatio', 0)),
                'dividend_yield': float(data.get('DividendYield', 0)),
                'eps': float(data.get('EPS', 0)),
                'revenue_ttm': float(data.get('RevenueTTM', 0)),
                'profit_margin': float(data.get('ProfitMargin', 0)),
                'operating_margin': float(data.get('OperatingMarginTTM', 0)),
                'roe': float(data.get('ReturnOnEquityTTM', 0)),
                'roa': float(data.get('ReturnOnAssetsTTM', 0)),
                '52week_high': float(data.get('52WeekHigh', 0)),
                '52week_low': float(data.get('52WeekLow', 0))
            }
        except Exception as e:
            print(f"Alpha Vantage公司概况获取失败: {e}")
            return {}
    
    def get_earnings(self, symbol: str) -> Dict:
        """获取盈利数据"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API Key未配置")
        
        self._rate_limit()
        
        params = {
            'function': 'EARNINGS',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'annual_earnings': pd.DataFrame(data.get('annualEarnings', [])),
                'quarterly_earnings': pd.DataFrame(data.get('quarterlyEarnings', []))
            }
        except Exception as e:
            print(f"Alpha Vantage盈利数据获取失败: {e}")
            return {'annual_earnings': pd.DataFrame(), 'quarterly_earnings': pd.DataFrame()}


class FundamentalsDataManager:
    """基本面数据管理器"""
    def __init__(self):
        self.fmp = None
        self.alphavantage = None
        
        # 尝试初始化数据源
        try:
            self.fmp = FinancialModelingPrepProvider()
        except:
            print("⚠️ Financial Modeling Prep未配置")
        
        try:
            self.alphavantage = AlphaVantageFundamentalsProvider()
        except:
            print("⚠️ Alpha Vantage基本面未配置")
    
    def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """获取综合基本面分析"""
        result = {
            'symbol': symbol,
            'company_profile': {},
            'income_statement': pd.DataFrame(),
            'balance_sheet': pd.DataFrame(),
            'key_metrics': pd.DataFrame(),
            'earnings': {},
            'source': None
        }
        
        # 优先使用FMP(数据更详细)
        if self.fmp:
            try:
                print("使用Financial Modeling Prep获取数据...")
                result['company_profile'] = self.fmp.get_company_profile(symbol)
                result['income_statement'] = self.fmp.get_income_statement(symbol)
                result['balance_sheet'] = self.fmp.get_balance_sheet(symbol)
                result['key_metrics'] = self.fmp.get_key_metrics(symbol)
                result['source'] = 'FMP'
                return result
            except Exception as e:
                print(f"FMP获取失败,尝试备用源: {e}")
        
        # 备用Alpha Vantage
        if self.alphavantage:
            try:
                print("使用Alpha Vantage获取数据...")
                result['company_profile'] = self.alphavantage.get_company_overview(symbol)
                result['earnings'] = self.alphavantage.get_earnings(symbol)
                result['source'] = 'AlphaVantage'
                return result
            except Exception as e:
                print(f"Alpha Vantage获取失败: {e}")
        
        result['source'] = 'None'
        return result
    
    def calculate_financial_health_score(self, analysis: Dict) -> Dict:
        """计算财务健康度评分(0-100)"""
        if not analysis.get('company_profile'):
            return {'score': 0, 'grade': 'N/A', 'details': '无数据'}
        
        profile = analysis['company_profile']
        score = 50  # 基准分
        details = []
        
        # PE比率评分(越低越好,合理范围10-25)
        pe_ratio = profile.get('pe_ratio', 0) or profile.get('PERatio', 0)
        if pe_ratio > 0:
            if pe_ratio < 15:
                score += 15
                details.append(f"✓ PE比率优秀({pe_ratio:.1f})")
            elif pe_ratio < 25:
                score += 10
                details.append(f"✓ PE比率良好({pe_ratio:.1f})")
            elif pe_ratio > 50:
                score -= 10
                details.append(f"✗ PE比率过高({pe_ratio:.1f})")
        
        # ROE评分(越高越好,>15%为优秀)
        roe = profile.get('roe', 0)
        if roe > 0:
            if roe > 0.15:
                score += 15
                details.append(f"✓ ROE优秀({roe*100:.1f}%)")
            elif roe > 0.10:
                score += 10
                details.append(f"✓ ROE良好({roe*100:.1f}%)")
            else:
                score += 5
                details.append(f"○ ROE一般({roe*100:.1f}%)")
        
        # 利润率评分
        profit_margin = profile.get('profit_margin', 0)
        if profit_margin > 0:
            if profit_margin > 0.20:
                score += 10
                details.append(f"✓ 利润率优秀({profit_margin*100:.1f}%)")
            elif profit_margin > 0.10:
                score += 5
                details.append(f"✓ 利润率良好({profit_margin*100:.1f}%)")
        
        # ROA评分
        roa = profile.get('roa', 0)
        if roa > 0:
            if roa > 0.10:
                score += 10
                details.append(f"✓ ROA优秀({roa*100:.1f}%)")
            elif roa > 0.05:
                score += 5
                details.append(f"✓ ROA良好({roa*100:.1f}%)")
        
        # 确保分数在0-100之间
        score = max(0, min(100, score))
        
        # 评级
        if score >= 80:
            grade = 'A'
        elif score >= 70:
            grade = 'B'
        elif score >= 60:
            grade = 'C'
        elif score >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'score': score,
            'grade': grade,
            'details': details
        }


if __name__ == "__main__":
    # 测试代码
    manager = FundamentalsDataManager()
    
    # 测试TSLA基本面
    print(f"\n{'='*60}")
    print("获取TSLA基本面数据...")
    print(f"{'='*60}")
    
    analysis = manager.get_comprehensive_analysis('TSLA')
    
    if analysis['company_profile']:
        profile = analysis['company_profile']
        print(f"\n【公司概况】")
        print(f"名称: {profile.get('name') or profile.get('company_name', 'N/A')}")
        print(f"行业: {profile.get('sector', 'N/A')} - {profile.get('industry', 'N/A')}")
        print(f"市值: ${profile.get('market_cap', 0):,.0f}")
        print(f"PE比率: {profile.get('pe_ratio') or profile.get('PERatio', 'N/A')}")
        print(f"ROE: {(profile.get('roe', 0)*100):.2f}%")
        print(f"利润率: {(profile.get('profit_margin', 0)*100):.2f}%")
        
        # 财务健康度评分
        health_score = manager.calculate_financial_health_score(analysis)
        print(f"\n【财务健康度】")
        print(f"评分: {health_score['score']}/100")
        print(f"评级: {health_score['grade']}")
        print(f"\n评分详情:")
        for detail in health_score['details']:
            print(f"  {detail}")
    
    print(f"\n数据来源: {analysis['source']}")
