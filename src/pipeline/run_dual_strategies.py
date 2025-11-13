"""
双策略检查系统 - 带独立邮件通知

策略1: 周度策略 (趋势跟踪 + 动态仓位) - 每周检查
策略2: 日度策略 (动量 + 成交量) - 每天检查
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.pipeline.run_improved_strategy import ImprovedStrategy
from src.pipeline.run_daily_strategy import DailyTradingStrategy
from src.notification.email_service import EmailService


def check_for_new_signals(strategy_name: str, signal_file: Path, days_back: int = 7) -> dict:
    """
    检查是否有新的交易信号
    
    Args:
        strategy_name: 策略名称
        signal_file: 信号文件路径
        days_back: 检查最近几天的信号
    
    Returns:
        dict: 信号信息
    """
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
        'all_signals': signals_df.to_dict('records'),
        'strategy_name': strategy_name
    }
    
    if has_new_signal:
        # 获取最新的信号
        latest = recent_signals.iloc[-1]
        result['latest_signal'] = {
            'date': latest['date'].strftime('%Y-%m-%d'),
            'action': latest['action'],
            'quantity': int(latest['quantity']),
            'reason': latest.get('reason', ''),
            'price': latest.get('price', 0.0)
        }
    else:
        result['latest_signal'] = None
    
    return result


def run_weekly_strategy() -> dict:
    """
    运行周度策略
    
    Returns:
        dict: 策略结果
    """
    print("=" * 80)
    print("📊 策略1: 周度策略 (趋势跟踪)")
    print("=" * 80)
    print()
    
    # 加载数据
    data_path = project_root / "data" / "sample_tsla.csv"
    loader = CSVPriceLoader(data_path)
    bars = list(loader.load())
    
    # 运行策略
    strategy = ImprovedStrategy(
        initial_cash=100000.0,
        max_position_pct=0.6,
        trend_filter_window=50,
        position_scaling=True
    )
    
    results = strategy.run_backtest(bars)
    
    # 检查新信号
    signal_file = project_root / "backtest_results" / "improved" / "signals_improved.csv"
    signal_info = check_for_new_signals("周度策略", signal_file, days_back=7)
    
    return {
        'strategy_name': '周度策略 (趋势跟踪)',
        'results': results,
        'signal_info': signal_info,
        'bars': bars
    }


def run_daily_strategy() -> dict:
    """
    运行日度策略
    
    Returns:
        dict: 策略结果
    """
    print()
    print("=" * 80)
    print("📊 策略2: 日度策略 (动量交易)")
    print("=" * 80)
    print()
    
    # 加载数据
    data_path = project_root / "data" / "sample_tsla.csv"
    loader = CSVPriceLoader(data_path)
    bars = list(loader.load())
    
    # 运行策略
    strategy = DailyTradingStrategy(
        initial_cash=100000.0,
        position_pct=0.6,
        momentum_window=5,
        trend_window=20,
        volume_threshold=1.3,
        profit_target=0.05,
        stop_loss=0.02
    )
    
    results = strategy.run_backtest(bars)
    
    # 检查新信号 (只检查最近1天)
    signal_file = project_root / "backtest_results" / "daily" / "signals_daily.csv"
    signal_info = check_for_new_signals("日度策略", signal_file, days_back=1)
    
    return {
        'strategy_name': '日度策略 (动量交易)',
        'results': results,
        'signal_info': signal_info,
        'bars': bars
    }


def send_strategy_email(strategy_data: dict, email_service: EmailService):
    """
    发送策略邮件
    
    Args:
        strategy_data: 策略数据
        email_service: 邮件服务
    """
    strategy_name = strategy_data['strategy_name']
    signal_info = strategy_data['signal_info']
    bars = strategy_data['bars']
    
    print(f"\n📧 发送 {strategy_name} 邮件通知...")
    
    if signal_info['has_signal']:
        latest = signal_info['latest_signal']
        current_price = latest.get('price', bars[-1].close)
        
        # 发送信号提醒
        email_service.send_signal_alert(
            symbol="TSLA",
            action=latest['action'],
            quantity=latest['quantity'],
            price=current_price,
            reason=f"[{strategy_name}] {latest['reason']}",
            signal_date=latest['date']
        )
    else:
        # 发送无信号通知
        email_service.send_weekly_summary(
            has_signal=False,
            signal_count=0,
            latest_signal=None,
            error_message=None
        )


def main():
    """主函数 - 运行所有策略并发送邮件"""
    print("=" * 80)
    print("🚀 TSLA 双策略检查系统")
    print("=" * 80)
    print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    
    try:
        # 运行策略1: 周度策略
        weekly_data = run_weekly_strategy()
        
        # 运行策略2: 日度策略
        daily_data = run_daily_strategy()
        
        # 发送邮件
        print()
        print("=" * 80)
        print("📧 发送邮件通知")
        print("=" * 80)
        
        # 策略1邮件
        send_strategy_email(weekly_data, email_service)
        
        # 策略2邮件
        send_strategy_email(daily_data, email_service)
        
        # 总结
        print()
        print("=" * 80)
        print("✅ 双策略检查完成!")
        print("=" * 80)
        print()
        
        print("📊 结果总结:")
        print()
        
        print(f"【{weekly_data['strategy_name']}】")
        if weekly_data['signal_info']['has_signal']:
            latest = weekly_data['signal_info']['latest_signal']
            print(f"  🚨 发现新信号: {latest['action']} {latest['quantity']} 股")
            print(f"  📅 信号日期: {latest['date']}")
        else:
            print(f"  ✅ 无新信号")
        print()
        
        print(f"【{daily_data['strategy_name']}】")
        if daily_data['signal_info']['has_signal']:
            latest = daily_data['signal_info']['latest_signal']
            print(f"  🚨 发现新信号: {latest['action']} {latest['quantity']} 股")
            print(f"  📅 信号日期: {latest['date']}")
        else:
            print(f"  ✅ 无新信号")
        print()
        
        print("💡 提示:")
        print("  - 两个策略的邮件已分别发送到: qsoft@139.com")
        print("  - 请检查邮箱(包括垃圾邮件文件夹)")
        print("  - 如有新信号,请及时在 Firstrade 执行交易")
        print()
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
