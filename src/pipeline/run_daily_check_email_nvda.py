"""
NVDA日度策略检查 - 带邮件推送
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.pipeline.run_daily_strategy_nvda import DailyTradingStrategyNVDA
from src.notification.email_service import EmailService


def check_for_new_signals() -> dict:
    """检查是否有新的交易信号 (NVDA日度策略)"""
    signal_file = project_root / "NVDA" / "backtest_results" / "daily" / "signals_daily.csv"
    
    if not signal_file.exists():
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': []
        }
    
    signals_df = pd.read_csv(signal_file)
    
    if signals_df.empty:
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': []
        }
    
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    
    one_day_ago = datetime.now() - timedelta(days=1)
    recent_signals = signals_df[signals_df['date'] >= one_day_ago]
    
    has_new_signal = len(recent_signals) > 0
    
    result = {
        'has_signal': has_new_signal,
        'signal_count': len(recent_signals),
        'all_signals': signals_df.to_dict('records')
    }
    
    if has_new_signal:
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


def run_daily_check_with_email():
    """运行NVDA日度检查并发送邮件通知"""
    print("=" * 80)
    print("📊 NVDA 日度策略检查 (邮件推送版)")
    print("=" * 80)
    print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    error_message = None
    
    try:
        print("[步骤 1/4] 📂 加载NVDA历史数据...")
        data_path = project_root / "NVDA" / "data" / "sample_nvda.csv"
        
        if not data_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {data_path}")
        
        loader = CSVPriceLoader(data_path)
        bars = list(loader.load())
        print(f"✓ 已加载 {len(bars)} 条历史数据")
        print(f"  日期范围: {bars[0].date} 至 {bars[-1].date}")
        print()
        
        print("[步骤 2/4] 🚀 运行NVDA日度策略...")
        strategy = DailyTradingStrategyNVDA(
            initial_cash=100000.0,
            position_pct=0.6,
            momentum_window=5,
            volume_threshold=1.3,
            profit_target=0.05,
            stop_loss=0.02
        )
        
        results = strategy.run_backtest(bars)
        print()
        
        print("[步骤 3/4] 🔍 检查新交易信号 (最近1天)...")
        signal_info = check_for_new_signals()
        
        if signal_info['has_signal']:
            print(f"✅ 发现 {signal_info['signal_count']} 个新信号!")
            print()
            print("最新信号:")
            latest = signal_info['latest_signal']
            print(f"  日期: {latest['date']}")
            print(f"  动作: {latest['action']}")
            print(f"  数量: {latest['quantity']:,}")
            print(f"  价格: ${latest['price']:.2f}")
            print(f"  原因: {latest['reason']}")
            print()
            
            print("[步骤 4/4] 📧 发送邮件提醒...")
            
            current_price = bars[-1].close
            
            action_str = str(latest['action']).upper()
            if 'BUY' in action_str:
                action = 'BUY'
            elif 'SELL' in action_str:
                action = 'SELL'
            else:
                action = action_str
            
            email_service.send_signal_alert(
                symbol="NVDA",
                action=action,
                quantity=latest['quantity'],
                price=current_price,
                reason=latest['reason'],
                signal_date=latest['date'],
                strategy_name="NVDA日度策略 (动量交易)"
            )
        else:
            print("✓ 暂无新交易信号")
            print()
            
            print("[步骤 4/4] 📧 发送每日总结...")
            email_service.send_daily_summary(
                has_signal=False,
                signal_count=0,
                latest_signal=None,
                error_message=None
            )
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        error_message = str(e)
        
        print()
        print("📧 发送错误通知邮件...")
        email_service.send_daily_summary(
            has_signal=False,
            signal_count=0,
            latest_signal=None,
            error_message=error_message
        )
    
    print()
    print("=" * 80)
    print("✅ NVDA日度策略检查完成!")
    print("=" * 80)
    print()
    print("💡 提示:")
    print("  - 邮件已发送至: qsswgl@gmail.com")
    print("  - 请检查你的邮箱(包括垃圾邮件文件夹)")
    print("  - 如有新信号,请及时在 Firstrade 执行交易")
    print()


if __name__ == "__main__":
    run_daily_check_with_email()
