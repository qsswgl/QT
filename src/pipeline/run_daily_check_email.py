"""
日度策略检查 - 带邮件推送 (完全参考周度策略实现)
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


def check_for_new_signals() -> dict:
    """
    检查是否有新的交易信号 (日度策略)
    
    Returns:
        dict: {
            'has_signal': bool,
            'signal_count': int,
            'latest_signal': dict or None,
            'all_signals': list
        }
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
    
    # 获取最近1天的信号 (日度策略只检查最近1天)
    one_day_ago = datetime.now() - timedelta(days=1)
    recent_signals = signals_df[signals_df['date'] >= one_day_ago]
    
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


def get_current_position(bars: list) -> dict:
    """
    获取当前持仓信息
    
    Args:
        bars: 价格数据列表
        
    Returns:
        dict: 持仓信息 {symbol, quantity, avg_price, current_price, market_value, profit_loss, profit_loss_pct}
    """
    trades_file = project_root / "backtest_results" / "daily" / "trades_daily.csv"
    
    if not trades_file.exists():
        return {
            'symbol': 'TSLA',
            'quantity': 0,
            'avg_price': 0,
            'current_price': bars[-1].close if bars else 0,
            'market_value': 0,
            'profit_loss': 0,
            'profit_loss_pct': 0
        }
    
    # 读取交易记录
    trades_df = pd.read_csv(trades_file)
    
    if trades_df.empty:
        return {
            'symbol': 'TSLA',
            'quantity': 0,
            'avg_price': 0,
            'current_price': bars[-1].close if bars else 0,
            'market_value': 0,
            'profit_loss': 0,
            'profit_loss_pct': 0
        }
    
    # 获取当前价格
    current_price = bars[-1].close if bars else 0
    
    # 计算当前持仓
    quantity = 0
    total_cost = 0
    
    for _, trade in trades_df.iterrows():
        if trade['action'] == 'BUY':
            quantity += trade['quantity']
            total_cost += trade['total']
        elif trade['action'] == 'SELL':
            if quantity > 0:
                # 按比例减少成本
                sell_ratio = trade['quantity'] / quantity
                total_cost *= (1 - sell_ratio)
                quantity -= trade['quantity']
    
    # 计算持仓信息
    if quantity > 0:
        avg_price = total_cost / quantity
        market_value = quantity * current_price
        profit_loss = market_value - total_cost
        profit_loss_pct = (profit_loss / total_cost) * 100 if total_cost > 0 else 0
    else:
        avg_price = 0
        market_value = 0
        profit_loss = 0
        profit_loss_pct = 0
    
    return {
        'symbol': 'TSLA',
        'quantity': int(quantity),
        'avg_price': avg_price,
        'current_price': current_price,
        'market_value': market_value,
        'profit_loss': profit_loss,
        'profit_loss_pct': profit_loss_pct
    }


def run_daily_check_with_email():
    """运行日度检查并发送邮件通知 (完全参考周度策略的实现)"""
    print("=" * 80)
    print("📊 TSLA 日度策略检查 (邮件推送版)")
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
        
        # 步骤2: 运行日度策略
        print("[步骤 2/4] 🚀 运行日度策略...")
        strategy = DailyTradingStrategy(
            initial_cash=100000.0,
            position_pct=0.6,
            momentum_window=5,
            volume_threshold=1.3,
            profit_target=0.05,
            stop_loss=0.02
        )
        
        results = strategy.run_backtest(bars)
        print()
        
        # 步骤3: 检查新信号
        print("[步骤 3/4] 🔍 检查新交易信号 (最近1天)...")
        signal_info = check_for_new_signals()
        
        # 获取当前持仓信息
        position_info = get_current_position(bars)
        print(f"📊 当前持仓: {position_info['quantity']} 股 @ ${position_info['avg_price']:.2f}")
        print()
        
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
            
            # 发送信号提醒邮件 - 使用与周度策略完全相同的方式
            print("[步骤 4/4] 📧 发送邮件提醒...")
            
            # 获取当前价格(使用最新收盘价)
            current_price = bars[-1].close
            
            # 确定动作
            action_str = str(latest['action']).upper()
            if 'BUY' in action_str:
                action = 'BUY'
            elif 'SELL' in action_str:
                action = 'SELL'
            else:
                action = action_str
            
            # 发送邮件 - 完全参考周度策略的调用方式
            email_service.send_signal_alert(
                symbol="TSLA",
                action=action,
                quantity=latest['quantity'],
                price=current_price,  # 使用当前价格而不是信号价格
                reason=latest['reason'],
                signal_date=latest['date'],
                strategy_name="日度策略 (动量交易)"
            )
        else:
            print("✓ 暂无新交易信号")
            print()
            
            # 发送每日总结邮件（包含持仓信息）
            print("[步骤 4/4] 📧 发送每日总结...")
            email_service.send_daily_summary(
                has_signal=False,
                signal_count=0,
                latest_signal=None,
                error_message=None,
                position_info=position_info,
                symbol="TSLA"
            )
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        error_message = str(e)
        
        # 发送错误通知邮件
        print()
        print("📧 发送错误通知邮件...")
        email_service.send_daily_summary(
            has_signal=False,
            signal_count=0,
            latest_signal=None,
            error_message=error_message,
            symbol="TSLA"
        )
    
    print()
    print("=" * 80)
    print("✅ 日度策略检查完成!")
    print("=" * 80)
    print()
    print("💡 提示:")
    print("  - 邮件已发送至: qsswgl@gmail.com")
    print("  - 请检查你的邮箱(包括垃圾邮件文件夹)")
    print("  - 如有新信号,请及时在 Firstrade 执行交易")
    print()


if __name__ == "__main__":
    run_daily_check_with_email()
