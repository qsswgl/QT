"""
每周策略回顾分析工具
分析过去7天的策略执行情况，评估策略正确性
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def parse_log_entries(content, days=7):
    """解析日志条目"""
    entries = []
    
    # 匹配日志条目
    pattern = r'### (\d{4}-\d{2}-\d{2}) \(周.*?\)\n(.*?)(?=\n### \d{4}-\d{2}-\d{2}|\n## 📝 记录模板|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    cutoff = datetime.now() - timedelta(days=days)
    
    for date_str, entry_content in matches:
        entry_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        if entry_date >= cutoff:
            # 解析关键信息
            entry = {
                'date': date_str,
                'datetime': entry_date,
                'content': entry_content
            }
            
            # 提取市场数据
            close_match = re.search(r'TSLA最新收盘:\s*\$?([\d.]+)', entry_content)
            if close_match:
                entry['close'] = float(close_match.group(1))
            
            # 提取信号信息
            signal_date_match = re.search(r'最新信号日期:\s*(\d{4}-\d{2}-\d{2}|无历史信号)', entry_content)
            if signal_date_match:
                entry['signal_date'] = signal_date_match.group(1)
            
            signal_action_match = re.search(r'信号类型:\s*(\w+|N/A)', entry_content)
            if signal_action_match:
                entry['signal_action'] = signal_action_match.group(1)
            
            signal_price_match = re.search(r'信号价格:\s*\$?([\d.]+)', entry_content)
            if signal_price_match:
                entry['signal_price'] = float(signal_price_match.group(1))
            
            # 提取近7天信号数
            signal_count_match = re.search(r'近7天信号数:\s*(\d+)', entry_content)
            if signal_count_match:
                entry['signal_count_7d'] = int(signal_count_match.group(1))
            
            # 提取价差
            price_gap_match = re.search(r'价差:\s*\$?([\d.-]+)\s*\(([\d.+-]+)%\)', entry_content)
            if price_gap_match:
                entry['price_gap'] = float(price_gap_match.group(1))
                entry['price_gap_pct'] = float(price_gap_match.group(2))
            
            entries.append(entry)
    
    # 按日期排序
    entries.sort(key=lambda x: x['datetime'])
    
    return entries


def analyze_strategy_performance(entries):
    """分析策略表现"""
    if not entries:
        return None
    
    # 统计信息
    total_days = len(entries)
    signal_days = sum(1 for e in entries if e.get('signal_count_7d', 0) > 0)
    
    # 价格变化
    prices = [e.get('close') for e in entries if 'close' in e]
    if len(prices) >= 2:
        price_change = prices[-1] - prices[0]
        price_change_pct = (price_change / prices[0]) * 100
    else:
        price_change = 0
        price_change_pct = 0
    
    # 最新信号分析
    latest_signal = None
    for e in reversed(entries):
        if 'signal_date' in e and e['signal_date'] != '无历史信号' and e['signal_date'] != 'N/A':
            latest_signal = {
                'date': e['signal_date'],
                'action': e.get('signal_action', 'N/A'),
                'price': e.get('signal_price', 0),
                'current_price': entries[-1].get('close', 0)
            }
            
            if latest_signal['price'] > 0 and latest_signal['current_price'] > 0:
                latest_signal['gain'] = latest_signal['current_price'] - latest_signal['price']
                latest_signal['gain_pct'] = (latest_signal['gain'] / latest_signal['price']) * 100
            
            break
    
    return {
        'total_days': total_days,
        'signal_days': signal_days,
        'price_start': prices[0] if prices else 0,
        'price_end': prices[-1] if prices else 0,
        'price_change': price_change,
        'price_change_pct': price_change_pct,
        'latest_signal': latest_signal
    }


def generate_weekly_review(entries, analysis):
    """生成每周回顾报告"""
    now = datetime.now()
    
    review = f"""
## 📊 每周策略回顾 ({now.strftime('%Y-%m-%d')})

**回顾周期**: {entries[0]['date']} 至 {entries[-1]['date']} (共 {analysis['total_days']} 天)

### 📈 市场表现

- **期初价格**: ${analysis['price_start']:.2f}
- **期末价格**: ${analysis['price_end']:.2f}
- **价格变化**: ${analysis['price_change']:.2f} ({analysis['price_change_pct']:+.2f}%)
- **趋势判断**: {"📈 上涨趋势" if analysis['price_change'] > 0 else "📉 下跌趋势" if analysis['price_change'] < 0 else "➡️ 横盘整理"}

### 🎯 信号分析

