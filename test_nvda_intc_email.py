"""
单独测试发送NVDA和INTC邮件
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import time

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.notification.email_service import EmailService


def send_simple_test(symbol: str):
    """发送简单测试邮件"""
    print(f"\n{'='*60}")
    print(f"📧 测试发送 {symbol} 邮件")
    print(f"{'='*60}")
    
    service = EmailService()
    
    # 发送简单测试邮件
    subject = f"[{symbol}策略] 🔔 测试邮件 - {datetime.now().strftime('%H:%M:%S')}"
    
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .content {{
            padding: 20px;
            line-height: 1.8;
        }}
        .highlight {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 {symbol} 策略邮件测试</h1>
            <p>邮件推送系统测试</p>
        </div>
        
        <div class="content">
            <h2>📊 测试信息</h2>
            <p><strong>股票代码:</strong> {symbol}</p>
            <p><strong>测试时间:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            <p><strong>邮件编号:</strong> TEST-{symbol}-{int(time.time())}</p>
            
            <div class="highlight">
                <p><strong>⚠️ 这是一封测试邮件</strong></p>
                <p>用于验证{symbol}的邮件推送功能是否正常工作。</p>
                <p>如果您收到这封邮件,说明{symbol}的邮件系统配置正确。</p>
            </div>
            
            <h3>✅ 验证项目</h3>
            <ul>
                <li>✓ 邮件服务器连接正常</li>
                <li>✓ HTML格式渲染正确</li>
                <li>✓ 中文编码无问题</li>
                <li>✓ 收件人地址正确</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>📧 收件人: qsswgl@gmail.com</p>
            <p>📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            <p>🤖 {symbol} 策略自动推送系统</p>
        </div>
    </div>
</body>
</html>
"""
    
    print(f"\n发送邮件到: {service.config.recipient_email}")
    print(f"主题: {subject}")
    print(f"内容长度: {len(body)} 字符")
    print()
    
    success = service._send_email(subject, body)
    
    if success:
        print(f"\n✅ {symbol} 测试邮件发送成功!")
        print(f"请检查邮箱 {service.config.recipient_email}")
    else:
        print(f"\n❌ {symbol} 测试邮件发送失败!")
    
    return success


def main():
    """主函数"""
    print("="*60)
    print("📧 NVDA和INTC邮件测试")
    print("="*60)
    print()
    print("目的: 验证NVDA和INTC的邮件是否能够成功送达")
    print("收件人: qsswgl@gmail.com")
    print()
    
    # 发送NVDA测试邮件
    print("\n" + "="*60)
    print("测试 1/2: NVDA")
    print("="*60)
    nvda_success = send_simple_test("NVDA")
    
    # 等待5秒,避免邮件服务器限流
    print("\n⏳ 等待5秒,避免邮件服务器限流...")
    time.sleep(5)
    
    # 发送INTC测试邮件
    print("\n" + "="*60)
    print("测试 2/2: INTC")
    print("="*60)
    intc_success = send_simple_test("INTC")
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    print(f"NVDA: {'✅ 成功' if nvda_success else '❌ 失败'}")
    print(f"INTC: {'✅ 成功' if intc_success else '❌ 失败'}")
    print()
    
    if nvda_success and intc_success:
        print("✅ 所有测试邮件发送成功!")
        print()
        print("📬 请检查邮箱:")
        print("   1. 收件箱")
        print("   2. 垃圾邮件文件夹")
        print("   3. 促销邮件标签")
        print()
        print("🔍 查找关键词:")
        print("   - [NVDA策略]")
        print("   - [INTC策略]")
        print("   - 测试邮件")
    else:
        print("⚠️ 部分邮件发送失败,请检查错误信息")
    
    print("="*60)


if __name__ == "__main__":
    main()
