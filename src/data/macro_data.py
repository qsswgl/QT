"""
宏观经济数据源
提供利率、GDP、通胀、就业等宏观经济指标
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class FREDProvider:
    """
    FRED (Federal Reserve Economic Data) 数据源
    免费API Key申请: https://fred.stlouisfed.org/docs/api/api_key.html
    免费版无限制
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FRED_API_KEY")
        self.base_url = "https://api.stlouisfed.org/fred"
    
    def get_series(self, series_id: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """获取经济指标序列数据
        
        常用series_id:
        - DFF: 联邦基金利率
        - GDP: 美国GDP
        - CPIAUCSL: CPI消费者物价指数
        - UNRATE: 失业率
        - T10Y2Y: 10年期-2年期国债收益率差
        """
        if not self.api_key:
            raise ValueError("FRED API Key未配置,请设置环境变量FRED_API_KEY")
        
        url = f"{self.base_url}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        
        if start_date:
            params['observation_start'] = start_date
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            observations = data.get('observations', [])
            df = pd.DataFrame(observations)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df[['date', 'value']].dropna()
                df.columns = ['date', series_id]
            
            return df
        except Exception as e:
            print(f"FRED数据获取失败({series_id}): {e}")
            return pd.DataFrame()
    
    def get_multiple_series(self, series_ids: List[str], start_date: Optional[str] = None) -> pd.DataFrame:
        """批量获取多个经济指标"""
        all_data = []
        
        for series_id in series_ids:
            df = self.get_series(series_id, start_date)
            if not df.empty:
                all_data.append(df)
        
        if not all_data:
            return pd.DataFrame()
        
        # 合并所有数据
        result = all_data[0]
        for df in all_data[1:]:
            result = pd.merge(result, df, on='date', how='outer')
        
        result = result.sort_values('date').reset_index(drop=True)
        return result
    
    def get_key_indicators(self) -> pd.DataFrame:
        """获取关键宏观经济指标"""
        key_series = {
            'DFF': '联邦基金利率',
            'T10Y2Y': '10年期-2年期国债利差',
            'CPIAUCSL': 'CPI',
            'UNRATE': '失业率',
            'DEXUSEU': '美元/欧元汇率'
        }
        
        # 获取最近1年数据
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        df = self.get_multiple_series(list(key_series.keys()), start_date)
        
        if not df.empty:
            # 重命名列
            rename_dict = {k: v for k, v in key_series.items()}
            df = df.rename(columns=rename_dict)
        
        return df


class WorldBankProvider:
    """
    World Bank数据源(无需API Key)
    提供全球经济指标
    """
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"
    
    def get_indicator(self, country: str, indicator: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取指定国家的经济指标
        
        country: 国家代码,如US(美国), CN(中国)
        indicator: 指标代码,如NY.GDP.MKTP.CD(GDP)
        
        常用指标:
        - NY.GDP.MKTP.CD: GDP
        - FP.CPI.TOTL.ZG: 通胀率
        - SL.UEM.TOTL.ZS: 失业率
        """
        url = f"{self.base_url}/country/{country}/indicator/{indicator}"
        params = {
            'date': f'{start_year}:{end_year}',
            'format': 'json',
            'per_page': 1000
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if len(data) > 1 and data[1]:
                records = data[1]
                df = pd.DataFrame(records)
                
                if not df.empty:
                    df = df[['date', 'value']].rename(columns={'date': 'year'})
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df = df.dropna()
                    df[indicator] = df['value']
                    df = df[['year', indicator]]
                
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"World Bank数据获取失败: {e}")
            return pd.DataFrame()


class EconomicIndicatorsAnalyzer:
    """宏观经济指标分析器"""
    
    @staticmethod
    def analyze_yield_curve(ten_two_spread: float) -> Dict:
        """分析收益率曲线
        10年期-2年期国债利差是衰退的领先指标
        """
        if ten_two_spread < -0.5:
            signal = 'strong_recession_warning'
            description = '收益率曲线严重倒挂,强烈衰退信号'
            risk_level = 'high'
        elif ten_two_spread < 0:
            signal = 'recession_warning'
            description = '收益率曲线倒挂,可能预示衰退'
            risk_level = 'medium'
        elif ten_two_spread < 0.5:
            signal = 'flattening'
            description = '收益率曲线趋平,经济放缓迹象'
            risk_level = 'low'
        else:
            signal = 'normal'
            description = '收益率曲线正常,经济健康'
            risk_level = 'low'
        
        return {
            'spread': ten_two_spread,
            'signal': signal,
            'description': description,
            'risk_level': risk_level
        }
    
    @staticmethod
    def analyze_inflation(cpi_yoy_change: float) -> Dict:
        """分析通胀水平"""
        if cpi_yoy_change > 5:
            level = 'high'
            description = '高通胀,央行可能加息'
            impact = 'negative'
        elif cpi_yoy_change > 3:
            level = 'moderate_high'
            description = '通胀偏高,需关注央行政策'
            impact = 'slightly_negative'
        elif cpi_yoy_change > 1:
            level = 'target'
            description = '通胀在目标范围内'
            impact = 'neutral'
        else:
            level = 'low'
            description = '通胀偏低,可能有通缩风险'
            impact = 'slightly_negative'
        
        return {
            'cpi_change': cpi_yoy_change,
            'level': level,
            'description': description,
            'market_impact': impact
        }
    
    @staticmethod
    def analyze_interest_rate(fed_funds_rate: float) -> Dict:
        """分析利率环境"""
        if fed_funds_rate > 5:
            environment = 'tight'
            description = '高利率环境,抑制经济增长'
            equity_impact = 'negative'
        elif fed_funds_rate > 3:
            environment = 'moderate'
            description = '中等利率,平衡增长与通胀'
            equity_impact = 'neutral'
        elif fed_funds_rate > 1:
            environment = 'accommodative'
            description = '宽松利率,支持经济增长'
            equity_impact = 'positive'
        else:
            environment = 'very_accommodative'
            description = '极度宽松,强力刺激经济'
            equity_impact = 'very_positive'
        
        return {
            'rate': fed_funds_rate,
            'environment': environment,
            'description': description,
            'equity_impact': equity_impact
        }
    
    @staticmethod
    def calculate_economic_health_score(indicators: Dict) -> Dict:
        """计算经济健康度评分(0-100)"""
        score = 50  # 基准分
        factors = []
        
        # 收益率曲线(权重30%)
        if 'yield_curve_spread' in indicators:
            spread = indicators['yield_curve_spread']
            if spread > 1:
                score += 15
                factors.append("✓ 收益率曲线正常")
            elif spread > 0:
                score += 5
                factors.append("○ 收益率曲线略平")
            elif spread > -0.5:
                score -= 10
                factors.append("✗ 收益率曲线倒挂")
            else:
                score -= 20
                factors.append("✗✗ 收益率曲线严重倒挂")
        
        # 通胀率(权重25%)
        if 'cpi_change' in indicators:
            cpi = indicators['cpi_change']
            if 1 < cpi < 3:
                score += 15
                factors.append("✓ 通胀适中")
            elif cpi < 1:
                score -= 5
                factors.append("○ 通胀偏低")
            elif cpi < 5:
                score -= 10
                factors.append("✗ 通胀偏高")
            else:
                score -= 15
                factors.append("✗✗ 高通胀")
        
        # 失业率(权重25%)
        if 'unemployment_rate' in indicators:
            unemp = indicators['unemployment_rate']
            if unemp < 4:
                score += 15
                factors.append("✓ 失业率低")
            elif unemp < 5:
                score += 10
                factors.append("✓ 失业率正常")
            elif unemp < 7:
                score -= 5
                factors.append("○ 失业率偏高")
            else:
                score -= 15
                factors.append("✗ 失业率高")
        
        # 利率环境(权重20%)
        if 'fed_funds_rate' in indicators:
            rate = indicators['fed_funds_rate']
            if rate < 2:
                score += 10
                factors.append("✓ 低利率环境")
            elif rate < 4:
                score += 5
                factors.append("○ 中等利率")
            else:
                score -= 10
                factors.append("✗ 高利率环境")
        
        score = max(0, min(100, score))
        
        if score >= 70:
            grade = 'A - 经济强劲'
        elif score >= 60:
            grade = 'B - 经济良好'
        elif score >= 50:
            grade = 'C - 经济平稳'
        elif score >= 40:
            grade = 'D - 经济疲软'
        else:
            grade = 'F - 经济衰退风险'
        
        return {
            'score': score,
            'grade': grade,
            'factors': factors
        }


class MacroDataManager:
    """宏观经济数据管理器"""
    def __init__(self):
        self.fred = None
        self.worldbank = None
        
        try:
            self.fred = FREDProvider()
        except:
            print("⚠️ FRED未配置")
        
        try:
            self.worldbank = WorldBankProvider()
        except:
            print("⚠️ World Bank未配置")
    
    def get_macro_snapshot(self) -> Dict:
        """获取宏观经济快照"""
        result = {
            'indicators': {},
            'analysis': {},
            'health_score': {}
        }
        
        if not self.fred:
            return result
        
        try:
            # 获取关键指标
            df = self.fred.get_key_indicators()
            
            if not df.empty:
                latest = df.iloc[-1]
                
                # 提取最新数据
                indicators = {
                    'fed_funds_rate': latest.get('联邦基金利率', 0),
                    'yield_curve_spread': latest.get('10年期-2年期国债利差', 0),
                    'unemployment_rate': latest.get('失业率', 0),
                    'date': latest.get('date', datetime.now())
                }
                
                # 计算CPI同比变化
                if '联邦基金利率' in df.columns:
                    cpi_col = 'CPI'
                    if cpi_col in df.columns and len(df) >= 12:
                        current_cpi = df[cpi_col].iloc[-1]
                        year_ago_cpi = df[cpi_col].iloc[-13]  # 12个月前
                        if year_ago_cpi > 0:
                            indicators['cpi_change'] = ((current_cpi - year_ago_cpi) / year_ago_cpi) * 100
                
                result['indicators'] = indicators
                
                # 分析各项指标
                analyzer = EconomicIndicatorsAnalyzer()
                
                if indicators.get('yield_curve_spread'):
                    result['analysis']['yield_curve'] = analyzer.analyze_yield_curve(
                        indicators['yield_curve_spread']
                    )
                
                if indicators.get('cpi_change'):
                    result['analysis']['inflation'] = analyzer.analyze_inflation(
                        indicators['cpi_change']
                    )
                
                if indicators.get('fed_funds_rate'):
                    result['analysis']['interest_rate'] = analyzer.analyze_interest_rate(
                        indicators['fed_funds_rate']
                    )
                
                # 计算经济健康度
                result['health_score'] = analyzer.calculate_economic_health_score(indicators)
        
        except Exception as e:
            print(f"宏观数据获取失败: {e}")
        
        return result


if __name__ == "__main__":
    # 测试代码
    manager = MacroDataManager()
    
    print(f"\n{'='*60}")
    print("宏观经济数据快照")
    print(f"{'='*60}")
    
    snapshot = manager.get_macro_snapshot()
    
    if snapshot['indicators']:
        print(f"\n【关键指标】")
        indicators = snapshot['indicators']
        print(f"联邦基金利率: {indicators.get('fed_funds_rate', 'N/A'):.2f}%")
        print(f"10Y-2Y国债利差: {indicators.get('yield_curve_spread', 'N/A'):.2f}%")
        print(f"失业率: {indicators.get('unemployment_rate', 'N/A'):.2f}%")
        if 'cpi_change' in indicators:
            print(f"CPI同比变化: {indicators['cpi_change']:.2f}%")
        print(f"数据日期: {indicators.get('date', 'N/A')}")
    
    if snapshot['analysis']:
        print(f"\n【分析】")
        analysis = snapshot['analysis']
        
        if 'yield_curve' in analysis:
            yc = analysis['yield_curve']
            print(f"\n收益率曲线: {yc['description']}")
            print(f"  风险等级: {yc['risk_level'].upper()}")
        
        if 'inflation' in analysis:
            inf = analysis['inflation']
            print(f"\n通胀水平: {inf['description']}")
            print(f"  市场影响: {inf['market_impact']}")
        
        if 'interest_rate' in analysis:
            ir = analysis['interest_rate']
            print(f"\n利率环境: {ir['description']}")
            print(f"  股市影响: {ir['equity_impact']}")
    
    if snapshot['health_score']:
        health = snapshot['health_score']
        print(f"\n【经济健康度】")
        print(f"评分: {health['score']}/100")
        print(f"评级: {health['grade']}")
        print(f"\n评分因素:")
        for factor in health['factors']:
            print(f"  {factor}")
