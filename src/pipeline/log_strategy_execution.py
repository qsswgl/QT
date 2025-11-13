"""
策略执行日志记录器
自动记录每日策略执行情况，便于每周回顾分析
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def read_latest_signal():
    """读取最新信号"""
    signal_file = project_root / "backtest_results" / "daily" / "signals_daily.csv"
    
    if not signal_file.exists():
        return None
    
    signals_df = pd.read_csv(signal_file)
    if signals_df.empty:
        return None
    
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    latest = signals_df.iloc[-1]
    
    return {
        'date': latest['date'].strftime('%Y-%m-%d'),
        'action': str(latest['action']),
        'quantity': int(latest['quantity']),
        'price': float(latest['price']),
        'reason': str(latest['reason'])
    }


def read_latest_price():
    """读取最新价格数据"""
    data_file = project_root / "data" / "sample_tsla.csv"
    
    if not data_file.exists():
        return None
    
    df = pd.read_csv(data_file)
    if df.empty:
        return None
    
    latest = df.iloc[-1]
    prev_5 = df.iloc[-6:-1] if len(df) >= 6 else df.iloc[:-1]
    
    return {
        'date': latest['date'],
        'close': float(latest['close']),
        'volume': int(latest['volume']),
        'avg_volume_5d': int(prev_5['volume'].mean()) if not prev_5.empty else 0,
        'price_change': float((latest['close'] - prev_5.iloc[-1]['close']) / prev_5.iloc[-1]['close'] * 100) if not prev_5.empty else 0
    }


def count_recent_signals(days=7):
    """统计最近N天的信号数量"""
    signal_file = project_root / "backtest_results" / "daily" / "signals_daily.csv"
    
    if not signal_file.exists():
        return 0
    
    signals_df = pd.read_csv(signal_file)
    if signals_df.empty:
        return 0
    
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    cutoff = datetime.now() - timedelta(days=days)
    recent = signals_df[signals_df['date'] >= cutoff]
    
    return len(recent)


def generate_daily_log_entry(strategy_type="日度策略"):
    """生成每日日志条目"""
    now = datetime.now()
    weekday_cn = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekday_cn[now.weekday()]
    
    # 读取数据
    latest_signal = read_latest_signal()
    latest_price = read_latest_price()
    recent_signal_count = count_recent_signals(7)
    
    # 格式化各项数据
    data_update_status = "✅ 成功" if latest_price else "❌ 失败"
    data_date = latest_price['date'] if latest_price else "N/A"
    data_integrity = "✅ 良好" if latest_price else "⚠️ 缺失"
    
    # 市场数据
    if latest_price:
        close_price = f"${latest_price['close']:.2f}"
        price_change = f"{latest_price['price_change']:+.2f}% (较前日)"
        volume = f"{latest_price['volume']:,}"
        avg_volume = f"{latest_price['avg_volume_5d']:,}"
    else:
        close_price = "N/A"
        price_change = "N/A"
        volume = "N/A"
        avg_volume = "N/A"
    
    # 信号数据
    signal_date = latest_signal['date'] if latest_signal else "无历史信号"
    signal_action = latest_signal['action'] if latest_signal else "N/A"
    signal_price = f"${latest_signal['price']:.2f}" if latest_signal else "N/A"
    signal_reason = latest_signal['reason'] if latest_signal else "N/A"
    
    # 操作建议
    operation_advice = "⚠️ 有新信号 - 请查看邮件" if recent_signal_count > 0 else "✅ 观望 - 无新信号"
    
    # 回顾数据
    if latest_signal:
        last_operation = f"{latest_signal['date']} {latest_signal['action']} @ ${latest_signal['price']:.2f}"
    else:
        last_operation = "无历史操作"
    
    current_price_review = f"${latest_price['close']:.2f}" if latest_price else "N/A"
    
    if latest_price and latest_signal:
        price_diff = latest_price['close'] - latest_signal['price']
        price_diff_pct = (price_diff / latest_signal['price']) * 100
        price_gap = f"${price_diff:.2f} ({price_diff_pct:+.2f}%)"
    else:
        price_gap = "N/A"
    
    # 构建日志
    log_entry = f"""
### {now.strftime('%Y-%m-%d')} (周{weekday})

**执行信息**:
- 执行时间: {now.strftime('%H:%M')}
- 策略类型: {strategy_type}
- 数据更新: {data_update_status}

**数据状态**:
- 最新数据日期: {data_date}
- 数据完整性: {data_integrity}
- 数据来源: (请手动填写: Yahoo Finance / Alpha Vantage / Twelve Data)

**市场状态**:
- TSLA最新收盘: {close_price}
- 价格变动: {price_change}
- 成交量: {volume}
- 5日平均成交量: {avg_volume}

**信号情况**:
- 最新信号日期: {signal_date}
- 信号类型: {signal_action}
- 信号价格: {signal_price}
- 信号原因: {signal_reason}
- 近7天信号数: {recent_signal_count}

**策略决策**:
- 当前持仓: (请根据实际情况填写: 空仓 / 持仓XXX股)
- 操作建议: {operation_advice}
- 决策依据: 
  - (请根据信号情况填写)

**回顾分析**:
- 上次操作: {last_operation}
- 当前价格: {current_price_review}
- 价差: {price_gap}
- 策略表现: (请每周回顾时填写: ✅ 正确 / ❌ 错误 / ⚠️ 待观察)

**备注**:
- (请添加任何特殊情况、系统问题或市场观察)

---
"""
    
    return log_entry


def append_to_log(entry):
    """追加日志到文件"""
    log_file = project_root / "STRATEGY_EXECUTION_LOG.md"
    
    if not log_file.exists():
        print("❌ 日志文件不存在，请先创建")
        return False
    
    # 读取现有内容
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到插入位置（在模板之前）
    template_marker = "## 📝 记录模板"
    
    if template_marker in content:
        # 在模板前插入新日志
        parts = content.split(template_marker)
        new_content = parts[0] + entry + "\n" + template_marker + parts[1]
    else:
        # 如果找不到标记，追加到文件末尾
        new_content = content + "\n" + entry
    
    # 写回文件
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 日志已记录到: {log_file}")
    return True


def main():
    """主函数"""
    print("=" * 70)
    print("📊 策略执行日志记录器")
    print("=" * 70)
    print()
    
    # 生成日志条目
    print("正在生成日志条目...")
    entry = generate_daily_log_entry()
    
    print("\n生成的日志内容:")
    print("-" * 70)
    print(entry)
    print("-" * 70)
    print()
    
    # 追加到日志文件
    print("正在保存到日志文件...")
    if append_to_log(entry):
        print()
        print("=" * 70)
        print("✅ 日志记录完成!")
        print("=" * 70)
        print()
        print("💡 提示:")
        print("  - 请查看并完善日志中的手动填写项")
        print("  - 每周日进行一次完整回顾")
        print("  - 分析策略准确性和改进方向")
        print()
    else:
        print()
        print("❌ 日志记录失败")
        print()


if __name__ == "__main__":
    main()
