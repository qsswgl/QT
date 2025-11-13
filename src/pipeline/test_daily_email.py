"""
日度策略检查 - 测试版本 (用于测试有信号的情况)
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.pipeline.run_daily_strategy import DailyTradingStrategy
from src.notification.email_service import EmailService


def check_for_new_signals(days_back: int = 30) -> dict:
    """
    检查是否有新的交易信号 (测试用 - 可调整天数)
    """
    signal_file = project_root / "backtest_results" / "daily" / "signals_daily.csv"
    
    if not signal_file.exists():
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': []
        }
    
    # 读取信号文件
    signals_df = pd.read_csv(signal_file)
    
    if signals_df.empty:
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': []
        }
    
    # 转换日期
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    
    # 获取最近N天的信号
    cutoff_date = datetime.now() - timedelta(days=days_back)
    recent_signals = signals_df[signals_df['date'] >= cutoff_date]
    
    has_new_signal = len(recent_signals) > 0
    
    result = {
        'has_signal': has_new_signal,
        'signal_count': len(recent_signals),
        'all_signals': signals_df.to_dict('records')
    }
    
    if has_new_signal:
        # 获取最新的信号
        latest = recent_signals.iloc[-1]
        result['latest_signal'] = {
            'date': latest['date'].strftime('%Y-%m-%d'),
            'action': latest['action'],
            'quantity': int(latest['quantity']),
            'reason': latest.get('reason', ''),
            'price': float(latest.get('price', 0))
        }
    else:
        result['latest_signal'] = None
    
    return result


def main():
    """测试邮件发送 (模拟有信号的情况)"""
    print("=" * 80)
    print("📊 TSLA 日度策略测试 (模拟有信号)")
    print("=" * 80)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    
    try:
        # 加载数据
        print("📂 加载历史数据...")
        data_path = project_root / "data" / "sample_tsla.csv"
        loader = CSVPriceLoader(data_path)
        bars = list(loader.load())
        print(f"✓ 已加载 {len(bars)} 条历史数据")
        print()
        
        # 检查最近30天的信号 (用于测试)
        print("🔍 检查最近30天的信号 (测试用)...")
        signal_info = check_for_new_signals(days_back=30)
        
        if signal_info['has_signal']:
            print(f"✅ 发现 {signal_info['signal_count']} 个信号!")
            print()
            print("最新信号:")
            latest = signal_info['latest_signal']
            print(f"  日期: {latest['date']}")
            print(f"  动作: {latest['action']}")
            print(f"  数量: {latest['quantity']:,}")
            print(f"  价格: ${latest['price']:.2f}")
            print(f"  原因: {latest['reason']}")
            print()
            
            # 发送邮件
            print("📧 发送测试邮件...")
            
            # 获取当前价格
            current_price = bars[-1].close
            
            # 确定动作
            action_str = str(latest['action']).upper()
            if 'BUY' in action_str:
                action = 'BUY'
            elif 'SELL' in action_str:
                action = 'SELL'
            else:
                action = action_str
            
            # 发送邮件
            success = email_service.send_signal_alert(
                symbol="TSLA",
                action=action,
                quantity=latest['quantity'],
                price=current_price,
                reason=latest['reason'],
                signal_date=latest['date'],
                strategy_name="日度策略 (动量交易)"
            )
            
            if success:
                print()
                print("✅ 测试邮件发送成功!")
                print("   请检查邮箱: qsoft@139.com")
            else:
                print()
                print("❌ 测试邮件发送失败!")
        else:
            print("⚠️  最近30天没有信号,无法测试")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✅ 测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