- **信号活跃度**: {analysis['signal_days']}/{analysis['total_days']} 天有新信号
- **信号频率**: {"⚠️ 频繁" if analysis['signal_days'] >= 3 else "✅ 正常" if analysis['signal_days'] > 0 else "💤 无信号"}

"""
    
    if analysis['latest_signal']:
        sig = analysis['latest_signal']
        
        # 判断信号表现
        if sig['action'] == 'BUY':
            if sig.get('gain_pct', 0) > 0:
                performance = "✅ 正确 - 买入后价格上涨"
            else:
                performance = "❌ 错误 - 买入后价格下跌"
        elif sig['action'] == 'SELL':
            if sig.get('gain_pct', 0) < 0:
                performance = "✅ 正确 - 卖出后价格下跌"
            else:
                performance = "⚠️ 待观察 - 卖出后价格上涨"
        else:
            performance = "⚠️ 待评估"
        
        review += f"""
**最近信号**:
- 信号日期: {sig['date']}
- 操作类型: {sig['action']}
- 信号价格: ${sig['price']:.2f}
- 当前价格: ${sig['current_price']:.2f}
- 价差: ${sig.get('gain', 0):.2f} ({sig.get('gain_pct', 0):+.2f}%)
- **策略表现**: {performance}

"""
    else:
        review += """
**最近信号**: 近期无新信号

"""
    
    # 每日执行摘要
    review += """
### 📋 每日执行摘要

| 日期 | 最新价格 | 信号状态 | 操作建议 |
|------|---------|---------|---------|
"""
    
    for entry in entries:
        date = entry['date']
        price = f"${entry.get('close', 0):.2f}" if 'close' in entry else "N/A"
        signal_count = entry.get('signal_count_7d', 0)
        signal_status = "🟢 有信号" if signal_count > 0 else "⚪ 无信号"
        advice = "⚠️ 查看邮件" if signal_count > 0 else "✅ 观望"
        
        review += f"| {date} | {price} | {signal_status} | {advice} |\n"
    
    review += """

### 🔍 策略评估

**优势**:
- (请根据本周表现填写)

**问题**:
- (请根据本周表现填写)

**改进建议**:
- (请根据分析结果提出改进方向)

### 📝 下周计划

- (请制定下周策略调整计划)

---

"""
    
    return review


def append_weekly_review(review):
    """追加周回顾到日志文件"""
    log_file = project_root / "STRATEGY_EXECUTION_LOG.md"
    
    if not log_file.exists():
        print("❌ 日志文件不存在")
        return False
    
    # 读取现有内容
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在文件开头插入（在标题之后）
    title_marker = "# 📊 策略执行日志"
    
    if title_marker in content:
        parts = content.split(title_marker, 1)
        new_content = parts[0] + title_marker + "\n" + review + "\n" + parts[1]
    else:
        new_content = review + "\n" + content
    
    # 写回文件
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 周回顾已添加到: {log_file}")
    return True


def main():
    """主函数"""
    print("=" * 70)
    print("📊 每周策略回顾分析")
    print("=" * 70)
    print()
    
    log_file = project_root / "STRATEGY_EXECUTION_LOG.md"
    
    if not log_file.exists():
        print("❌ 日志文件不存在，请先执行日度策略")
        return
    
    # 读取日志文件
    print("正在读取策略执行日志...")
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析最近7天的条目
    print("正在分析最近7天的执行记录...")
    entries = parse_log_entries(content, days=7)
    
    if not entries:
        print("⚠️ 未找到最近7天的执行记录")
        print("提示: 请确保已运行过日度策略")
        return
    
    print(f"✅ 找到 {len(entries)} 条记录")
    print()
    
    # 分析策略表现
    print("正在分析策略表现...")
    analysis = analyze_strategy_performance(entries)
    
    if not analysis:
        print("❌ 分析失败，数据不完整")
        return
    
    # 生成周回顾
    print("正在生成周回顾报告...")
    review = generate_weekly_review(entries, analysis)
    
    print("\n生成的周回顾:")
    print("-" * 70)
    print(review)
    print("-" * 70)
    print()
    
    # 保存到日志文件
    print("正在保存周回顾...")
    if append_weekly_review(review):
        print()
        print("=" * 70)
        print("✅ 周回顾分析完成!")
        print("=" * 70)
        print()
        print("💡 建议:")
        print("  - 请完善周回顾中的策略评估")
        print("  - 根据分析结果调整策略参数")
        print("  - 制定下周的操作计划")
        print()
    else:
        print()
        print("❌ 保存失败")
        print()


if __name__ == "__main__":
    main()
