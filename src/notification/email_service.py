"""
邮件发送服务
"""
import smtplib
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
        
        # 构建邮件主题
        action_cn = "买入" if action == "BUY" else "卖出"
        subject = f"{self.config.subject_prefix} 🚨 {strategy_name} - {symbol} {action_cn}信号!"
        
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
            has_signal, signal_count, latest_signal, error_message
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
        error_message: Optional[str]
    ) -> str:
        """构建每周总结邮件正文"""
        
        if error_message:
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
        <h1>⚠️ 策略检查失败</h1>
    </div>
    <div class="content">
        <div class="error-box">
            <h3>错误信息:</h3>
            <p>{error_message}</p>
        </div>
        <p>建议: 手动运行 weekly_check.bat 检查详细错误</p>
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
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 发现新信号!</h1>
        <p>TSLA 策略每周检查</p>
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
        <p style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px;">
            <strong>⚠️ 提醒:</strong> 请在美股交易时间内执行,并记录交易详情
        </p>
    </div>
</body>
</html>
            """
            return html
        
        else:
            # 无信号通知
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
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ 每周检查完成</h1>
        <p>TSLA 策略运行正常</p>
    </div>
    <div class="content">
        <div class="success-box">
            <h2 style="color: #28a745; margin-top: 0;">📊 检查结果</h2>
            <p style="font-size: 18px;"><strong>暂无新交易信号</strong></p>
            <p>策略运行正常,继续持有当前仓位即可</p>
        </div>
        <p style="padding: 15px; background: #e7f3ff; border-radius: 5px;">
            <strong>💡 提示:</strong> 无需任何操作,下周继续自动检查
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
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件正文 (HTML格式)
        
        Returns:
            bool: 是否发送成功
        """
        try:
            # 创建邮件对象
            message = MIMEMultipart('alternative')
            message['From'] = Header(f"TSLA策略提醒 <{self.config.sender_email}>", 'utf-8')
            message['To'] = Header(self.config.recipient_email, 'utf-8')
            message['Subject'] = Header(subject, 'utf-8')
            
            # 添加HTML正文
            html_part = MIMEText(body, 'html', 'utf-8')
            message.attach(html_part)
            
            # 连接SMTP服务器并发送
            print(f"📧 正在连接邮件服务器 {self.config.smtp_server}:{self.config.smtp_port}...")
            
            if self.config.use_ssl:
                # 使用SSL
                with smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port) as server:
                    print("📧 正在登录...")
                    server.login(self.config.sender_email, self.config.sender_password)
                    
                    print("📧 正在发送邮件...")
                    server.send_message(message)
                    
                    print(f"✅ 邮件发送成功! → {self.config.recipient_email}")
                    return True
            else:
                # 使用TLS
                with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                    server.set_debuglevel(0)  # 关闭调试信息
                    
                    if self.config.use_tls:
                        print("📧 正在启动TLS...")
                        server.starttls()
                    
                    print("📧 正在登录...")
                    server.login(self.config.sender_email, self.config.sender_password)
                    
                    print("📧 正在发送邮件...")
                    server.send_message(message)
                    
                    print(f"✅ 邮件发送成功! → {self.config.recipient_email}")
                    return True
                
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ 邮件认证失败: {e}")
            print("   请检查邮箱地址和SMTP授权码是否正确")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 发送邮件时发生错误: {e}")
            return False


def test_email():
    """测试邮件发送"""
    print("=" * 60)
    print("📧 邮件推送测试")
    print("=" * 60)
    print()
    
    service = EmailService()
    
    print("配置信息:")
    print(f"  发件人: {service.config.sender_email}")
    print(f"  收件人: {service.config.recipient_email}")
    print(f"  SMTP服务器: {service.config.smtp_server}:{service.config.smtp_port}")
    print(f"  已启用: {service.config.enabled}")
    print()
    
    # 测试发送信号提醒
    print("测试1: 发送交易信号提醒...")
    print("-" * 60)
    
    success = service.send_signal_alert(
        symbol="TSLA",
        action="BUY",
        quantity=2076,
        price=250.50,
        reason="趋势确认 + 强势突破信号",
        signal_date="2025-11-12"
    )
    
    if success:
        print("✅ 测试1通过")
    else:
        print("❌ 测试1失败")
    
    print()
    print("=" * 60)
    print("✅ 邮件推送测试完成!")
    print("=" * 60)
    print()
    print("请检查你的邮箱: qsoft@139.com")
    print()


if __name__ == "__main__":
    test_email()
