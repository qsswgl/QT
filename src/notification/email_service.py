"""
邮件发送服务
"""
import smtplib
import socket
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.notification.email_config import email_config


class EmailService:
    """邮件发送服务"""
    
    def __init__(self, config=None):
        self.config = config or email_config
    
    def send_signal_alert(
        self, 
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        reason: str,
        signal_date: str,
        strategy_name: str = "TSLA策略"
    ) -> bool:
        """
        发送交易信号提醒邮件
        
        Args:
            symbol: 股票代码
            action: 动作 (BUY/SELL)
            quantity: 数量
            price: 价格
            reason: 信号原因
            signal_date: 信号日期
            strategy_name: 策略名称
        
        Returns:
            bool: 是否发送成功
        """
        if not self.config.enabled:
            print("📧 邮件推送未启用")
            return False
        
        # 构建动态主题前缀
        subject_prefix = f"[{symbol}策略]"
        
        # 构建邮件主题
        action_cn = "买入" if action == "BUY" else "卖出"
        subject = f"{subject_prefix} 🚨 {strategy_name} - {symbol} {action_cn}信号!"
        
        # 构建邮件正文
        body = self._build_signal_email_body(
            symbol, action, quantity, price, reason, signal_date, strategy_name
        )
        
        # 发送邮件
        return self._send_email(subject, body)
    
    def send_weekly_summary(
        self,
        has_signal: bool,
        signal_count: int = 0,
        latest_signal: Optional[dict] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        发送每周检查总结邮件
        
        Args:
            has_signal: 是否有新信号
            signal_count: 信号数量
            latest_signal: 最新信号详情
            error_message: 错误信息(如果有)
        
        Returns:
            bool: 是否发送成功
        """
        if not self.config.enabled:
            print("📧 邮件推送未启用")
            return False
        
        # 构建邮件主题
        if error_message:
            subject = f"{self.config.subject_prefix} ⚠️ 每周检查失败"
        elif has_signal:
            subject = f"{self.config.subject_prefix} 🚨 发现新信号!"
        else:
            subject = f"{self.config.subject_prefix} ✅ 每周检查完成 - 无新信号"
        
        # 构建邮件正文
        body = self._build_summary_email_body(
            has_signal, signal_count, latest_signal, error_message, strategy_type="周度策略"
        )
        
        # 发送邮件
        return self._send_email(subject, body)
    
    def send_daily_summary(
        self,
        has_signal: bool,
        signal_count: int = 0,
        latest_signal: Optional[dict] = None,
        error_message: Optional[str] = None,
        position_info: Optional[dict] = None,
        symbol: str = "TSLA",
        additional_info: Optional[str] = None
    ) -> bool:
        """
        发送每日检查总结邮件
        
        Args:
            has_signal: 是否有新信号
            signal_count: 信号数量
            latest_signal: 最新信号详情
            error_message: 错误信息(如果有)
            position_info: 当前持仓信息 {symbol, quantity, avg_price, current_price, market_value, profit_loss, profit_loss_pct}
            symbol: 股票代码
            additional_info: 附加信息(如基本面快照)
        
        Returns:
            bool: 是否发送成功
        """
        if not self.config.enabled:
            print("📧 邮件推送未启用")
            return False
        
        # 构建动态主题前缀
        subject_prefix = f"[{symbol}策略]"
        
        # 构建邮件主题 - 只有真正的错误才显示"失败"
        if error_message and not additional_info:  # 真正的错误
            subject = f"{subject_prefix} ⚠️ {symbol} 每日检查失败"
        elif has_signal:
            subject = f"{subject_prefix} 🚨 {symbol} 发现新信号!"
        else:
            subject = f"{subject_prefix} ✅ {symbol} 每日检查完成 - 无新信号"
        
        # 合并附加信息到error_message用于邮件正文显示
        display_message = error_message
        if additional_info and not error_message:
            display_message = additional_info
        elif additional_info and error_message:
            display_message = f"{error_message}\n\n{additional_info}"
        
        # 构建邮件正文
        body = self._build_summary_email_body(
            has_signal, signal_count, latest_signal, display_message, 
            strategy_type="日度策略", position_info=position_info, symbol=symbol
        )
        
        # 发送邮件
        return self._send_email(subject, body)
    
    def _build_signal_email_body(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        reason: str,
        signal_date: str,
        strategy_name: str = "TSLA策略"
    ) -> str:
        """构建交易信号邮件正文"""
        action_cn = "买入" if action == "BUY" else "卖出"
        action_color = "#00AA00" if action == "BUY" else "#FF0000"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .strategy-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-size: 14px;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 10px 10px;
        }}
        .signal-box {{
            background: white;
            padding: 20px;
            border-left: 4px solid {action_color};
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .signal-item {{
            margin: 10px 0;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        .label {{
            font-weight: bold;
            color: #555;
            display: inline-block;
            width: 120px;
        }}
        .value {{
            color: #333;
        }}
        .action-value {{
            color: {action_color};
            font-size: 24px;
            font-weight: bold;
        }}
        .button {{
            display: inline-block;
            padding: 15px 30px;
            background: {action_color};
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
            text-align: center;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 交易信号提醒</h1>
        <p>TSLA 策略检测到新信号</p>
        <div class="strategy-badge">{strategy_name}</div>
    </div>
    
    <div class="content">
        <div class="signal-box">
            <h2 style="margin-top: 0; color: {action_color};">📊 信号详情</h2>
            
            <div class="signal-item">
                <span class="label">📅 信号日期:</span>
                <span class="value">{signal_date}</span>
            </div>
            
            <div class="signal-item">
                <span class="label">📈 股票代码:</span>
                <span class="value">{symbol}</span>
            </div>
            
            <div class="signal-item">
                <span class="label">⚡ 交易动作:</span>
                <span class="action-value">{action_cn} ({action})</span>
            </div>
            
            <div class="signal-item">
                <span class="label">📦 建议数量:</span>
                <span class="value" style="font-size: 18px; font-weight: bold;">{quantity:,} 股</span>
            </div>
            
            <div class="signal-item">
                <span class="label">💰 参考价格:</span>
                <span class="value" style="font-size: 18px; font-weight: bold;">${price:,.2f}</span>
            </div>
            
            <div class="signal-item">
                <span class="label">💡 信号原因:</span>
                <span class="value">{reason}</span>
            </div>
            
            <div class="signal-item">
                <span class="label">💵 预估总额:</span>
                <span class="value" style="font-size: 18px; font-weight: bold; color: #FF6600;">
                    ${quantity * price:,.2f}
                </span>
            </div>
        </div>
        
        <div class="warning">
            <strong>⚠️ 重要提示:</strong>
            <ul style="margin: 10px 0;">
                <li>请在美股交易时间内执行 (EST 9:30 AM - 4:00 PM)</li>
                <li>确认账户有足够资金 (建议准备 +5% 缓冲)</li>
                <li>建议使用市价单 (Market Order) 快速成交</li>
                <li>执行后请记录订单号和实际成交价格</li>
            </ul>
        </div>
        
        <center>
            <a href="https://www.firstrade.com" class="button">
                🔗 登录 Firstrade 执行交易
            </a>
        </center>
        
        <div style="margin-top: 30px; padding: 15px; background: #e8f4f8; border-radius: 5px;">
            <h3 style="margin-top: 0;">📋 执行步骤</h3>
            <ol>
                <li>登录 Firstrade 账户</li>
                <li>进入 Trade → Stocks & Options</li>
                <li>填写订单信息:
                    <ul>
                        <li>Symbol: {symbol}</li>
                        <li>Action: {action_cn}</li>
                        <li>Quantity: {quantity:,}</li>
                        <li>Order Type: Market</li>
                    </ul>
                </li>
                <li>确认并提交订单</li>
                <li>记录订单号和成交价格</li>
                <li>在 TRADE_EXECUTION_LOG.md 中记录</li>
            </ol>
        </div>
    </div>
    
    <div class="footer">
        <p>📅 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🤖 {strategy_name} 自动提醒系统</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _build_summary_email_body(
        self,
        has_signal: bool,
        signal_count: int,
        latest_signal: Optional[dict],
        error_message: Optional[str],
        strategy_type: str = "周度策略",
        position_info: Optional[dict] = None,
        symbol: str = "TSLA",
        is_error: bool = None
    ) -> str:
        """构建总结邮件正文
        
        Args:
            has_signal: 是否有信号
            signal_count: 信号数量
            latest_signal: 最新信号详情
            error_message: 错误信息或附加信息
            strategy_type: 策略类型（"日度策略" 或 "周度策略"）
            position_info: 当前持仓信息
            symbol: 股票代码
            is_error: 是否为真正的错误(None时自动判断:有error_message且无has_signal)
        """
        
        # 自动判断是否为错误:有error_message但没有信号,且不是正常检查完成
        if is_error is None:
            is_error = error_message is not None and not has_signal and position_info is None
        
        if error_message and is_error:
            # 错误通知
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #dc3545;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 10px 10px;
        }}
        .error-box {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ {strategy_type}检查失败</h1>
    </div>
    <div class="content">
        <div class="error-box">
            <h3>错误信息:</h3>
            <p>{error_message}</p>
        </div>
        <p>建议: 手动检查日志获取详细错误信息</p>
    </div>
</body>
</html>
            """
            return html
        
        elif has_signal and latest_signal:
            # 有信号通知
            action = latest_signal.get('action', 'UNKNOWN')
            action_cn = "买入" if action == "BUY" else "卖出"
            action_color = "#00AA00" if action == "BUY" else "#FF0000"
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 10px 10px;
        }}
        .highlight {{
            background: white;
            padding: 20px;
            border-left: 4px solid {action_color};
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .button {{
            display: inline-block;
            padding: 15px 30px;
            background: {action_color};
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .strategy-box {{
            background: #fff8e1;
            border: 2px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        .strategy-box h3 {{
            color: #ff6f00;
            margin-top: 0;
        }}
        .strategy-box ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .strategy-box li {{
            margin: 8px 0;
        }}
        .rule-item {{
            background: white;
            padding: 10px;
            margin: 8px 0;
            border-left: 3px solid #ffc107;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 发现新信号!</h1>
        <p>{symbol} {strategy_type}检查</p>
    </div>
    <div class="content">
        <div class="highlight">
            <h2 style="color: {action_color}; margin-top: 0;">检测到 {signal_count} 个新信号</h2>
            <p><strong>最新信号:</strong></p>
            <ul>
                <li>动作: <strong style="color: {action_color};">{action_cn}</strong></li>
                <li>数量: <strong>{latest_signal.get('quantity', 0):,} 股</strong></li>
                <li>日期: {latest_signal.get('date', 'N/A')}</li>
            </ul>
        </div>
        <center>
            <a href="https://www.firstrade.com" class="button">
                🔗 立即登录 Firstrade
            </a>
        </center>
        
        <div class="strategy-box">
            <h3>📊 策略算法与规则说明</h3>
            
            <div class="rule-item">
                <strong>💡 策略类型:</strong> 动量交易策略
                <p style="margin: 5px 0 0 0;">基于短期和中期移动平均线的趋势跟踪系统,结合成交量确认,捕捉市场动量。</p>
            </div>
            
            <div class="rule-item">
                <strong>🔍 核心算法:</strong>
                <ul style="margin: 5px 0;">
                    <li><strong>MA5</strong> (5日移动平均线): 短期趋势指标</li>
                    <li><strong>MA20</strong> (20日移动平均线): 中期趋势指标</li>
                    <li><strong>成交量确认:</strong> 必须超过20日平均成交量的1.3倍</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>📈 买入信号规则:</strong>
                <ul style="margin: 5px 0;">
                    <li>MA5 > MA20 (短期均线上穿中期均线,金叉)</li>
                    <li>当前价格 > MA5 (价格在短期均线之上)</li>
                    <li>成交量 > 20日平均成交量 × 1.3 (放量确认)</li>
                    <li>当前无持仓 (避免重复买入)</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>📉 卖出信号规则:</strong>
                <ul style="margin: 5px 0;">
                    <li>MA5 < MA20 (短期均线下穿中期均线,死叉)</li>
                    <li>当前价格 < MA5 (价格跌破短期均线)</li>
                    <li>成交量 > 20日平均成交量 × 1.3 (放量确认)</li>
                    <li>当前有持仓 (才能卖出)</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>🛡️ 风险管理:</strong>
                <ul style="margin: 5px 0;">
                    <li><strong>仓位控制:</strong> 单次交易使用60%可用资金</li>
                    <li><strong>止盈:</strong> 5% 获利自动卖出</li>
                    <li><strong>止损:</strong> 2% 亏损自动卖出</li>
                    <li><strong>风险收益比:</strong> 2.5:1 (符合资金管理原则)</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>⏰ 检查频率:</strong>
                <ul style="margin: 5px 0;">
                    <li>每周一至周五 21:00 (北京时间) 自动检查</li>
                    <li>信号产生后,在下一个交易日开盘时执行</li>
                    <li>节假日和非交易日自动跳过</li>
                </ul>
            </div>
            
            <p style="margin-top: 15px; padding: 12px; background: #ffebee; border-left: 4px solid #f44336; border-radius: 4px;">
                <strong>⚠️ 重要提示:</strong> 本策略基于技术分析,不构成投资建议。市场有风险,投资需谨慎。建议结合基本面分析和市场环境综合判断。
            </p>
        </div>
        
        <p style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
            <strong>⚠️ 提醒:</strong> 请在美股交易时间内执行,并记录交易详情
        </p>
    </div>
</body>
</html>
            """
            return html
        
        else:
            # 无信号通知 - 包含持仓信息
            # 构建持仓信息HTML
            position_html = ""
            if position_info and position_info.get('quantity', 0) > 0:
                # 有持仓
                symbol = position_info.get('symbol', 'N/A')
                quantity = position_info.get('quantity', 0)
                avg_price = position_info.get('avg_price', 0)
                current_price = position_info.get('current_price', 0)
                market_value = position_info.get('market_value', 0)
                profit_loss = position_info.get('profit_loss', 0)
                profit_loss_pct = position_info.get('profit_loss_pct', 0)
                
                # 盈亏颜色
                pnl_color = "#00AA00" if profit_loss >= 0 else "#FF0000"
                pnl_symbol = "+" if profit_loss >= 0 else ""
                
                position_html = f"""
        <div class="position-box">
            <h2 style="color: #667eea; margin-top: 0;">📊 当前持仓</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>股票代码</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{symbol}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>持仓数量</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;"><strong>{quantity:,} 股</strong></td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>平均成本</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${avg_price:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>当前价格</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${current_price:.2f}</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>市值</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;"><strong>${market_value:,.2f}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>浮动盈亏</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: {pnl_color};">
                        <strong>{pnl_symbol}${abs(profit_loss):,.2f} ({pnl_symbol}{profit_loss_pct:.2f}%)</strong>
                    </td>
                </tr>
            </table>
        </div>
                """
            else:
                # 空仓
                position_html = """
        <div class="position-box">
            <h2 style="color: #667eea; margin-top: 0;">📊 当前持仓</h2>
            <p style="text-align: center; font-size: 18px; color: #666; padding: 30px 0;">
                <strong>⚪ 空仓</strong><br>
                <span style="font-size: 14px;">等待买入信号</span>
            </p>
        </div>
                """
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 10px 10px;
        }}
        .success-box {{
            background: #d4edda;
            border: 1px solid #28a745;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            text-align: center;
        }}
        .position-box {{
            background: white;
            border: 2px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .strategy-box {{
            background: #fff8e1;
            border: 2px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .strategy-box h3 {{
            color: #ff6f00;
            margin-top: 0;
            margin-bottom: 15px;
        }}
        .strategy-box ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .strategy-box li {{
            margin: 8px 0;
        }}
        .rule-item {{
            background: white;
            padding: 10px;
            margin: 8px 0;
            border-left: 4px solid #ffc107;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ {strategy_type}检查完成</h1>
        <p>{symbol} 策略运行正常</p>
    </div>
    <div class="content">
        <div class="success-box">
            <h2 style="color: #28a745; margin-top: 0;">📊 {symbol} 检查结果</h2>
            <p style="font-size: 18px;"><strong>暂无新交易信号</strong></p>
            <p>策略运行正常,继续持有当前仓位即可</p>
        </div>
        {position_html}
        """
            
            # 添加附加信息(如基本面快照)
            if error_message and not is_error:
                # 将换行符转换为HTML换行
                formatted_message = error_message.replace('\n', '<br>')
                html += f"""
        <div style="background: #fff3cd; border: 2px solid #ffc107; padding: 20px; margin: 20px 0; border-radius: 5px;">
            {formatted_message}
        </div>
        """
            
            html += """
        <div class="strategy-box">
            <h3>📊 策略算法与规则说明</h3>
            
            <h4 style="color: #ff6f00; margin-top: 15px;">💡 策略类型: 动量交易策略</h4>
            <p style="margin: 10px 0;">基于短期和中期移动平均线的动量突破策略,结合成交量确认和风险管理。</p>
            
            <h4 style="color: #ff6f00; margin-top: 15px;">🔍 核心算法</h4>
            <div class="rule-item">
                <strong>1. 趋势判断 (双均线系统)</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li><strong>MA5</strong> (5日均线): 短期价格动量指标</li>
                    <li><strong>MA20</strong> (20日均线): 中期趋势方向指标</li>
                    <li><strong>金叉</strong>: MA5上穿MA20 → 多头信号</li>
                    <li><strong>死叉</strong>: MA5下穿MA20 → 空头信号</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>2. 成交量确认</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>成交量需超过<strong>20日平均成交量的1.3倍</strong></li>
                    <li>确保信号有足够的市场参与度和真实性</li>
                    <li>过滤掉低成交量的虚假突破</li>
                </ul>
            </div>
            
            <h4 style="color: #ff6f00; margin-top: 15px;">📈 交易信号规则</h4>
            <div class="rule-item">
                <strong>🟢 买入信号 (BUY)</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>MA5 > MA20 (短期均线在长期均线上方)</li>
                    <li>当日收盘价 > MA5 (价格在短期均线上方)</li>
                    <li>成交量 ≥ 1.3 × 平均成交量</li>
                    <li>当前无持仓(空仓状态)</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>🔴 卖出信号 (SELL)</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>MA5 < MA20 (短期均线在长期均线下方)</li>
                    <li>当日收盘价 < MA5 (价格在短期均线下方)</li>
                    <li>成交量 ≥ 1.3 × 平均成交量</li>
                    <li>当前有持仓</li>
                </ul>
            </div>
            
            <h4 style="color: #ff6f00; margin-top: 15px;">🛡️ 风险管理</h4>
            <div class="rule-item">
                <strong>仓位管理</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li><strong>固定仓位比例</strong>: 每次交易使用账户资金的<strong>60%</strong></li>
                    <li><strong>保留现金</strong>: 40%现金应对突发情况</li>
                </ul>
            </div>
            
            <div class="rule-item">
                <strong>止盈止损</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li><strong>止盈</strong>: 盈利达到<strong>5%</strong>自动平仓</li>
                    <li><strong>止损</strong>: 亏损达到<strong>2%</strong>自动平仓</li>
                    <li><strong>风险收益比</strong>: 2.5:1 (高于行业标准的2:1)</li>
                </ul>
            </div>
            
            <h4 style="color: #ff6f00; margin-top: 15px;">⏰ 检查频率</h4>
            <div class="rule-item">
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li><strong>检查时间</strong>: 每周一至周五晚上21:00</li>
                    <li><strong>数据更新</strong>: 使用当日美股收盘后数据</li>
                    <li><strong>信号生成</strong>: 基于最新1天的K线数据</li>
                    <li><strong>执行时间</strong>: 次日美股交易时段(9:30-16:00 ET)</li>
                </ul>
            </div>
            
            <p style="margin-top: 15px; padding: 10px; background: #ffe082; border-radius: 5px;">
                <strong>⚠️ 重要提示:</strong> 本策略为技术分析策略,仅供参考。实际交易请结合基本面分析、市场情绪、宏观经济等多方面因素综合判断。
            </p>
        </div>
        
        <p style="padding: 15px; background: #e7f3ff; border-radius: 5px;">
            <strong>💡 提示:</strong> 无需任何操作,系统将继续自动检查
        </p>
        <p style="text-align: center; color: #666; margin-top: 30px;">
            📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
</body>
</html>
            """
            return html
    
    def _send_email(self, subject: str, body: str) -> bool:
        """
        发送邮件 (支持多账户故障转移)
        
        发送策略:
        1. 依次尝试所有配置的邮件账户
        2. 如果第一个账户失败,自动切换到下一个
        3. 每个账户都有重试机制
        4. 只要有一个账户发送成功即可
        
        Args:
            subject: 邮件主题
            body: 邮件正文 (HTML格式)
        
        Returns:
            bool: 是否发送成功
        """
        if not self.config.accounts:
            print("❌ 错误: 没有配置任何邮件账户!")
            return False
        
        # 遍历所有邮件账户,依次尝试
        for account_idx, account in enumerate(self.config.accounts, 1):
            print(f"\n{'='*60}")
            print(f"📧 尝试使用账户 {account_idx}/{len(self.config.accounts)}: {account.name} ({account.sender_email})")
            print(f"{'='*60}")
            
            # 尝试用当前账户发送
            if self._send_with_account(account, subject, body):
                print(f"\n✅ 邮件发送成功! 使用账户: {account.name}")
                return True
            else:
                print(f"\n⚠️ 账户 {account.name} 发送失败")
                if account_idx < len(self.config.accounts):
                    print(f"⏭️  正在切换到下一个账户...")
        
        # 所有账户都失败
        print(f"\n{'='*60}")
        print(f"❌ 邮件发送失败: 已尝试所有 {len(self.config.accounts)} 个账户")
        print(f"{'='*60}")
        return False
    
    def _send_with_account(self, account, subject: str, body: str) -> bool:
        """
        使用指定账户发送邮件 (带重试机制)
        
        Args:
            account: 邮件账户配置
            subject: 邮件主题
            body: 邮件正文
        
        Returns:
            bool: 是否发送成功
        """
        max_retries = 3  # 每个账户重试3次
        retry_delay = 5   # 每次重试间隔5秒
        timeout = 60      # SMTP超时60秒
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"⏳ 重试 {attempt}/{max_retries}...")
                    time.sleep(retry_delay)
                
                # 创建邮件对象
                message = MIMEMultipart('alternative')
                message['From'] = account.sender_email
                message['To'] = self.config.recipient_email
                message['Subject'] = Header(subject, 'utf-8')
                
                # 添加HTML正文
                html_part = MIMEText(body, 'html', 'utf-8')
                message.attach(html_part)
                
                # 连接SMTP服务器并发送
                print(f"📧 正在连接 {account.smtp_server}:{account.smtp_port}...")
                
                if account.use_ssl:
                    # 使用SSL
                    server = smtplib.SMTP_SSL(account.smtp_server, account.smtp_port, timeout=timeout)
                    try:
                        server.set_debuglevel(0)
                        print("📧 正在登录...")
                        server.login(account.sender_email, account.sender_password)
                        
                        print("📧 正在发送邮件...")
                        server.send_message(message)
                        print(f"✅ 邮件发送成功! {account.sender_email} → {self.config.recipient_email}")
                        
                        # 发送成功,关闭连接并返回
                        try:
                            server.quit()
                        except:
                            pass  # 忽略quit错误
                        return True
                    finally:
                        try:
                            server.close()
                        except:
                            pass
                else:
                    # 使用TLS
                    server = smtplib.SMTP(account.smtp_server, account.smtp_port, timeout=timeout)
                    try:
                        server.set_debuglevel(0)
                        
                        if account.use_tls:
                            print("📧 正在启动TLS...")
                            server.starttls()
                        
                        print("📧 正在登录...")
                        server.login(account.sender_email, account.sender_password)
                        
                        print("📧 正在发送邮件...")
                        server.send_message(message)
                        print(f"✅ 邮件发送成功! {account.sender_email} → {self.config.recipient_email}")
                        
                        # 发送成功,关闭连接并返回
                        try:
                            server.quit()
                        except:
                            pass  # 忽略quit错误
                        return True
                    finally:
                        try:
                            server.close()
                        except:
                            pass
                    
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ 认证失败: {e}")
                print(f"   账户: {account.sender_email}")
                print(f"   请检查邮箱地址和授权码是否正确")
                return False  # 认证错误不重试,直接切换账户
            except (socket.timeout, TimeoutError) as e:
                print(f"⚠️ 网络超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print(f"⚠️ 账户 {account.sender_email} 超时")
                    return False
                # 继续重试
            except OSError as e:
                # OSError通常表示连接被重置或其他网络问题
                print(f"⚠️ 网络错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    print(f"⚠️ 账户 {account.sender_email} 网络错误")
                    return False
                # 继续重试
            except smtplib.SMTPException as e:
                print(f"❌ SMTP错误: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ 将在 {retry_delay} 秒后重试...")
                else:
                    return False
            except Exception as e:
                print(f"❌ 发送错误: {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ 将在 {retry_delay} 秒后重试...")
                else:
                    return False
        
        return False


def test_email():
    """测试邮件发送"""
    print("=" * 60)
    print("📧 邮件推送测试 (多账户故障转移)")
    print("=" * 60)
    print()
    
    service = EmailService()
    
    print("配置信息:")
    print(f"  收件人: {service.config.recipient_email}")
    print(f"  已启用: {service.config.enabled}")
    print(f"  配置账户数: {len(service.config.accounts)}")
    print()
    
    print("发件账户列表 (按优先级):")
    for idx, account in enumerate(service.config.accounts, 1):
        print(f"  {idx}. {account.name}")
        print(f"     邮箱: {account.sender_email}")
        print(f"     服务器: {account.smtp_server}:{account.smtp_port}")
        print(f"     SSL: {account.use_ssl}, TLS: {account.use_tls}")
        print()
    
    # 测试发送信号提醒
    print("测试: 发送交易信号提醒...")
    print("-" * 60)
    
    success = service.send_signal_alert(
        symbol="TSLA",
        action="BUY",
        quantity=2076,
        price=250.50,
        reason="趋势确认 + 强势突破信号",
        signal_date="2025-11-15"
    )
    
    print()
    print("=" * 60)
    if success:
        print("✅ 邮件推送测试通过!")
        print(f"请检查邮箱: {service.config.recipient_email}")
    else:
        print("❌ 邮件推送测试失败!")
        print("所有配置的邮件账户都无法发送")
    print("=" * 60)
    print()


if __name__ == "__main__":
    test_email()
