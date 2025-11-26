"""
测试增强后的邮件模板(包含策略说明)
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.notification.email_service import EmailService

def test_no_signal_email():
    """测试无信号邮件(包含策略说明)"""
    print("=" * 50)
    print("测试无信号邮件(包含策略说明)")
    print("=" * 50)
    
    email_service = EmailService()
    
    # 模拟持仓信息
    position_info = {
        'symbol': 'NVDA',
        'quantity': 100,
        'avg_price': 450.50,
        'current_price': 485.20,
        'market_value': 48520.00,
        'profit_loss': 3470.00,
        'profit_loss_pct': 7.70
    }
    
    try:
        email_service.send_daily_summary(
            has_signal=False,
            signal_count=0,
            latest_signal=None,
            error_message=None,
            position_info=position_info,
            symbol='NVDA'
        )
        print("✅ 无信号邮件发送成功 (NVDA)")
    except Exception as e:
        print(f"❌ 无信号邮件发送失败: {e}")

def test_signal_email():
    """测试有信号邮件(包含策略说明)"""
    print("\n" + "=" * 50)
    print("测试有信号邮件(包含策略说明)")
    print("=" * 50)
    
    email_service = EmailService()
    
    # 模拟买入信号
    latest_signal = {
        'action': 'BUY',
        'quantity': 100,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'price': 485.20
    }
    
    try:
        email_service.send_daily_summary(
            has_signal=True,
            signal_count=1,
            latest_signal=latest_signal,
            error_message=None,
            position_info=None,
            symbol='INTC'
        )
        print("✅ 有信号邮件发送成功 (INTC)")
    except Exception as e:
        print(f"❌ 有信号邮件发送失败: {e}")

if __name__ == '__main__':
    # 测试两种邮件类型
    test_no_signal_email()
    test_signal_email()
    
    print("\n" + "=" * 50)
    print("测试完成!请检查邮箱查看效果")
    print("=" * 50)
