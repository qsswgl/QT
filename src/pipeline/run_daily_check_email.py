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
from src.utils.real_portfolio import RealPortfolioManager
from src.utils.fundamentals_manager import FundamentalsManager
from src.utils.news_manager import NewsManager
from src.utils.market_environment_manager import MarketEnvironmentManager
from src.utils.realtime_quotes_manager import RealtimeQuotesManager


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


def get_real_position(symbol: str, current_price: float = None) -> dict:
    """
    获取真实Firstrade账户持仓信息
    
    Args:
        symbol: 股票代码
        current_price: 当前价格
        
    Returns:
        dict: 持仓信息
    """
    try:
        manager = RealPortfolioManager()
        return manager.get_position(symbol, current_price)
    except Exception as e:
        print(f"⚠️  无法读取真实持仓: {e}")
        print(f"   返回空仓位信息")
        return {
            'symbol': symbol,
            'quantity': 0,
            'avg_price': 0,
            'current_price': current_price or 0,
            'market_value': 0,
            'profit_loss': 0,
            'profit_loss_pct': 0
        }


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
    fundamentals_mgr = None
    health = None
    news_mgr = None
    news_summary = None
    market_env = None
    realtime_quote = None
    
    try:
        # 先获取盘中实时价格
        print("[步骤 -1/6] 💹 获取盘中实时报价...")
        try:
            quotes_mgr = RealtimeQuotesManager()
            realtime_quote = quotes_mgr.get_realtime_quote('TSLA')
            
            if realtime_quote['success']:
                print(f"✓ 实时价格: ${realtime_quote['current_price']:.2f}")
                print(f"  涨跌: {realtime_quote['change']:+.2f} ({realtime_quote['change_pct']:+.2f}%)")
                print(f"  时间: {realtime_quote['time_beijing']} (盘中实时)")
            else:
                print(f"⚠️  实时报价获取失败: {realtime_quote['error']}")
                realtime_quote = None
        except Exception as e:
            print(f"⚠️  实时报价获取失败: {e}")
            realtime_quote = None
        print()
        
        print("[步骤 0/6] 🌍 市场环境综合分析...")
        try:
            env_mgr = MarketEnvironmentManager()
            market_env = env_mgr.get_comprehensive_analysis('TSLA')
            # 显示简要信息
            print(f"✓ 宏观环境: {market_env['macro']['environment']} ({market_env['macro']['risk_level']} risk)")
            print(f"✓ 市场情绪: {market_env['sentiment']['overall_sentiment']} ({market_env['sentiment']['overall_score']}/100)")
            print(f"✓ 综合风险: {market_env['overall_risk'].upper()}")
            print(f"✓ 建议仓位: {market_env['position_adjustment']:.0%}")
        except Exception as e:
            print(f"⚠️  市场环境分析失败: {e}")
            market_env = None
        print()
        
        print("[步骤 1/6] 📊 获取基本面数据...")
        try:
            fundamentals_mgr = FundamentalsManager()
            health = fundamentals_mgr.calculate_financial_health('TSLA')
            print(f"✓ 财务健康评分: {health['score']}/100 (等级: {health['grade']})")
            if health['details'].get('pe') != 'N/A':
                print(f"  PE比率: {health['details']['pe']:.2f}")
            if health['details'].get('roe') != 'N/A':
                print(f"  ROE: {health['details']['roe']*100:.2f}%")
        except Exception as e:
            print(f"⚠️  基本面数据获取失败: {e}")
            print("   将仅使用技术面策略")
            health = {'score': 0, 'grade': 'N/A', 'details': {}, 'checks': {}}
        print()
        
        print("[步骤 2/6] 📰 获取新闻情绪数据...")
        try:
            news_mgr = NewsManager()
            news_summary = news_mgr.get_news_summary('TSLA', days=7)
            sentiment = news_summary['sentiment']
            print(f"✓ 新闻情绪评分: {sentiment['score']}/100 ({sentiment['sentiment']})")
            print(f"  正面新闻: {sentiment['positive']} | 负面: {sentiment['negative']} | 中性: {sentiment['neutral']}")
            print(f"  风险调整: {news_summary['risk_adjustment']}x")
            print(f"  建议: {news_summary['recommendation']}")
        except Exception as e:
            print(f"⚠️  新闻数据获取失败: {e}")
            print("   将不使用新闻情绪")
            news_summary = None
        print()
        
        print("[步骤 3/6] 📂 加载历史数据...")
        data_path = project_root / "data" / "sample_tsla.csv"
        
        if not data_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {data_path}")
        
        loader = CSVPriceLoader(data_path)
        bars = list(loader.load())
        print(f"✓ 已加载 {len(bars)} 条历史数据")
        print(f"  日期范围: {bars[0].date} 至 {bars[-1].date}")
        print()
        
        print("[步骤 4/6] 🚀 运行日度策略...")
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
        
        print("[步骤 5/6] 🔍 检查新交易信号 (最近1天)...")
        signal_info = check_for_new_signals()
        
        # 获取真实持仓信息(优先使用实时价格)
        if realtime_quote and realtime_quote['success']:
            current_price = realtime_quote['current_price']
        else:
            current_price = bars[-1].close if bars else 0
        
        position_info = get_real_position('TSLA', current_price)
        print(f"📊 真实持仓: {position_info['quantity']} 股 @ ${position_info['avg_price']:.2f}")
        if position_info['quantity'] > 0:
            pnl_symbol = '+' if position_info['profit_loss'] >= 0 else ''
            print(f"   当前市值: ${position_info['market_value']:,.2f}")
            print(f"   浮动盈亏: {pnl_symbol}${position_info['profit_loss']:,.2f} ({pnl_symbol}{position_info['profit_loss_pct']:.2f}%)")
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
            
            # 添加基本面判断
            if fundamentals_mgr and health:
                print("  � 基本面检查:")
                decision = fundamentals_mgr.should_allow_buy('TSLA', min_score=50)
                if latest['action'] == 'BUY':
                    if decision['allow']:
                        print(f"     ✅ {decision['reason']}")
                    else:
                        print(f"     ⚠️  {decision['reason']}")
            print()
            
            print("[步骤 6/6] 📧 发送邮件提醒...")
            
            current_price = bars[-1].close
            
            action_str = str(latest['action']).upper()
            if 'BUY' in action_str:
                action = 'BUY'
            elif 'SELL' in action_str:
                action = 'SELL'
            else:
                action = action_str
            
            # 在原因中添加基本面信息和新闻情绪
            enhanced_reason = latest['reason']
            if health and health['score'] > 0:
                enhanced_reason += f"\n📊 基本面: 评分{health['score']}/100(等级{health['grade']})"
                if health['details'].get('pe') != 'N/A':
                    enhanced_reason += f", PE={health['details']['pe']:.1f}"
                if health['details'].get('roe') != 'N/A':
                    enhanced_reason += f", ROE={health['details']['roe']*100:.1f}%"
            
            if news_summary:
                sentiment = news_summary['sentiment']
                enhanced_reason += f"\n📰 新闻情绪: {sentiment['score']}/100({sentiment['sentiment']})"
                enhanced_reason += f", 风险调整{news_summary['risk_adjustment']}x"
                enhanced_reason += f"\n   {news_summary['recommendation']}"
            
            email_service.send_signal_alert(
                symbol="TSLA",
                action=action,
                quantity=latest['quantity'],
                price=current_price,
                reason=enhanced_reason,
                signal_date=latest['date'],
                strategy_name="TSLA日度策略 (技术面+基本面+新闻情绪)"
            )
        else:
            print("✓ 暂无新交易信号")
            print()
            
            # 显示当前基本面状况
            if health and health['score'] > 0:
                print("  📊 当前基本面状况:")
                print(f"     评分: {health['score']}/100 (等级: {health['grade']})")
                if health['details'].get('pe') != 'N/A':
                    print(f"     PE: {health['details']['pe']:.2f}")
                if health['details'].get('roe') != 'N/A':
                    print(f"     ROE: {health['details']['roe']*100:.2f}%")
                print()
            
            # 显示新闻情绪状况
            if news_summary:
                print("  📰 当前新闻情绪:")
                sentiment = news_summary['sentiment']
                print(f"     情绪评分: {sentiment['score']}/100 ({sentiment['sentiment']})")
                print(f"     正面/负面/中性: {sentiment['positive']}/{sentiment['negative']}/{sentiment['neutral']}")
                print(f"     风险调整: {news_summary['risk_adjustment']}x")
                print()
            
            print("[步骤 6/6] 📧 发送每日总结...")
            
            # 准备附加信息 - 先添加实时价格
            additional_info = None
            
            # 首先添加盘中实时价格
            if realtime_quote and realtime_quote['success']:
                additional_info = f"💹 盘中实时报价 (数据时间: {realtime_quote['time_beijing']}):\n"
                additional_info += f"当前价格: ${realtime_quote['current_price']:.2f}\n"
                additional_info += f"涨跌: {realtime_quote['change']:+.2f} ({realtime_quote['change_pct']:+.2f}%)\n"
                additional_info += f"开/高/低: ${realtime_quote['open']:.2f} / ${realtime_quote['high']:.2f} / ${realtime_quote['low']:.2f}\n"
                additional_info += f"昨收: ${realtime_quote['prev_close']:.2f}"
            
            if health and health['score'] > 0:
                if additional_info is None:
                    additional_info = "📊 基本面数据:\n"
                else:
                    additional_info += "\n\n📊 基本面数据:\n"
                additional_info += f"财务健康评分: {health['score']}/100 (等级: {health['grade']})\n"
                if health['details'].get('pe') != 'N/A':
                    additional_info += f"市盈率PE: {health['details']['pe']:.2f}\n"
                if health['details'].get('roe') != 'N/A':
                    additional_info += f"ROE: {health['details']['roe']*100:.2f}%\n"
                if health['details'].get('current_ratio') != 'N/A':
                    additional_info += f"流动比率: {health['details']['current_ratio']:.2f}"
            
            if news_summary:
                if additional_info is None:
                    additional_info = ""
                else:
                    additional_info += "\n\n"
                sentiment = news_summary['sentiment']
                additional_info += f"📰 新闻情绪数据:\n"
                additional_info += f"情绪评分: {sentiment['score']}/100 ({sentiment['sentiment']})\n"
                additional_info += f"新闻分布: 正面{sentiment['positive']} | 负面{sentiment['negative']} | 中性{sentiment['neutral']}\n"
                additional_info += f"风险调整: {news_summary['risk_adjustment']}x\n"
                additional_info += f"建议: {news_summary['recommendation']}"
            
            if market_env:
                if additional_info is None:
                    additional_info = ""
                else:
                    additional_info += "\n\n"
                additional_info += f"🌍 市场环境数据:\n"
                additional_info += f"宏观环境: {market_env['macro']['environment']} (风险: {market_env['macro']['risk_level']})\n"
                additional_info += f"市场情绪: {market_env['sentiment']['overall_sentiment']} ({market_env['sentiment']['overall_score']}/100)\n"
                
                # 添加关键市场指标
                indicators = market_env['sentiment'].get('market_indicators', {})
                if indicators:
                    vix = indicators.get('vix')
                    if vix:
                        additional_info += f"VIX恐慌指数: {vix['price']} ({vix['status']})\n"
                    
                    gold = indicators.get('gold')
                    if gold:
                        additional_info += f"黄金: ${gold['price']} ({gold['change_pct']:+.2f}%)\n"
                        
                    oil = indicators.get('oil')
                    if oil:
                        additional_info += f"原油: ${oil['price']} ({oil['change_pct']:+.2f}%)\n"
                
                additional_info += f"综合风险: {market_env['overall_risk'].upper()}\n"
                additional_info += f"建议仓位: {market_env['position_adjustment']:.0%}\n"
                additional_info += f"综合建议: {market_env['recommendation']}"
            
            # 发送每日总结邮件
            email_service.send_daily_summary(
                has_signal=False,
                signal_count=0,
                latest_signal=None,
                error_message=None,
                additional_info=additional_info,
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
