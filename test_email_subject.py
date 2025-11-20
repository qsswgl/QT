"""测试邮件主题 - 添加时间戳避免Gmail分组"""
from datetime import datetime
from src.notification.email_service import EmailService
from src.notification.email_config import email_config

# 创建邮件服务
service = EmailService(email_config)

# 获取当前时间
now = datetime.now().strftime('%H:%M:%S')

# 修改send_daily_summary方法,在主题中加上时间
class TestEmailService(EmailService):
    def send_daily_summary(self, has_signal, signal_count=0, latest_signal=None, 
                          error_message=None, position_info=None, symbol="TSLA"):
        if not self.config.enabled:
            print("📧 邮件推送未启用")
            return False
        
        # 构建动态主题前缀(加上时间戳)
        time_str = datetime.now().strftime('%H:%M:%S')
        subject_prefix = f"[{symbol}策略]"
        
        # 构建邮件主题
        if error_message:
            subject = f"{subject_prefix} ⚠️ {symbol} 每日检查失败 ({time_str})"
        elif has_signal:
            subject = f"{subject_prefix} 🚨 {symbol} 发现新信号! ({time_str})"
        else:
            subject = f"{subject_prefix} ✅ {symbol} 每日检查完成 - 无新信号 ({time_str})"
        
        # 调试输出
        print(f"📧 邮件主题: {subject}")
        
        # 构建邮件正文
        body = self._build_summary_email_body(
            has_signal, signal_count, latest_signal, error_message, 
            strategy_type="日度策略", position_info=position_info, symbol=symbol
        )
        
        # 发送邮件
        return self._send_email(subject, body)

# 使用测试服务
test_service = TestEmailService(email_config)

# 发送INTC测试邮件
print("="*80)
print("发送 INTC 测试邮件(带时间戳)")
print("="*80)
result = test_service.send_daily_summary(
    has_signal=False,
    signal_count=0,
    latest_signal=None,
    error_message=None,
    position_info={
        'symbol': 'INTC',
        'quantity': 0,
        'avg_price': 0,
        'current_price': 23.5,
        'market_value': 0,
        'profit_loss': 0,
        'profit_loss_pct': 0
    },
    symbol='INTC'
)
print(f"\n✅ INTC测试邮件发送{'成功' if result else '失败'}\n")

# 发送NVDA测试邮件
print("="*80)
print("发送 NVDA 测试邮件(带时间戳)")
print("="*80)
result = test_service.send_daily_summary(
    has_signal=False,
    signal_count=0,
    latest_signal=None,
    error_message=None,
    position_info={
        'symbol': 'NVDA',
        'quantity': 0,
        'avg_price': 0,
        'current_price': 145.8,
        'market_value': 0,
        'profit_loss': 0,
        'profit_loss_pct': 0
    },
    symbol='NVDA'
)
print(f"\n✅ NVDA测试邮件发送{'成功' if result else '失败'}\n")

print("="*80)
print("📬 请查看您的Gmail邮箱,主题中应该包含时间戳")
print("📬 例如: [INTC策略] ✅ INTC 每日检查完成 - 无新信号 (20:15:30)")
print("="*80)
