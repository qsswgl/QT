# -*- coding: utf-8 -*-
"""
实时行情管理器
使用Finnhub API获取盘中实时报价
"""
import os
import requests
from datetime import datetime
import pytz
from typing import Dict, Optional


class RealtimeQuotesManager:
    """实时行情管理器"""
    
    def __init__(self):
        """初始化实时行情管理器"""
        self.api_key = self._load_api_key()
        self.base_url = "https://finnhub.io/api/v1"
        
    def _load_api_key(self) -> Optional[str]:
        """从.env文件读取Finnhub API密钥"""
        env_path = 'K:/QT/.env'
        
        if not os.path.exists(env_path):
            print(f"⚠️  .env文件不存在: {env_path}")
            return None
        
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('FINNHUB_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"\'')
                    if api_key and api_key != 'your_finnhub_api_key_here':
                        return api_key
        
        print("⚠️  未找到有效的FINNHUB_API_KEY")
        return None
    
    def get_realtime_quote(self, symbol: str) -> Dict:
        """
        获取股票盘中实时报价
        
        Args:
            symbol: 股票代码 (如 'NVDA', 'TSLA', 'INTC')
            
        Returns:
            dict: 包含实时行情数据
                {
                    'symbol': str,
                    'current_price': float,
                    'prev_close': float,
                    'open': float,
                    'high': float,
                    'low': float,
                    'change': float,
                    'change_pct': float,
                    'timestamp': int,
                    'time_beijing': str,
                    'time_eastern': str,
                    'success': bool
                }
        """
        if not self.api_key:
            return {
                'symbol': symbol,
                'success': False,
                'error': 'API密钥未配置'
            }
        
        try:
            print(f"   📡 请求 {symbol} 盘中实时报价...")
            
            url = f"{self.base_url}/quote?symbol={symbol}&token={self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'c' in data and data['c'] > 0:
                # c=当前价, pc=昨收价, o=开盘价, h=今日最高, l=今日最低, t=时间戳
                current_price = data['c']
                prev_close = data['pc']
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                
                # 转换时间戳为北京时间和美东时间
                timestamp = data['t']
                us_eastern = pytz.timezone('US/Eastern')
                beijing = pytz.timezone('Asia/Shanghai')
                dt_utc = datetime.fromtimestamp(timestamp, tz=pytz.utc)
                dt_beijing = dt_utc.astimezone(beijing)
                dt_eastern = dt_utc.astimezone(us_eastern)
                
                result = {
                    'symbol': symbol,
                    'current_price': current_price,
                    'prev_close': prev_close,
                    'open': data.get('o', 0),
                    'high': data.get('h', 0),
                    'low': data.get('l', 0),
                    'change': change,
                    'change_pct': change_pct,
                    'timestamp': timestamp,
                    'time_beijing': dt_beijing.strftime('%Y-%m-%d %H:%M:%S'),
                    'time_eastern': dt_eastern.strftime('%Y-%m-%d %H:%M:%S'),
                    'success': True
                }
                
                print(f"   ✅ {symbol}: ${current_price:.2f} ({change:+.2f}, {change_pct:+.2f}%)")
                print(f"      时间: {dt_beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京)")
                
                return result
            else:
                return {
                    'symbol': symbol,
                    'success': False,
                    'error': '无效的响应数据'
                }
                
        except requests.exceptions.Timeout:
            return {
                'symbol': symbol,
                'success': False,
                'error': '请求超时'
            }
        except requests.exceptions.RequestException as e:
            return {
                'symbol': symbol,
                'success': False,
                'error': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'success': False,
                'error': f'未知错误: {str(e)}'
            }
    
    def format_quote_info(self, quote: Dict) -> str:
        """
        格式化行情信息用于显示
        
        Args:
            quote: get_realtime_quote返回的行情数据
            
        Returns:
            str: 格式化的行情信息
        """
        if not quote['success']:
            return f"❌ {quote['symbol']}: {quote['error']}"
        
        symbol = quote['symbol']
        price = quote['current_price']
        change = quote['change']
        change_pct = quote['change_pct']
        time_str = quote['time_beijing']
        
        # 根据涨跌选择emoji
        if change > 0:
            emoji = "📈"
            sign = "+"
        elif change < 0:
            emoji = "📉"
            sign = ""
        else:
            emoji = "➡️"
            sign = ""
        
        info = f"{emoji} {symbol}: ${price:.2f} ({sign}{change:.2f}, {sign}{change_pct:.2f}%)\n"
        info += f"   开/高/低: ${quote['open']:.2f} / ${quote['high']:.2f} / ${quote['low']:.2f}\n"
        info += f"   时间: {time_str} (盘中实时)"
        
        return info
    
    def is_market_open(self) -> bool:
        """
        检查美股市场是否开盘
        
        Returns:
            bool: True表示市场开盘,False表示市场关闭
        """
        us_eastern = pytz.timezone('US/Eastern')
        now_et = datetime.now(us_eastern)
        
        # 检查是否为交易日(周一到周五)
        if now_et.weekday() >= 5:  # 周六(5)或周日(6)
            return False
        
        # 检查是否在交易时间(9:30 AM - 4:00 PM ET)
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now_et <= market_close
    
    def get_market_status(self) -> Dict:
        """
        获取市场状态信息
        
        Returns:
            dict: 市场状态
                {
                    'is_open': bool,
                    'current_time_et': str,
                    'current_time_beijing': str,
                    'message': str
                }
        """
        us_eastern = pytz.timezone('US/Eastern')
        beijing = pytz.timezone('Asia/Shanghai')
        
        now_et = datetime.now(us_eastern)
        now_beijing = datetime.now(beijing)
        
        is_open = self.is_market_open()
        
        if is_open:
            message = "✅ 市场开盘中"
        elif now_et.weekday() >= 5:
            message = "⏸️  周末休市"
        else:
            message = "🔴 市场已收盘"
        
        return {
            'is_open': is_open,
            'current_time_et': now_et.strftime('%Y-%m-%d %H:%M:%S ET'),
            'current_time_beijing': now_beijing.strftime('%Y-%m-%d %H:%M:%S'),
            'message': message
        }


if __name__ == "__main__":
    """测试实时行情管理器"""
    print("=" * 60)
    print("📊 实时行情管理器测试")
    print("=" * 60)
    print()
    
    manager = RealtimeQuotesManager()
    
    # 检查市场状态
    status = manager.get_market_status()
    print(f"🕐 当前时间: {status['current_time_beijing']} (北京)")
    print(f"🕐 当前时间: {status['current_time_et']}")
    print(f"📊 市场状态: {status['message']}")
    print()
    
    # 获取实时报价
    for symbol in ['NVDA', 'TSLA', 'INTC']:
        quote = manager.get_realtime_quote(symbol)
        print()
        print(manager.format_quote_info(quote))
        print()
