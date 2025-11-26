"""
使用Finnhub API获取NVDA/TSLA/INTC实时行情
Finnhub提供真正的实时数据(延迟<1秒)
"""
import os
import requests
from datetime import datetime
import pytz

def load_api_key():
    """从.env文件读取Finnhub API密钥"""
    env_path = 'K:/QT/.env'
    
    if not os.path.exists(env_path):
        print(f"❌ .env文件不存在: {env_path}")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('FINNHUB_API_KEY='):
                api_key = line.split('=', 1)[1].strip().strip('"\'')
                if api_key and api_key != 'your_finnhub_api_key_here':
                    return api_key
    
    print("❌ 未找到有效的FINNHUB_API_KEY")
    return None

def get_realtime_quote(symbol, api_key):
    """
    获取股票实时报价
    
    Args:
        symbol: 股票代码
        api_key: Finnhub API密钥
        
    Returns:
        dict: 包含实时行情数据
    """
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'c' in data and data['c'] > 0:
            # c=当前价, pc=昨收价, o=开盘价, h=今日最高, l=今日最低, t=时间戳
            current_price = data['c']
            prev_close = data['pc']
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            # 转换时间戳为北京时间
            timestamp = data['t']
            us_eastern = pytz.timezone('US/Eastern')
            beijing = pytz.timezone('Asia/Shanghai')
            dt_utc = datetime.fromtimestamp(timestamp, tz=pytz.utc)
            dt_beijing = dt_utc.astimezone(beijing)
            dt_eastern = dt_utc.astimezone(us_eastern)
            
            return {
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
        else:
            return {
                'symbol': symbol,
                'success': False,
                'error': '无效的响应数据'
            }
            
    except Exception as e:
        return {
            'symbol': symbol,
            'success': False,
            'error': str(e)
        }

def display_quote(quote_data):
    """显示行情数据"""
    if not quote_data['success']:
        print(f"\n❌ {quote_data['symbol']}: {quote_data['error']}")
        return
    
    symbol = quote_data['symbol']
    current = quote_data['current_price']
    change = quote_data['change']
    change_pct = quote_data['change_pct']
    
    # 根据涨跌使用不同的emoji
    if change > 0:
        emoji = "📈"
        sign = "+"
    elif change < 0:
        emoji = "📉"
        sign = ""
    else:
        emoji = "➡️"
        sign = ""
    
    print(f"\n{emoji} {symbol} (🔴 实时数据)")
    print("=" * 60)
    print(f"当前价格: ${current:.2f} ({sign}{change:.2f}, {sign}{change_pct:.2f}%)")
    print(f"昨收价格: ${quote_data['prev_close']:.2f}")
    print(f"开盘价格: ${quote_data['open']:.2f}")
    print(f"最高价格: ${quote_data['high']:.2f}")
    print(f"最低价格: ${quote_data['low']:.2f}")
    print(f"美东时间: {quote_data['time_eastern']}")
    print(f"北京时间: {quote_data['time_beijing']}")

def save_quotes(quotes):
    """保存行情到文件"""
    output_file = 'K:/QT/realtime_quotes.txt'
    
    beijing_now = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"NVDA/TSLA/INTC实时行情 (Finnhub)\n")
        f.write(f"更新时间: {beijing_now}\n")
        f.write("=" * 60 + "\n\n")
        
        for quote in quotes:
            if quote['success']:
                f.write(f"{quote['symbol']}:\n")
                f.write(f"  当前价格: ${quote['current_price']:.2f}\n")
                f.write(f"  涨跌: {'+' if quote['change'] >= 0 else ''}{quote['change']:.2f} ")
                f.write(f"({'+' if quote['change_pct'] >= 0 else ''}{quote['change_pct']:.2f}%)\n")
                f.write(f"  开/高/低: ${quote['open']:.2f} / ${quote['high']:.2f} / ${quote['low']:.2f}\n")
                f.write(f"  美东时间: {quote['time_eastern']}\n")
                f.write(f"  北京时间: {quote['time_beijing']}\n\n")
    
    print(f"\n💾 行情数据已保存到: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("📊 获取NVDA/TSLA/INTC实时行情 (Finnhub)")
    print("=" * 60)
    
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now_beijing = datetime.now(beijing_tz)
    print(f"查询时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)\n")
    
    # 加载API密钥
    api_key = load_api_key()
    if not api_key:
        return
    
    # 获取三支股票的实时行情
    symbols = ['NVDA', 'TSLA', 'INTC']
    quotes = []
    
    for symbol in symbols:
        print(f"   📡 请求 {symbol} 实时数据...")
        quote = get_realtime_quote(symbol, api_key)
        quotes.append(quote)
        
        if quote['success']:
            print(f"   ✅ {symbol}: ${quote['current_price']:.2f}")
        else:
            print(f"   ❌ {symbol}: {quote['error']}")
    
    # 显示详细行情
    for quote in quotes:
        display_quote(quote)
    
    # 汇总表格
    print("\n" + "=" * 60)
    print("📋 今日行情汇总")
    print("=" * 60)
    print(f"{'股票':<10} {'当前价格':>12} {'涨跌':>10} {'涨跌幅':>10} {'更新时间(北京)':<20}")
    print("-" * 60)
    
    for quote in quotes:
        if quote['success']:
            symbol = quote['symbol']
            price = quote['current_price']
            change = quote['change']
            change_pct = quote['change_pct']
            time_str = quote['time_beijing']
            
            print(f"{symbol:<10} ${price:>10.2f} {change:>+9.2f} {change_pct:>+8.2f}% {time_str:<20}")
    
    # 保存到文件
    save_quotes(quotes)
    
    print("\n✅ 实时行情获取完成!")

if __name__ == "__main__":
    main()
