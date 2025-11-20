"""最终测试 - 验证所有股票的邮件主题"""
from src.notification.email_service import EmailService
from src.notification.email_config import email_config

service = EmailService(email_config)

print("="*80)
print("📧 最终测试 - 验证邮件主题")
print("="*80)

# 测试INTC
print("\n[1/3] 发送 INTC 测试邮件...")
result = service.send_daily_summary(
    has_signal=False,
    signal_count=0,
    latest_signal=None,
    error_message=None,
    position_info={'symbol': 'INTC', 'quantity': 0, 'avg_price': 0, 
                   'current_price': 23.5, 'market_value': 0, 
                   'profit_loss': 0, 'profit_loss_pct': 0},
    symbol='INTC'
)
print(f"✅ INTC 发送{'成功' if result else '失败'}")

# 测试NVDA
print("\n[2/3] 发送 NVDA 测试邮件...")
result = service.send_daily_summary(
    has_signal=False,
    signal_count=0,
    latest_signal=None,
    error_message=None,
    position_info={'symbol': 'NVDA', 'quantity': 0, 'avg_price': 0, 
                   'current_price': 145.8, 'market_value': 0, 
                   'profit_loss': 0, 'profit_loss_pct': 0},
    symbol='NVDA'
)
print(f"✅ NVDA 发送{'成功' if result else '失败'}")

# 测试TSLA
print("\n[3/3] 发送 TSLA 测试邮件...")
result = service.send_daily_summary(
    has_signal=False,
    signal_count=0,
    latest_signal=None,
    error_message=None,
    position_info={'symbol': 'TSLA', 'quantity': 0, 'avg_price': 0, 
                   'current_price': 401.99, 'market_value': 0, 
                   'profit_loss': 0, 'profit_loss_pct': 0},
    symbol='TSLA'
)
print(f"✅ TSLA 发送{'成功' if result else '失败'}")

print("\n" + "="*80)
print("✅ 测试完成!请检查Gmail收件箱:")
print("   - [INTC策略] ✅ INTC 每日检查完成 - 无新信号")
print("   - [NVDA策略] ✅ NVDA 每日检查完成 - 无新信号")
print("   - [TSLA策略] ✅ TSLA 每日检查完成 - 无新信号")
print("="*80)
