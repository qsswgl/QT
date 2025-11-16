"""
快速测试策略邮件发送
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.notification.email_service import EmailService

def test_strategy_email():
    """测试策略邮件发送"""
    print("=" * 80)
    print("📧 测试策略邮件发送")
    print("=" * 80)
    print()
    
    service = EmailService()
    
    print("配置信息:")
    print(f"  发件人: {service.config.sender_email}")
    print(f"  收件人: {service.config.recipient_email}")
    print(f"  SMTP: {service.config.smtp_server}:{service.config.smtp_port}")
    print()
    
    # 测试1: 发送信号提醒
    print("=" * 80)
    print("测试1: 发送交易信号提醒")
    print("=" * 80)
    
    success = service.send_signal_alert(
        symbol="TSLA",
        action="BUY",
        quantity=100,
        price=250.50,
        reason="测试信号",
        signal_date="2025-11-15"
    )
    
    if success:
        print("✅ 信号提醒发送成功")
    else:
        print("❌ 信号提醒发送失败")
    
    print()
    
    # 测试2: 发送每日总结
    print("=" * 80)
    print("测试2: 发送每日总结")
    print("=" * 80)
    
    success = service.send_daily_summary(
        symbol="TSLA",
        latest_price=250.50,
        price_change=-1.5,
        no_signal_days=5,
        last_signal_date="2025-10-24",
        last_signal_action="SELL",
        last_signal_price=433.72
    )
    
    if success:
        print("✅ 每日总结发送成功")
    else:
        print("❌ 每日总结发送失败")
    
    print()
    print("=" * 80)
    print("✅ 测试完成!")
    print("=" * 80)
    print()
    print("💡 请检查邮箱: qsswgl@gmail.com")


if __name__ == "__main__":
    try:
        test_strategy_email()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
