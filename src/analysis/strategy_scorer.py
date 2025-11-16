"""
策略对比和评分系统

功能:
1. 对比三个股票的策略表现
2. 为每个策略打分
3. 生成策略排名
4. 提供优化建议
"""
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analysis.strategy_analyzer import StrategyAnalyzer


class StrategyScorer:
    """策略评分器"""
    
    # 评分权重
    WEIGHTS = {
        "win_rate": 0.30,        # 胜率权重 30%
        "profit": 0.25,          # 盈利权重 25%
        "consistency": 0.20,     # 稳定性权重 20%
        "frequency": 0.15,       # 交易频率权重 15%
        "risk_reward": 0.10      # 风险收益比权重 10%
    }
    
    def __init__(self):
        self.symbols = ["TSLA", "NVDA", "INTC"]
        self.analyzers = {
            symbol: StrategyAnalyzer(symbol) for symbol in self.symbols
        }
    
    def score_strategy(
        self, 
        symbol: str, 
        strategy_type: str = "daily",
        period: str = "month"
    ) -> Dict:
        """
        为单个策略打分
        
        Args:
            symbol: 股票代码
            strategy_type: 策略类型 (daily/weekly)
            period: 评估周期 (week/month)
        
        Returns:
            评分结果字典
        """
        analyzer = self.analyzers[symbol]
        
        # 获取分析数据
        if period == "week":
            analysis = analyzer.analyze_week()
        else:
            analysis = analyzer.analyze_month()
        
        strategy_data = analysis[f"{strategy_type}_strategy"]
        
        # 计算各项得分 (0-100分)
        scores = {}
        
        # 1. 胜率得分 (0-100)
        win_rate = strategy_data['win_rate']
        if win_rate >= 70:
            scores['win_rate'] = 100
        elif win_rate >= 60:
            scores['win_rate'] = 90
        elif win_rate >= 50:
            scores['win_rate'] = 75
        elif win_rate >= 40:
            scores['win_rate'] = 50
        else:
            scores['win_rate'] = max(0, win_rate)
        
        # 2. 盈利得分 (0-100)
        total_profit = strategy_data['total_profit']
        if total_profit >= 5000:
            scores['profit'] = 100
        elif total_profit >= 3000:
            scores['profit'] = 80
        elif total_profit >= 1000:
            scores['profit'] = 60
        elif total_profit >= 0:
            scores['profit'] = 40
        else:
            # 亏损情况
            if total_profit >= -500:
                scores['profit'] = 30
            elif total_profit >= -1000:
                scores['profit'] = 20
            else:
                scores['profit'] = 0
        
        # 3. 稳定性得分 (基于盈利交易占比)
        if strategy_data['trades_count'] > 0:
            consistency = (strategy_data['profitable_trades'] / strategy_data['trades_count']) * 100
            scores['consistency'] = consistency
        else:
            scores['consistency'] = 0
        
        # 4. 交易频率得分
        trades_count = strategy_data['trades_count']
        if period == "week":
            # 周度评估
            if strategy_type == "daily":
                # 日度策略，一周期望3-5笔交易
                if 3 <= trades_count <= 5:
                    scores['frequency'] = 100
                elif 2 <= trades_count < 3 or 5 < trades_count <= 7:
                    scores['frequency'] = 75
                elif trades_count == 1 or 7 < trades_count <= 10:
                    scores['frequency'] = 50
                else:
                    scores['frequency'] = 25
            else:
                # 周度策略，一周期望1-2笔交易
                if 1 <= trades_count <= 2:
                    scores['frequency'] = 100
                elif trades_count == 3:
                    scores['frequency'] = 75
                else:
                    scores['frequency'] = 50
        else:
            # 月度评估
            if strategy_type == "daily":
                # 日度策略，一月期望10-20笔交易
                if 10 <= trades_count <= 20:
                    scores['frequency'] = 100
                elif 5 <= trades_count < 10 or 20 < trades_count <= 30:
                    scores['frequency'] = 75
                elif 3 <= trades_count < 5 or 30 < trades_count <= 40:
                    scores['frequency'] = 50
                else:
                    scores['frequency'] = 25
            else:
                # 周度策略，一月期望4-8笔交易
                if 4 <= trades_count <= 8:
                    scores['frequency'] = 100
                elif 2 <= trades_count < 4 or 8 < trades_count <= 12:
                    scores['frequency'] = 75
                else:
                    scores['frequency'] = 50
        
        # 5. 风险收益比得分
        if strategy_data['trades_count'] > 0:
            avg_profit = strategy_data.get('avg_profit', 0)
            if avg_profit > 0:
                # 盈利情况
                if avg_profit >= 200:
                    scores['risk_reward'] = 100
                elif avg_profit >= 100:
                    scores['risk_reward'] = 80
                elif avg_profit >= 50:
                    scores['risk_reward'] = 60
                else:
                    scores['risk_reward'] = 40
            else:
                scores['risk_reward'] = 20
        else:
            scores['risk_reward'] = 0
        
        # 计算总分
        total_score = sum(
            scores[key] * self.WEIGHTS[key] 
            for key in scores.keys()
        )
        
        return {
            "symbol": symbol,
            "strategy_type": strategy_type,
            "period": period,
            "scores": scores,
            "total_score": round(total_score, 2),
            "grade": self._get_grade(total_score),
            "trades_count": strategy_data['trades_count'],
            "win_rate": strategy_data['win_rate'],
            "total_profit": strategy_data['total_profit']
        }
    
    def _get_grade(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "A+ 优秀"
        elif score >= 80:
            return "A 良好"
        elif score >= 70:
            return "B+ 中上"
        elif score >= 60:
            return "B 中等"
        elif score >= 50:
            return "C 及格"
        else:
            return "D 不及格"
    
    def compare_all_strategies(self, period: str = "month") -> pd.DataFrame:
        """
        对比所有策略
        
        Args:
            period: 评估周期 (week/month)
        
        Returns:
            对比结果DataFrame
        """
        results = []
        
        for symbol in self.symbols:
            for strategy_type in ["daily", "weekly"]:
                score_result = self.score_strategy(symbol, strategy_type, period)
                results.append({
                    "股票": symbol,
                    "策略": strategy_type,
                    "总分": score_result['total_score'],
                    "等级": score_result['grade'],
                    "胜率": f"{score_result['win_rate']:.1f}%",
                    "盈亏": f"${score_result['total_profit']:.2f}",
                    "交易次数": score_result['trades_count'],
                    "胜率分": score_result['scores']['win_rate'],
                    "盈利分": score_result['scores']['profit'],
                    "稳定分": score_result['scores']['consistency'],
                    "频率分": score_result['scores']['frequency'],
                    "风险收益分": score_result['scores']['risk_reward']
                })
        
        df = pd.DataFrame(results)
        df = df.sort_values('总分', ascending=False)
        return df
    
    def generate_comparison_report(self, period: str = "month", save_to_file: bool = True) -> str:
        """
        生成策略对比报告
        
        Args:
            period: 评估周期
            save_to_file: 是否保存到文件
        
        Returns:
            报告内容 (Markdown格式)
        """
        df = self.compare_all_strategies(period)
        
        period_name = "周度" if period == "week" else "月度"
        
        report = f"""# 📊 策略对比和评分报告 ({period_name})

## 基本信息
- **评估周期**: {period_name}
- **评估股票**: {', '.join(self.symbols)}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🏆 策略排名

"""
        
        # 添加排名表格
        report += "| 排名 | 股票 | 策略 | 总分 | 等级 | 胜率 | 盈亏 | 交易次数 |\n"
        report += "|------|------|------|------|------|------|------|----------|\n"
        
        for idx, row in df.iterrows():
            rank = df.index.get_loc(idx) + 1
            report += f"| {rank} | {row['股票']} | {row['策略']} | {row['总分']:.1f} | {row['等级']} | {row['胜率']} | {row['盈亏']} | {row['交易次数']} |\n"
        
        report += "\n---\n\n## 📈 详细评分\n\n"
        
        # 添加详细评分表格
        report += "| 股票 | 策略 | 胜率分 | 盈利分 | 稳定分 | 频率分 | 风险收益分 |\n"
        report += "|------|------|--------|--------|--------|--------|------------|\n"
        
        for idx, row in df.iterrows():
            report += f"| {row['股票']} | {row['策略']} | {row['胜率分']:.1f} | {row['盈利分']:.1f} | {row['稳定分']:.1f} | {row['频率分']:.1f} | {row['风险收益分']:.1f} |\n"
        
        report += "\n---\n\n## 💡 策略分析\n\n"
        
        # 找出最佳和最差策略
        best = df.iloc[0]
        worst = df.iloc[-1]
        
        report += f"### ✅ 最佳策略\n\n"
        report += f"**{best['股票']} - {best['策略']}策略**\n"
        report += f"- 总分: {best['总分']:.1f} ({best['等级']})\n"
        report += f"- 胜率: {best['胜率']}\n"
        report += f"- 盈亏: {best['盈亏']}\n"
        report += f"- 交易次数: {best['交易次数']}\n\n"
        report += "**优势**:\n"
        
        # 分析优势
        if best['胜率分'] >= 80:
            report += f"- ✅ 胜率表现优秀 (得分: {best['胜率分']:.1f})\n"
        if best['盈利分'] >= 80:
            report += f"- ✅ 盈利能力强 (得分: {best['盈利分']:.1f})\n"
        if best['稳定分'] >= 80:
            report += f"- ✅ 稳定性高 (得分: {best['稳定分']:.1f})\n"
        
        report += f"\n### ⚠️ 需改进策略\n\n"
        report += f"**{worst['股票']} - {worst['策略']}策略**\n"
        report += f"- 总分: {worst['总分']:.1f} ({worst['等级']})\n"
        report += f"- 胜率: {worst['胜率']}\n"
        report += f"- 盈亏: {worst['盈亏']}\n"
        report += f"- 交易次数: {worst['交易次数']}\n\n"
        report += "**需改进**:\n"
        
        # 分析弱点
        if worst['胜率分'] < 60:
            report += f"- ⚠️ 胜率偏低 (得分: {worst['胜率分']:.1f}) - 需优化信号质量\n"
        if worst['盈利分'] < 60:
            report += f"- ⚠️ 盈利能力不足 (得分: {worst['盈利分']:.1f}) - 需改进风险管理\n"
        if worst['稳定分'] < 60:
            report += f"- ⚠️ 稳定性差 (得分: {worst['稳定分']:.1f}) - 需加强信号过滤\n"
        if worst['频率分'] < 60:
            report += f"- ⚠️ 交易频率不佳 (得分: {worst['频率分']:.1f}) - 需调整参数阈值\n"
        
        report += "\n---\n\n## 📋 优化建议\n\n"
        
        # 按股票分组提供建议
        for symbol in self.symbols:
            symbol_df = df[df['股票'] == symbol]
            daily_score = symbol_df[symbol_df['策略'] == 'daily']['总分'].values[0]
            weekly_score = symbol_df[symbol_df['策略'] == 'weekly']['总分'].values[0]
            
            report += f"### {symbol}\n\n"
            
            if daily_score >= 70 and weekly_score >= 70:
                report += "- ✅ 整体表现良好，保持当前策略\n"
            elif daily_score < 60 or weekly_score < 60:
                report += "- ⚠️ 需要重点优化:\n"
                if daily_score < 60:
                    report += "  - 日度策略需调整参数\n"
                if weekly_score < 60:
                    report += "  - 周度策略需优化信号\n"
            
            # 对比日度和周度
            if daily_score > weekly_score + 10:
                report += f"- 💡 日度策略表现明显优于周度策略，建议加大日度策略权重\n"
            elif weekly_score > daily_score + 10:
                report += f"- 💡 周度策略表现明显优于日度策略，建议加大周度策略权重\n"
            
            report += "\n"
        
        report += "---\n\n"
        report += "## 🎯 行动计划\n\n"
        report += "- [ ] 对最佳策略进行案例研究，总结成功经验\n"
        report += "- [ ] 对低分策略进行参数调优\n"
        report += "- [ ] 加强风险管理，控制最大回撤\n"
        report += "- [ ] 定期回顾和更新策略评分\n"
        report += "- [ ] 考虑组合策略，分散风险\n"
        
        # 保存到文件
        if save_to_file:
            report_file = project_root / f"strategy_comparison_{period}_{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 策略对比报告已保存: {report_file}")
            
            # 也保存CSV
            csv_file = project_root / f"strategy_scores_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"✅ 评分数据已保存: {csv_file}")
        
        return report


def main():
    """主函数"""
    print("=" * 80)
    print("📊 策略对比和评分系统")
    print("=" * 80)
    print()
    
    scorer = StrategyScorer()
    
    # 生成月度对比报告
    print("📈 生成月度策略对比报告...")
    print("-" * 80)
    scorer.generate_comparison_report(period="month")
    
    print()
    print("=" * 80)
    print("✅ 对比报告生成完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
