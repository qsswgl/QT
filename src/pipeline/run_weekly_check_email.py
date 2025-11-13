"""
策略信号检查 - 带邮件推送

支持两种策略:
- weekly: 周度策略 (趋势跟踪)  
- dai    if signals_df.empty:
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': [],
            'strategy_name': strategy_name
        }
    
    # 转换日期
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    
    # 获取最近N天的信号
    cutoff_date = datetime.now() - timedelta(days=days_back)易)
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import argparse

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.pipeline.run_improved_strategy import ImprovedStrategy
from src.notification.email_service import EmailService


def check_for_new_signals(strategy_type: str = 'weekly', days_back: int = None) -> dict:
    """
    检查是否有新的交易信号
    
    Args:
        strategy_type: 策略类型 ('weekly' or 'daily')
        days_back: 检查最近几天的信号
    
    Returns:
        dict: {
            'has_signal': bool,
            'signal_count': int,
            'latest_signal': dict or None,
            'all_signals': list,
            'strategy_name': str
        }
    """
    # 根据策略类型选择文件和名称
    if strategy_type == 'daily':
        signal_file = project_root / "backtest_results" / "daily" / "signals_daily.csv"
        strategy_name = "日度策略 (动量交易)"
        if days_back is None:
            days_back = 1  # 日度策略默认检查最近1天
    else:  # weekly
        signal_file = project_root / "backtest_results" / "improved" / "signals_improved.csv"
        strategy_name = "周度策略 (趋势跟踪)"
        if days_back is None:
            days_back = 7  # 周度策略默认检查最近7天
    
    # 计算cutoff日期
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    if not signal_file.exists():
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': [],
            'strategy_name': strategy_name
        }
    
    # 读取信号文件
    signals_df = pd.read_csv(signal_file)
    
    if signals_df.empty:
        return {
            'has_signal': False,
            'signal_count': 0,
            'latest_signal': None,
            'all_signals': [],
            'strategy_name': strategy_name
        }
    
    # 转换日期
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    
    # 获取最近N天的信号
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
        }
    else:
        result['latest_signal'] = None
    
    return result


def run_weekly_check_with_email():
    """运行每周检查并发送邮件通知"""
    print("=" * 80)
    print("📊 TSLA 策略每周检查 (邮件推送版)")
    print("=" * 80)
    print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    error_message = None
    
    try:
        # 步骤1: 加载数据
        print("[步骤 1/4] 📂 加载历史数据...")
        data_path = project_root / "data" / "sample_tsla.csv"
        
        if not data_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {data_path}")
        
        loader = CSVPriceLoader(data_path)
        bars = list(loader.load())
        print(f"✓ 已加载 {len(bars)} 条历史数据")
        print(f"  日期范围: {bars[0].date} 至 {bars[-1].date}")
        print()
        
        # 步骤2: 运行策略
        print("[步骤 2/4] 🚀 运行改进策略...")
        strategy = ImprovedStrategy(
            initial_cash=100000.0,
            max_position_pct=0.6,
            trend_filter_window=50,
            position_scaling=True
        )
        
        results = strategy.run_backtest(bars)
        print()
        
        # 步骤3: 检查新信号
        print("[步骤 3/4] 🔍 检查新交易信号...")
        signal_info = check_for_new_signals()
        
        if signal_info['has_signal']:
            print(f"✅ 发现 {signal_info['signal_count']} 个新信号!")
            print()
            print("最新信号:")
            latest = signal_info['latest_signal']
            print(f"  日期: {latest['date']}")
            print(f"  动作: {latest['action']}")
            print(f"  数量: {latest['quantity']:,}")
            print(f"  原因: {latest['reason']}")
            print()
            
            # 发送信号提醒邮件
            print("[步骤 4/4] 📧 发送邮件提醒...")
            
            # 获取当前价格(使用最新收盘价)
            current_price = bars[-1].close
            
            email_service.send_signal_alert(
                symbol="TSLA",
                action=latest['action'],
                quantity=latest['quantity'],
                price=current_price,
                reason=latest['reason'],
                signal_date=latest['date']
            )
        else:
            print("✓ 暂无新交易信号")
            print()
            
            # 发送每周总结邮件
            print("[步骤 4/4] 📧 发送每周总结...")
            email_service.send_weekly_summary(
                has_signal=False,
                signal_count=0,
                latest_signal=None,
                error_message=None
            )
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        error_message = str(e)
        
        # 发送错误通知邮件
        print()
        print("📧 发送错误通知邮件...")
        email_service.send_weekly_summary(
            has_signal=False,
            signal_count=0,
            latest_signal=None,
            error_message=error_message
        )
    
    print()
    print("=" * 80)
    print("✅ 每周检查完成!")
    print("=" * 80)
    print()
    print("💡 提示:")
    print("  - 邮件已发送至: qsswgl@gmail.com")
    print("  - 请检查你的邮箱(包括垃圾邮件文件夹)")
    print("  - 如有新信号,请及时在 Firstrade 执行交易")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='策略信号检查和邮件通知')
    parser.add_argument('--strategy',
                        choices=['weekly', 'daily'],
                        default='weekly',
                        help='策略类型: weekly (周度) 或 daily (日度)')
    parser.add_argument('--days',
                        type=int,
                        default=None,
                        help='检查最近几天的信号 (可选)')
    
    args = parser.parse_args()
    
    # 根据策略类型调用不同的检查
    if args.strategy == 'weekly':
        run_weekly_check_with_email()
    else:  # daily
        # 对于日度策略,只检查信号并发送邮件
        print("=" * 80)
        print("📊 TSLA 日度策略检查 (邮件推送版)")
        print("=" * 80)
        print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        days_back = args.days if args.days is not None else 1
        signal_info = check_for_new_signals(strategy_type='daily', days_back=days_back)
        
        print(f"📊 检查最近 {days_back} 天的信号")
        print(f"策略: {signal_info['strategy_name']}")
        print()
        
        if signal_info['has_signal']:
            print(f"✅ 发现 {signal_info['signal_count']} 个新信号!")
            
            # 发送邮件
            email_service = EmailService()
            latest = signal_info['latest_signal']
            
            print()
            print("📧 发送邮件通知...")
            
            # 确定动作类型
            action_str = str(latest['action']).upper()
            if 'BUY' in action_str:
                action = 'BUY'
            elif 'SELL' in action_str:
                action = 'SELL'
            else:
                action = action_str
            
            # 发送邮件 - 使用与周度策略相同的方式
            email_service.send_signal_alert(
                symbol="TSLA",
                action=action,
                quantity=int(latest.get('quantity', latest.get('shares', 0))),
                price=float(latest.get('price', 0)),
                reason=str(latest.get('reason', '')),
                signal_date=latest.get('date', ''),
                strategy_name=signal_info['strategy_name']
            )
            
            print(f"✅ 邮件已发送至: qsswgl@gmail.com")
        else:
            print("✅ 最近没有新信号")
            print("   无需发送邮件")
        
        print()
        print("=" * 80)
        print("✅ 日度策略检查完成!")
        print("=" * 80)
