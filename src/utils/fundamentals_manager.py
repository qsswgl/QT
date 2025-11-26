"""
基本面数据管理器 - 使用Alpha Vantage API
用于获取股票基本面数据并计算财务健康评分
"""
import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

class FundamentalsManager:
    """基本面数据管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("❌ 未找到ALPHA_VANTAGE_API_KEY环境变量")
        
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}  # 简单缓存避免重复请求
    
    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """
        获取公司概览数据
        
        Args:
            symbol: 股票代码 (如 'NVDA')
        
        Returns:
            dict: 公司基本面数据,包含:
                - Symbol: 股票代码
                - Name: 公司名称
                - MarketCapitalization: 市值
                - PERatio: 市盈率
                - ReturnOnEquityTTM: ROE (最近12个月)
                - CurrentRatio: 流动比率
                - 52WeekHigh/Low: 52周最高/最低价
                等等...
        """
        # 检查缓存
        cache_key = f"overview_{symbol}"
        if cache_key in self.cache:
            print(f"   💾 使用缓存数据: {symbol}")
            return self.cache[cache_key]
        
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            print(f"   📡 请求 {symbol} 基本面数据...")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否有错误
                if 'Error Message' in data:
                    print(f"   ❌ API错误: {data['Error Message']}")
                    return None
                
                if 'Note' in data:
                    print(f"   ⚠️  API频率限制: {data['Note']}")
                    return None
                
                # 检查是否有数据
                if 'Symbol' in data:
                    # 缓存数据
                    self.cache[cache_key] = data
                    print(f"   ✅ 成功获取 {symbol} 数据")
                    return data
                else:
                    print(f"   ❌ 返回数据格式错误")
                    return None
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            return None
    
    def calculate_financial_health(self, symbol: str) -> Dict:
        """
        计算财务健康评分 (0-100)
        
        评分标准:
        - PE < 40: +20分 (估值合理)
        - ROE > 10%: +25分 (盈利能力强)
        - Current Ratio > 1.5: +20分 (流动性好)
        - Debt/Equity < 1.0: +20分 (负债低)
        - Profit Margin > 10%: +15分 (利润率高)
        
        Returns:
            dict: {
                'score': 75,  # 0-100
                'grade': 'B', # A/B/C/D/F
                'checks': {
                    'pe_ok': True,
                    'roe_ok': True,
                    ...
                },
                'details': {...}
            }
        """
        overview = self.get_company_overview(symbol)
        
        if not overview:
            return {
                'score': 0,
                'grade': 'F',
                'checks': {},
                'details': {},
                'error': '无法获取数据'
            }
        
        score = 0
        checks = {}
        details = {}
        
        # 1. PE检查 (20分)
        try:
            pe = float(overview.get('PERatio', 999))
            details['pe'] = pe
            if pe > 0 and pe < 40:
                score += 20
                checks['pe_ok'] = True
            else:
                checks['pe_ok'] = False
        except:
            checks['pe_ok'] = False
            details['pe'] = 'N/A'
        
        # 2. ROE检查 (25分)
        try:
            roe = float(overview.get('ReturnOnEquityTTM', 0))
            details['roe'] = roe
            if roe > 0.10:  # 10%
                score += 25
                checks['roe_ok'] = True
            else:
                checks['roe_ok'] = False
        except:
            checks['roe_ok'] = False
            details['roe'] = 'N/A'
        
        # 3. 流动比率检查 (20分)
        try:
            current_ratio = float(overview.get('CurrentRatio', 0))
            details['current_ratio'] = current_ratio
            if current_ratio > 1.5:
                score += 20
                checks['current_ratio_ok'] = True
            else:
                checks['current_ratio_ok'] = False
        except:
            checks['current_ratio_ok'] = False
            details['current_ratio'] = 'N/A'
        
        # 4. 负债率检查 (20分)
        try:
            debt_to_equity = float(overview.get('DebtToEquity', 999))
            details['debt_to_equity'] = debt_to_equity
            if debt_to_equity < 100:  # <1.0 (以百分比表示)
                score += 20
                checks['debt_ok'] = True
            else:
                checks['debt_ok'] = False
        except:
            checks['debt_ok'] = False
            details['debt_to_equity'] = 'N/A'
        
        # 5. 利润率检查 (15分)
        try:
            profit_margin = float(overview.get('ProfitMargin', 0))
            details['profit_margin'] = profit_margin
            if profit_margin > 0.10:  # 10%
                score += 15
                checks['profit_margin_ok'] = True
            else:
                checks['profit_margin_ok'] = False
        except:
            checks['profit_margin_ok'] = False
            details['profit_margin'] = 'N/A'
        
        # 计算等级
        if score >= 80:
            grade = 'A'
        elif score >= 60:
            grade = 'B'
        elif score >= 40:
            grade = 'C'
        elif score >= 20:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'score': score,
            'grade': grade,
            'checks': checks,
            'details': details,
            'symbol': symbol
        }
    
    def should_allow_buy(self, symbol: str, min_score: int = 60) -> Dict:
        """
        判断是否允许买入 (基于财务健康度)
        
        Args:
            symbol: 股票代码
            min_score: 最低要求评分 (默认60)
        
        Returns:
            dict: {
                'allow': True/False,
                'reason': '说明',
                'health': {...}
            }
        """
        health = self.calculate_financial_health(symbol)
        
        if 'error' in health:
            # 如果无法获取数据,默认允许(不影响现有策略)
            return {
                'allow': True,
                'reason': f"无法获取基本面数据: {health['error']},使用原有策略",
                'health': health
            }
        
        score = health['score']
        grade = health['grade']
        
        if score >= min_score:
            return {
                'allow': True,
                'reason': f"财务健康良好 (评分: {score}/100, 等级: {grade})",
                'health': health
            }
        else:
            # 列出未通过的检查
            failed_checks = [k for k, v in health['checks'].items() if not v]
            return {
                'allow': False,
                'reason': f"财务健康欠佳 (评分: {score}/100, 等级: {grade}), 未通过: {', '.join(failed_checks)}",
                'health': health
            }

# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("基本面数据管理器测试")
    print("=" * 60)
    
    manager = FundamentalsManager()
    
    # 测试3只股票
    for symbol in ['NVDA', 'TSLA', 'INTC']:
        print(f"\n{'=' * 60}")
        print(f"测试股票: {symbol}")
        print(f"{'=' * 60}")
        
        # 获取基本面数据
        overview = manager.get_company_overview(symbol)
        
        if overview:
            print(f"\n📊 基本信息:")
            print(f"   公司名: {overview.get('Name', 'N/A')}")
            print(f"   行业: {overview.get('Industry', 'N/A')}")
            print(f"   市值: ${float(overview.get('MarketCapitalization', 0))/1e9:.2f}B")
            print(f"   PE: {overview.get('PERatio', 'N/A')}")
            print(f"   ROE: {float(overview.get('ReturnOnEquityTTM', 0))*100:.2f}%" if overview.get('ReturnOnEquityTTM') else '   ROE: N/A')
            print(f"   流动比率: {overview.get('CurrentRatio', 'N/A')}")
        
        # 计算财务健康度
        health = manager.calculate_financial_health(symbol)
        
        print(f"\n💯 财务健康评分:")
        print(f"   评分: {health['score']}/100")
        print(f"   等级: {health['grade']}")
        print(f"   通过检查: {sum(health['checks'].values())}/{len(health['checks'])}")
        
        # 买入建议
        decision = manager.should_allow_buy(symbol, min_score=60)
        print(f"\n🎯 买入建议:")
        print(f"   {'✅ 允许买入' if decision['allow'] else '❌ 不建议买入'}")
        print(f"   原因: {decision['reason']}")
        
        # 避免频率限制
        time.sleep(12)  # Alpha Vantage: 5次/分钟
    
    print(f"\n{'=' * 60}")
    print("✅ 测试完成!")
    print(f"{'=' * 60}")
