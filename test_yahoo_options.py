"""
Yahoo Finance期权数据测试
无需API密钥的免费期权数据源!
"""
import yfinance as yf
from datetime import datetime

print("=" * 60)
print("Yahoo Finance 期权数据测试")
print("=" * 60)
print("优势: 完全免费, 无需API密钥, 数据实时!")
print()

# 测试3只股票的期权数据
symbols = ['NVDA', 'TSLA', 'INTC']

for symbol in symbols:
    print("=" * 60)
    print(f"测试股票: {symbol}")
    print("=" * 60)
    
    try:
        # 创建股票对象
        stock = yf.Ticker(symbol)
        
        # 1. 获取期权到期日
        print(f"\n📅 期权到期日:")
        expiration_dates = stock.options
        if expiration_dates:
            print(f"   ✅ 共有 {len(expiration_dates)} 个到期日")
            print(f"   最近3个: {expiration_dates[:3]}")
        else:
            print(f"   ❌ 无期权数据")
            continue
        
        # 2. 获取最近到期日的期权链
        nearest_expiry = expiration_dates[0]
        print(f"\n📊 获取 {nearest_expiry} 到期的期权链...")
        
        opt_chain = stock.option_chain(nearest_expiry)
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        print(f"   ✅ Call期权: {len(calls)} 个")
        print(f"   ✅ Put期权: {len(puts)} 个")
        
        # 3. 获取当前股价
        current_price = stock.info.get('currentPrice', stock.info.get('regularMarketPrice', 0))
        print(f"\n💰 当前股价: ${current_price:.2f}")
        
        # 4. 找到平值期权 (ATM)
        if not calls.empty and not puts.empty:
            # 找到最接近当前价格的行权价
            calls['distance'] = abs(calls['strike'] - current_price)
            atm_call = calls.loc[calls['distance'].idxmin()]
            
            puts['distance'] = abs(puts['strike'] - current_price)
            atm_put = puts.loc[puts['distance'].idxmin()]
            
            print(f"\n🎯 平值期权 (ATM) - 行权价 ${atm_call['strike']:.2f}:")
            print(f"   Call隐含波动率: {atm_call.get('impliedVolatility', 0)*100:.2f}%")
            print(f"   Put隐含波动率: {atm_put.get('impliedVolatility', 0)*100:.2f}%")
            print(f"   Call未平仓合约: {atm_call.get('openInterest', 0):,}")
            print(f"   Put未平仓合约: {atm_put.get('openInterest', 0):,}")
        
        # 5. 计算Put/Call比率
        total_call_oi = calls['openInterest'].sum()
        total_put_oi = puts['openInterest'].sum()
        
        if total_call_oi > 0:
            pc_ratio = total_put_oi / total_call_oi
            print(f"\n📈 Put/Call比率: {pc_ratio:.2f}")
            
            if pc_ratio > 1.3:
                print(f"   ⚠️  看跌情绪较重 (比率>1.3)")
            elif pc_ratio < 0.7:
                print(f"   ⚠️  看涨情绪过度 (比率<0.7)")
            else:
                print(f"   ✅ 市场情绪中性")
        
        # 6. 计算Max Pain (最大痛苦点)
        print(f"\n🎲 计算Max Pain...")
        
        # 合并所有行权价
        all_strikes = sorted(set(calls['strike'].tolist() + puts['strike'].tolist()))
        
        max_pain_strike = None
        min_pain_value = float('inf')
        
        for strike in all_strikes:
            # 计算该行权价的总痛苦值
            call_pain = calls[calls['strike'] > strike].apply(
                lambda x: (x['strike'] - strike) * x['openInterest'], axis=1
            ).sum()
            
            put_pain = puts[puts['strike'] < strike].apply(
                lambda x: (strike - x['strike']) * x['openInterest'], axis=1
            ).sum()
            
            total_pain = call_pain + put_pain
            
            if total_pain < min_pain_value:
                min_pain_value = total_pain
                max_pain_strike = strike
        
        if max_pain_strike:
            print(f"   Max Pain行权价: ${max_pain_strike:.2f}")
            print(f"   当前价格距离: ${abs(current_price - max_pain_strike):.2f}")
            
            if abs(current_price - max_pain_strike) < current_price * 0.02:
                print(f"   💡 价格接近Max Pain,可能横盘整理")
            elif current_price > max_pain_strike:
                print(f"   ⬆️  价格高于Max Pain,可能有下行压力")
            else:
                print(f"   ⬇️  价格低于Max Pain,可能有上行支撑")
        
        print()
        
    except Exception as e:
        print(f"❌ 获取 {symbol} 期权数据失败: {e}")
        print()

print("=" * 60)
print("✅ Yahoo Finance期权数据测试完成!")
print("=" * 60)

print("\n💡 Yahoo Finance 优势:")
print("   ✅ 完全免费,无需API密钥")
print("   ✅ 数据实时更新")
print("   ✅ 覆盖所有美股期权")
print("   ✅ 无请求频率限制")
print("   ✅ 数据质量高")

print("\n📊 可用指标:")
print("   - 期权到期日列表")
print("   - Call/Put期权链")
print("   - 隐含波动率 (IV)")
print("   - 未平仓合约 (OI)")
print("   - Put/Call比率")
print("   - Max Pain (最大痛苦点)")

print("\n🚀 下一步:")
print("   1. 将期权数据集成到策略中")
print("   2. 使用Put/Call比率判断市场情绪")
print("   3. 参考Max Pain预测价格走势")
