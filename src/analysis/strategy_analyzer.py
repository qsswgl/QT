"""
策略执行记录和分析系统

功能:
1. 自动收集每日策略执行结果
2. 生成周度分析报告
3. 生成月度分析报告
4. 策略考核和改进建议
"""
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class StrategyAnalyzer:
    """策略分析器"""
    
    def __init__(self, symbol: str, data_dir: Path = None):
        """
        初始化策略分析器
        
        Args:
            symbol: 股票代码 (TSLA/NVDA/INTC)
            data_dir: 数据目录路径
        """
        self.symbol = symbol
        
        if data_dir is None:
            if symbol == "TSLA":
                self.data_dir = project_root
            else:
                self.data_dir = project_root / symbol
        else:
            self.data_dir = data_dir
            
        self.daily_results_dir = self.data_dir / "backtest_results" / "daily"
        self.weekly_results_dir = self.data_dir / "backtest_results" / "weekly"
        
        # 执行记录文件
        self.execution_log_file = self.data_dir / "strategy_execution_records.json"
        
        # 确保记录文件存在
        if not self.execution_log_file.exists():
            self._init_execution_log()
    
    def _init_execution_log(self):
        """初始化执行记录文件"""
        # 确保目录存在
        self.execution_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        initial_data = {
            "symbol": self.symbol,
            "created_at": datetime.now().isoformat(),
            "executions": []
        }
        with open(self.execution_log_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    def record_execution(
        self,
        strategy_type: str,  # "daily" 或 "weekly"
        signals_count: int,
        new_signals_count: int,
        latest_signal_date: str = None,
        latest_signal_action: str = None,
        latest_signal_price: float = None,
        latest_price: float = None,
        price_change: float = None,
        notes: str = ""
    ):
        """
        记录一次策略执行
        
        Args:
            strategy_type: 策略类型 (daily/weekly)
            signals_count: 总信号数
            new_signals_count: 新信号数
            latest_signal_date: 最新信号日期
            latest_signal_action: 最新信号动作
            latest_signal_price: 最新信号价格
            latest_price: 当前价格
            price_change: 价格变动
            notes: 备注
        """
        # 读取现有记录
        with open(self.execution_log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加新记录
        execution = {
            "timestamp": datetime.now().isoformat(),
            "strategy_type": strategy_type,
            "signals_count": signals_count,
            "new_signals_count": new_signals_count,
            "latest_signal_date": latest_signal_date,
            "latest_signal_action": latest_signal_action,
            "latest_signal_price": latest_signal_price,
            "latest_price": latest_price,
            "price_change": price_change,
            "notes": notes
        }
        
        data["executions"].append(execution)
        
        # 保存
        with open(self.execution_log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 执行记录已保存: {self.symbol} {strategy_type}")
    
    def load_signals(self, strategy_type: str = "daily") -> pd.DataFrame:
        """
        加载信号数据
        
        Args:
            strategy_type: 策略类型 (daily/weekly)
        
        Returns:
            信号DataFrame
        """
        if strategy_type == "daily":
            signal_file = self.daily_results_dir / "signals_daily.csv"
        else:
            signal_file = self.weekly_results_dir / "signals_weekly.csv"
        
        if not signal_file.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(signal_file)
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    
    def load_trades(self, strategy_type: str = "daily") -> pd.DataFrame:
        """
        加载交易记录
        
        Args:
            strategy_type: 策略类型 (daily/weekly)
        
        Returns:
            交易DataFrame
        """
        if strategy_type == "daily":
            trade_file = self.daily_results_dir / "trades_daily.csv"
        else:
            trade_file = self.weekly_results_dir / "trades_weekly.csv"
        
        if not trade_file.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(trade_file)
        df['entry_date'] = pd.to_datetime(df['entry_date'])
        df['exit_date'] = pd.to_datetime(df['exit_date'])
        return df.sort_values('entry_date')
    
    def analyze_week(self, start_date: str = None) -> Dict:
        """
        分析一周的策略表现
        
        Args:
            start_date: 周开始日期 (格式: YYYY-MM-DD), 默认为本周
        
        Returns:
            周度分析结果字典
        """
        if start_date is None:
            today = datetime.now()
            # 找到本周一
            start_date = today - timedelta(days=today.weekday())
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        end_date = start_date + timedelta(days=6)
        
        # 加载数据
        daily_signals = self.load_signals("daily")
        weekly_signals = self.load_signals("weekly")
        daily_trades = self.load_trades("daily")
        weekly_trades = self.load_trades("weekly")
        
        # 筛选本周数据
        week_daily_signals = daily_signals[
            (daily_signals['date'] >= start_date) & 
            (daily_signals['date'] <= end_date)
        ]
        
        week_weekly_signals = weekly_signals[
            (weekly_signals['date'] >= start_date) & 
            (weekly_signals['date'] <= end_date)
        ]
        
        week_daily_trades = daily_trades[
            (daily_trades['entry_date'] >= start_date) & 
            (daily_trades['entry_date'] <= end_date)
        ]
        
        week_weekly_trades = weekly_trades[
            (weekly_trades['entry_date'] >= start_date) & 
            (weekly_trades['entry_date'] <= end_date)
        ]
        
        # 分析结果
        analysis = {
            "symbol": self.symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            "week_number": start_date.isocalendar()[1],
            
            "daily_strategy": {
                "signals_count": len(week_daily_signals),
                "buy_signals": len(week_daily_signals[week_daily_signals['action'] == 'BUY']),
                "sell_signals": len(week_daily_signals[week_daily_signals['action'] == 'SELL']),
                "trades_count": len(week_daily_trades),
                "profitable_trades": len(week_daily_trades[week_daily_trades['profit'] > 0]),
                "total_profit": week_daily_trades['profit'].sum() if len(week_daily_trades) > 0 else 0,
                "win_rate": (len(week_daily_trades[week_daily_trades['profit'] > 0]) / len(week_daily_trades) * 100) 
                            if len(week_daily_trades) > 0 else 0
            },
            
            "weekly_strategy": {
                "signals_count": len(week_weekly_signals),
                "buy_signals": len(week_weekly_signals[week_weekly_signals['action'] == 'BUY']),
                "sell_signals": len(week_weekly_signals[week_weekly_signals['action'] == 'SELL']),
                "trades_count": len(week_weekly_trades),
                "profitable_trades": len(week_weekly_trades[week_weekly_trades['profit'] > 0]),
                "total_profit": week_weekly_trades['profit'].sum() if len(week_weekly_trades) > 0 else 0,
                "win_rate": (len(week_weekly_trades[week_weekly_trades['profit'] > 0]) / len(week_weekly_trades) * 100) 
                            if len(week_weekly_trades) > 0 else 0
            }
        }
        
        return analysis
    
    def analyze_month(self, year: int = None, month: int = None) -> Dict:
        """
        分析一个月的策略表现
        
        Args:
            year: 年份, 默认为当前年
            month: 月份, 默认为当前月
        
        Returns:
            月度分析结果字典
        """
        if year is None or month is None:
            today = datetime.now()
            year = today.year
            month = today.month
        
        # 计算月初和月末
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # 加载数据
        daily_signals = self.load_signals("daily")
        weekly_signals = self.load_signals("weekly")
        daily_trades = self.load_trades("daily")
        weekly_trades = self.load_trades("weekly")
        
        # 筛选本月数据
        month_daily_signals = daily_signals[
            (daily_signals['date'] >= start_date) & 
            (daily_signals['date'] <= end_date)
        ]
        
        month_weekly_signals = weekly_signals[
            (weekly_signals['date'] >= start_date) & 
            (weekly_signals['date'] <= end_date)
        ]
        
        month_daily_trades = daily_trades[
            (daily_trades['entry_date'] >= start_date) & 
            (daily_trades['entry_date'] <= end_date)
        ]
        
        month_weekly_trades = weekly_trades[
            (weekly_trades['entry_date'] >= start_date) & 
            (weekly_trades['entry_date'] <= end_date)
        ]
        
        # 分析结果
        analysis = {
            "symbol": self.symbol,
            "period": f"{year}年{month}月",
            "date_range": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            
            "daily_strategy": {
                "signals_count": len(month_daily_signals),
                "buy_signals": len(month_daily_signals[month_daily_signals['action'] == 'BUY']),
                "sell_signals": len(month_daily_signals[month_daily_signals['action'] == 'SELL']),
                "trades_count": len(month_daily_trades),
                "profitable_trades": len(month_daily_trades[month_daily_trades['profit'] > 0]),
                "losing_trades": len(month_daily_trades[month_daily_trades['profit'] < 0]),
                "total_profit": month_daily_trades['profit'].sum() if len(month_daily_trades) > 0 else 0,
                "avg_profit": month_daily_trades['profit'].mean() if len(month_daily_trades) > 0 else 0,
                "max_profit": month_daily_trades['profit'].max() if len(month_daily_trades) > 0 else 0,
                "max_loss": month_daily_trades['profit'].min() if len(month_daily_trades) > 0 else 0,
                "win_rate": (len(month_daily_trades[month_daily_trades['profit'] > 0]) / len(month_daily_trades) * 100) 
                            if len(month_daily_trades) > 0 else 0
            },
            
            "weekly_strategy": {
                "signals_count": len(month_weekly_signals),
                "buy_signals": len(month_weekly_signals[month_weekly_signals['action'] == 'BUY']),
                "sell_signals": len(month_weekly_signals[month_weekly_signals['action'] == 'SELL']),
                "trades_count": len(month_weekly_trades),
                "profitable_trades": len(month_weekly_trades[month_weekly_trades['profit'] > 0]),
                "losing_trades": len(month_weekly_trades[month_weekly_trades['profit'] < 0]),
                "total_profit": month_weekly_trades['profit'].sum() if len(month_weekly_trades) > 0 else 0,
                "avg_profit": month_weekly_trades['profit'].mean() if len(month_weekly_trades) > 0 else 0,
                "max_profit": month_weekly_trades['profit'].max() if len(month_weekly_trades) > 0 else 0,
                "max_loss": month_weekly_trades['profit'].min() if len(month_weekly_trades) > 0 else 0,
                "win_rate": (len(month_weekly_trades[month_weekly_trades['profit'] > 0]) / len(month_weekly_trades) * 100) 
                            if len(month_weekly_trades) > 0 else 0
            }
        }
        
        return analysis
    
    def generate_weekly_report(self, start_date: str = None, save_to_file: bool = True) -> str:
        """
        生成周度报告
        
        Args:
            start_date: 周开始日期
            save_to_file: 是否保存到文件
        
        Returns:
            报告内容 (Markdown格式)
        """
        analysis = self.analyze_week(start_date)
        
        report = f"""# 📊 {analysis['symbol']} 策略周度分析报告

## 基本信息
- **分析周期**: {analysis['period']}
- **第{analysis['week_number']}周**
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 日度策略表现

### 信号统计
- 总信号数: {analysis['daily_strategy']['signals_count']}
  - BUY信号: {analysis['daily_strategy']['buy_signals']}
  - SELL信号: {analysis['daily_strategy']['sell_signals']}

### 交易统计
- 总交易次数: {analysis['daily_strategy']['trades_count']}
- 盈利交易: {analysis['daily_strategy']['profitable_trades']}
- 胜率: {analysis['daily_strategy']['win_rate']:.2f}%
- 总盈亏: ${analysis['daily_strategy']['total_profit']:.2f}

---

## 📊 周度策略表现

### 信号统计
- 总信号数: {analysis['weekly_strategy']['signals_count']}
  - BUY信号: {analysis['weekly_strategy']['buy_signals']}
  - SELL信号: {analysis['weekly_strategy']['sell_signals']}

### 交易统计
- 总交易次数: {analysis['weekly_strategy']['trades_count']}
- 盈利交易: {analysis['weekly_strategy']['profitable_trades']}
- 胜率: {analysis['weekly_strategy']['win_rate']:.2f}%
- 总盈亏: ${analysis['weekly_strategy']['total_profit']:.2f}

---

## 💡 策略评估

### 日度策略
"""
        
        # 日度策略评估
        if analysis['daily_strategy']['trades_count'] == 0:
            report += "- ⚠️ 本周无交易，策略未触发买卖信号\n"
        elif analysis['daily_strategy']['win_rate'] >= 60:
            report += f"- ✅ 表现优秀，胜率{analysis['daily_strategy']['win_rate']:.1f}%\n"
        elif analysis['daily_strategy']['win_rate'] >= 45:
            report += f"- ✅ 表现良好，胜率{analysis['daily_strategy']['win_rate']:.1f}%\n"
        else:
            report += f"- ⚠️ 表现欠佳，胜率{analysis['daily_strategy']['win_rate']:.1f}%，需要优化\n"
        
        if analysis['daily_strategy']['total_profit'] > 0:
            report += f"- ✅ 本周盈利 ${analysis['daily_strategy']['total_profit']:.2f}\n"
        elif analysis['daily_strategy']['total_profit'] < 0:
            report += f"- ⚠️ 本周亏损 ${abs(analysis['daily_strategy']['total_profit']):.2f}\n"
        
        report += "\n### 周度策略\n"
        
        # 周度策略评估
        if analysis['weekly_strategy']['trades_count'] == 0:
            report += "- ⚠️ 本周无交易，策略未触发买卖信号\n"
        elif analysis['weekly_strategy']['win_rate'] >= 60:
            report += f"- ✅ 表现优秀，胜率{analysis['weekly_strategy']['win_rate']:.1f}%\n"
        elif analysis['weekly_strategy']['win_rate'] >= 45:
            report += f"- ✅ 表现良好，胜率{analysis['weekly_strategy']['win_rate']:.1f}%\n"
        else:
            report += f"- ⚠️ 表现欠佳，胜率{analysis['weekly_strategy']['win_rate']:.1f}%，需要优化\n"
        
        if analysis['weekly_strategy']['total_profit'] > 0:
            report += f"- ✅ 本周盈利 ${analysis['weekly_strategy']['total_profit']:.2f}\n"
        elif analysis['weekly_strategy']['total_profit'] < 0:
            report += f"- ⚠️ 本周亏损 ${abs(analysis['weekly_strategy']['total_profit']):.2f}\n"
        
        report += "\n---\n\n"
        report += "**下一步行动**:\n"
        report += "- [ ] 回顾本周交易记录\n"
        report += "- [ ] 分析信号质量\n"
        report += "- [ ] 评估风险管理\n"
        report += "- [ ] 优化参数设置\n"
        
        # 保存到文件
        if save_to_file:
            report_file = self.data_dir / f"weekly_report_{analysis['period'].replace(' ', '_').replace('~', 'to')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 周度报告已保存: {report_file}")
        
        return report
    
    def generate_monthly_report(self, year: int = None, month: int = None, save_to_file: bool = True) -> str:
        """
        生成月度报告
        
        Args:
            year: 年份
            month: 月份
            save_to_file: 是否保存到文件
        
        Returns:
            报告内容 (Markdown格式)
        """
        analysis = self.analyze_month(year, month)
        
        report = f"""# 📊 {analysis['symbol']} 策略月度分析报告

## 基本信息
- **分析周期**: {analysis['period']}
- **日期范围**: {analysis['date_range']}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📈 日度策略月度表现

### 信号统计
- 总信号数: {analysis['daily_strategy']['signals_count']}
  - BUY信号: {analysis['daily_strategy']['buy_signals']}
  - SELL信号: {analysis['daily_strategy']['sell_signals']}

### 交易统计
- 总交易次数: {analysis['daily_strategy']['trades_count']}
- 盈利交易: {analysis['daily_strategy']['profitable_trades']}
- 亏损交易: {analysis['daily_strategy']['losing_trades']}
- 胜率: {analysis['daily_strategy']['win_rate']:.2f}%

### 盈亏统计
- 总盈亏: ${analysis['daily_strategy']['total_profit']:.2f}
- 平均盈亏: ${analysis['daily_strategy']['avg_profit']:.2f}
- 最大盈利: ${analysis['daily_strategy']['max_profit']:.2f}
- 最大亏损: ${analysis['daily_strategy']['max_loss']:.2f}

---

## 📊 周度策略月度表现

### 信号统计
- 总信号数: {analysis['weekly_strategy']['signals_count']}
  - BUY信号: {analysis['weekly_strategy']['buy_signals']}
  - SELL信号: {analysis['weekly_strategy']['sell_signals']}

### 交易统计
- 总交易次数: {analysis['weekly_strategy']['trades_count']}
- 盈利交易: {analysis['weekly_strategy']['profitable_trades']}
- 亏损交易: {analysis['weekly_strategy']['losing_trades']}
- 胜率: {analysis['weekly_strategy']['win_rate']:.2f}%

### 盈亏统计
- 总盈亏: ${analysis['weekly_strategy']['total_profit']:.2f}
- 平均盈亏: ${analysis['weekly_strategy']['avg_profit']:.2f}
- 最大盈利: ${analysis['weekly_strategy']['max_profit']:.2f}
- 最大亏损: ${analysis['weekly_strategy']['max_loss']:.2f}

---

## 💡 月度策略考核

### 日度策略考核

**交易频率**: """
        
        # 日度策略考核
        if analysis['daily_strategy']['trades_count'] == 0:
            report += "❌ 未达标 - 本月无交易\n"
        elif analysis['daily_strategy']['trades_count'] < 5:
            report += f"⚠️ 偏低 - 仅{analysis['daily_strategy']['trades_count']}笔交易\n"
        else:
            report += f"✅ 正常 - {analysis['daily_strategy']['trades_count']}笔交易\n"
        
        report += "\n**胜率**: "
        if analysis['daily_strategy']['trades_count'] == 0:
            report += "N/A\n"
        elif analysis['daily_strategy']['win_rate'] >= 60:
            report += f"✅ 优秀 - {analysis['daily_strategy']['win_rate']:.1f}%\n"
        elif analysis['daily_strategy']['win_rate'] >= 45:
            report += f"✅ 良好 - {analysis['daily_strategy']['win_rate']:.1f}%\n"
        else:
            report += f"❌ 需改进 - {analysis['daily_strategy']['win_rate']:.1f}%\n"
        
        report += "\n**盈亏表现**: "
        if analysis['daily_strategy']['total_profit'] > 0:
            report += f"✅ 盈利 ${analysis['daily_strategy']['total_profit']:.2f}\n"
        elif analysis['daily_strategy']['total_profit'] < 0:
            report += f"❌ 亏损 ${abs(analysis['daily_strategy']['total_profit']):.2f}\n"
        else:
            report += "⚠️ 持平\n"
        
        report += "\n### 周度策略考核\n\n"
        report += "**交易频率**: "
        
        # 周度策略考核
        if analysis['weekly_strategy']['trades_count'] == 0:
            report += "❌ 未达标 - 本月无交易\n"
        elif analysis['weekly_strategy']['trades_count'] < 2:
            report += f"⚠️ 偏低 - 仅{analysis['weekly_strategy']['trades_count']}笔交易\n"
        else:
            report += f"✅ 正常 - {analysis['weekly_strategy']['trades_count']}笔交易\n"
        
        report += "\n**胜率**: "
        if analysis['weekly_strategy']['trades_count'] == 0:
            report += "N/A\n"
        elif analysis['weekly_strategy']['win_rate'] >= 60:
            report += f"✅ 优秀 - {analysis['weekly_strategy']['win_rate']:.1f}%\n"
        elif analysis['weekly_strategy']['win_rate'] >= 45:
            report += f"✅ 良好 - {analysis['weekly_strategy']['win_rate']:.1f}%\n"
        else:
            report += f"❌ 需改进 - {analysis['weekly_strategy']['win_rate']:.1f}%\n"
        
        report += "\n**盈亏表现**: "
        if analysis['weekly_strategy']['total_profit'] > 0:
            report += f"✅ 盈利 ${analysis['weekly_strategy']['total_profit']:.2f}\n"
        elif analysis['weekly_strategy']['total_profit'] < 0:
            report += f"❌ 亏损 ${abs(analysis['weekly_strategy']['total_profit']):.2f}\n"
        else:
            report += "⚠️ 持平\n"
        
        report += "\n---\n\n"
        report += "## 📝 改进建议\n\n"
        report += "### 日度策略\n"
        
        # 日度策略建议
        if analysis['daily_strategy']['trades_count'] > 0:
            if analysis['daily_strategy']['win_rate'] < 45:
                report += "- ⚠️ 胜率偏低，建议:\n"
                report += "  - 调整动量窗口参数\n"
                report += "  - 优化成交量阈值\n"
                report += "  - 加强趋势过滤\n"
            if analysis['daily_strategy']['max_loss'] < -1000:
                report += "- ⚠️ 单笔亏损过大，建议:\n"
                report += "  - 降低止损线\n"
                report += "  - 减小仓位\n"
        else:
            report += "- ⚠️ 交易次数过少，建议:\n"
            report += "  - 适当放宽信号阈值\n"
            report += "  - 检查数据更新是否正常\n"
        
        report += "\n### 周度策略\n"
        
        # 周度策略建议
        if analysis['weekly_strategy']['trades_count'] > 0:
            if analysis['weekly_strategy']['win_rate'] < 45:
                report += "- ⚠️ 胜率偏低，建议:\n"
                report += "  - 调整周线趋势判断\n"
                report += "  - 优化入场时机\n"
            if analysis['weekly_strategy']['max_loss'] < -2000:
                report += "- ⚠️ 单笔亏损过大，建议:\n"
                report += "  - 调整止损策略\n"
                report += "  - 控制仓位规模\n"
        else:
            report += "- ⚠️ 交易次数过少，建议:\n"
            report += "  - 检查周度数据更新\n"
            report += "  - 评估信号触发条件\n"
        
        report += "\n---\n\n"
        report += "**下月计划**:\n"
        report += "- [ ] 根据本月表现调整参数\n"
        report += "- [ ] 优化风险管理策略\n"
        report += "- [ ] 改进信号过滤机制\n"
        report += "- [ ] 持续跟踪策略表现\n"
        
        # 保存到文件
        if save_to_file:
            report_file = self.data_dir / f"monthly_report_{analysis['period'].replace('年', '_').replace('月', '')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 月度报告已保存: {report_file}")
        
        return report


def generate_all_reports():
    """生成所有股票的周度和月度报告"""
    symbols = ["TSLA", "NVDA", "INTC"]
    
    print("=" * 80)
    print("📊 生成策略分析报告")
    print("=" * 80)
    print()
    
    # 生成周度报告
    print("📈 生成周度报告...")
    print("-" * 80)
    for symbol in symbols:
        print(f"\n{symbol}:")
        analyzer = StrategyAnalyzer(symbol)
        analyzer.generate_weekly_report()
    
    print()
    print("=" * 80)
    
    # 生成月度报告
    print("📊 生成月度报告...")
    print("-" * 80)
    for symbol in symbols:
        print(f"\n{symbol}:")
        analyzer = StrategyAnalyzer(symbol)
        analyzer.generate_monthly_report()
    
    print()
    print("=" * 80)
    print("✅ 所有报告生成完成!")
    print("=" * 80)


if __name__ == "__main__":
    generate_all_reports()
