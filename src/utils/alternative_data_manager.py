"""
另类数据管理器
获取VIX恐慌指数、大宗商品、汇率等补充市场数据
主要使用 yfinance 作为数据源
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional

class AlternativeDataManager:
    """另类数据管理器"""
    
    def __init__(self):
        pass
        
    def get_market_indicators(self) -> Dict:
        """获取关键市场指标
        
        Returns:
            {
                'vix': {'price': float, 'change': float, 'status': str},
                'gold': {'price': float, 'change': float},
                'oil': {'price': float, 'change': float},
                'usd_index': {'price': float, 'change': float},
                'timestamp': str
            }
        """
        indicators = {
            'vix': '^VIX',      # 恐慌指数
            'gold': 'GC=F',     # 黄金期货
            'oil': 'CL=F',      # 原油期货
            'usd_index': 'DX-Y.NYB' # 美元指数
        }
        
        result = {}
        
        try:
            # 批量获取数据
            tickers = " ".join(indicators.values())
            data = yf.Tickers(tickers)
            
            for name, symbol in indicators.items():
                try:
                    ticker = data.tickers[symbol]
                    # 获取最新数据
                    hist = ticker.history(period="2d")
                    
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change_pct = ((current - prev) / prev) * 100
                        
                        info = {
                            'price': round(current, 2),
                            'change_pct': round(change_pct, 2),
                            'trend': 'up' if change_pct > 0 else 'down'
                        }
                        
                        # 特殊处理VIX状态
                        if name == 'vix':
                            info['status'] = self._analyze_vix(current)
                            
                        result[name] = info
                    else:
                        result[name] = None
                        
                except Exception as e:
                    print(f"获取 {name} ({symbol}) 失败: {e}")
                    result[name] = None
            
            result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return result
            
        except Exception as e:
            print(f"获取市场指标失败: {e}")
            return {}

    def _analyze_vix(self, vix_value: float) -> str:
        """分析VIX恐慌指数状态"""
        if vix_value < 15:
            return "complacent"  # 市场过度乐观/贪婪
        elif vix_value < 20:
            return "normal"      # 正常波动
        elif vix_value < 30:
            return "fear"        # 恐慌
        else:
            return "extreme_fear" # 极度恐慌

    def get_sector_performance(self) -> Dict:
        """获取主要板块表现(通过ETF)"""
        sectors = {
            'XLK': '科技',
            'XLF': '金融',
            'XLV': '医疗',
            'XLE': '能源',
            'XLP': '消费'
        }
        
        result = {}
        try:
            tickers = " ".join(sectors.keys())
            data = yf.Tickers(tickers)
            
            for symbol, name in sectors.items():
                ticker = data.tickers[symbol]
                hist = ticker.history(period="5d")
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    week_ago = hist['Close'].iloc[0]
                    week_change = ((current - week_ago) / week_ago) * 100
                    
                    result[name] = {
                        'price': round(current, 2),
                        'week_change': round(week_change, 2)
                    }
            return result
        except Exception as e:
            print(f"获取板块数据失败: {e}")
            return {}

if __name__ == "__main__":
    # 测试
    mgr = AlternativeDataManager()
    print("📊 市场关键指标:")
    indicators = mgr.get_market_indicators()
    for k, v in indicators.items():
        if k != 'timestamp' and v:
            print(f"  {k.upper()}: {v['price']} ({v['change_pct']}%)")
            if k == 'vix':
                print(f"    状态: {v['status']}")
    
    print("\n📈 板块表现(5日):")
    sectors = mgr.get_sector_performance()
    for k, v in sectors.items():
        print(f"  {k}: {v['week_change']}%")
