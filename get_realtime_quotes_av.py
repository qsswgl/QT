"""
使用Alpha Vantage获取实时行情数据
"""
import os
import sys
from pathlib import Path
import requests
from datetime import datetime
import time

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def load_api_key():
    """从.env文件加载API密钥"""
    env_file = project_root / '.env'
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k.strip() == 'ALPHA_VANTAGE_API_KEY':
                        return v.strip()
    return os.getenv('ALPHA_VANTAGE_API_KEY')


def get_realtime_quote_av(symbol: str, api_key: str) -> dict:
    """使用Alpha Vantage获取实时行情(尝试盘中数据)"""
    try:
        # 先尝试获取盘中数据(TIME_SERIES_INTRADAY)
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '1min',
            'apikey': api_key
        }
        
        print(f"   📡 请求 {symbol} 盘中实时数据...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 检查是否有盘中数据
        if 'Time Series (1min)' in data:
            time_series = data['Time Series (1min)']
            if time_series:
                # 获取最新一分钟的数据
                latest_time = list(time_series.keys())[0]
                latest_data = time_series[latest_time]
                
                current_price = float(latest_data.get('4. close', 0))
                open_price = float(latest_data.get('1. open', 0))
                high_price = float(latest_data.get('2. high', 0))
                low_price = float(latest_data.get('3. low', 0))
                volume = int(latest_data.get('5. volume', 0))
                
                # 获取元数据中的前一日收盘价
                meta_data = data.get('Meta Data', {})
                
                # 使用GLOBAL_QUOTE获取更多信息
                params2 = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': api_key
                }
                response2 = requests.get(url, params=params2, timeout=10)
                data2 = response2.json()
                
                prev_close = 0
                if 'Global Quote' in data2 and data2['Global Quote']:
                    prev_close = float(data2['Global Quote'].get('08. previous close', 0))
                
                if prev_close == 0:
                    prev_close = current_price  # 如果没有前收盘,用当前价
                
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                
                print(f"   ✅ {symbol}: ${current_price:.2f} (盘中实时, 时间: {latest_time})")
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'prev_close': prev_close,
                    'change': change,
                    'change_pct': change_pct,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'volume': volume,
                    'latest_trading_day': latest_time,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'data_type': 'intraday'
                }
        
        # 如果没有盘中数据,回退到GLOBAL_QUOTE(收盘数据)
        print(f"   ⚠️  无盘中数据,使用收盘价...")
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Global Quote' not in data:
            print(f"   ⚠️  {symbol} 数据格式异常: {data}")
            return None
        
        quote = data['Global Quote']
        
        if not quote:
            print(f"   ⚠️  {symbol} 数据为空")
            return None
        
        # 解析数据
        current_price = float(quote.get('05. price', 0))
        prev_close = float(quote.get('08. previous close', 0))
        change = float(quote.get('09. change', 0))
        change_pct = float(quote.get('10. change percent', '0').rstrip('%'))
        
        print(f"   ✅ {symbol}: ${current_price:.2f} (最近收盘价)")
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'prev_close': prev_close,
            'change': change,
            'change_pct': change_pct,
            'open': float(quote.get('02. open', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0)),
            'volume': int(quote.get('06. volume', 0)),
            'latest_trading_day': quote.get('07. latest trading day', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_type': 'daily_close'
        }
    except Exception as e:
        print(f"   ❌ 获取{symbol}失败: {e}")
        return None


def display_quote(quote: dict):
    """格式化显示行情"""
    if not quote:
        return
    
    symbol = quote['symbol']
    price = quote['current_price']
    change = quote['change']
    change_pct = quote['change_pct']
    data_type = quote.get('data_type', 'unknown')
    
    # 涨跌符号
    if change > 0:
        symbol_char = '📈'
        sign = '+'
    elif change < 0:
        symbol_char = '📉'
        sign = ''
    else:
        symbol_char = '➡️'
        sign = ''
    
    # 数据类型标签
    if data_type == 'intraday':
        type_label = '🔴 盘中实时'
    else:
        type_label = '⚪ 收盘价'
    
    print(f"\n{symbol_char} {symbol} ({type_label})")
    print(f"{'='*60}")
    print(f"当前价格: ${price:.2f} ({sign}{change:.2f}, {sign}{change_pct:.2f}%)")
    print(f"昨收价格: ${quote['prev_close']:.2f}")
    print(f"开盘价格: ${quote['open']:.2f}")
    print(f"最高价格: ${quote['high']:.2f}")
    print(f"最低价格: ${quote['low']:.2f}")
    print(f"成交量:   {quote['volume']:,}")
    print(f"数据时间: {quote['latest_trading_day']}")
    print(f"查询时间: {quote['timestamp']}")


if __name__ == "__main__":
    print("="*60)
    print("📊 获取NVDA/TSLA/INTC实时行情 (Alpha Vantage)")
    print("="*60)
    print(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    api_key = load_api_key()
    if not api_key:
        print("❌ 未找到Alpha Vantage API密钥!")
        print("请确保.env文件中配置了ALPHA_VANTAGE_API_KEY")
        exit(1)
    
    symbols = ['NVDA', 'TSLA', 'INTC']
    quotes = {}
    
    for i, symbol in enumerate(symbols):
        quote = get_realtime_quote_av(symbol, api_key)
        if quote:
            quotes[symbol] = quote
            display_quote(quote)
        
        # Alpha Vantage限制: 5次/分钟
        if i < len(symbols) - 1:
            print(f"\n⏳ 等待15秒 (API频率限制)...")
            time.sleep(15)
    
    # 生成汇总
    print("\n" + "="*60)
    print("📋 今日行情汇总")
    print("="*60)
    print(f"{'股票':<8} {'当前价格':>12} {'涨跌':>12} {'涨跌幅':>10} {'交易日':>12}")
    print("-"*60)
    
    for symbol in symbols:
        if symbol in quotes:
            q = quotes[symbol]
            sign = '+' if q['change'] > 0 else ''
            print(f"{symbol:<8} ${q['current_price']:>10.2f} {sign}{q['change']:>10.2f} {sign}{q['change_pct']:>8.2f}% {q['latest_trading_day']:>12}")
    
    print("\n✅ 实时行情获取完成!")
    
    # 保存到文件
    output_file = project_root / 'realtime_quotes.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"NVDA/TSLA/INTC实时行情\n")
        f.write(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        for symbol in symbols:
            if symbol in quotes:
                q = quotes[symbol]
                sign = '+' if q['change'] > 0 else ''
                f.write(f"{symbol}:\n")
                f.write(f"  当前价格: ${q['current_price']:.2f}\n")
                f.write(f"  涨跌: {sign}{q['change']:.2f} ({sign}{q['change_pct']:.2f}%)\n")
                f.write(f"  开/高/低: ${q['open']:.2f} / ${q['high']:.2f} / ${q['low']:.2f}\n")
                f.write(f"  成交量: {q['volume']:,}\n")
                f.write(f"  交易日: {q['latest_trading_day']}\n\n")
    
    print(f"💾 行情数据已保存到: {output_file}")
