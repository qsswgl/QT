# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
邮件系统诊断工具
检查邮件配置和网络连接
"""
import sys
from pathlib import Path
import socket
import smtplib
from email.mime.text import MIMEText

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.notification.email_config import email_config


def test_network_connectivity():
    """测试网络连接"""
    print("=" * 70)
    print("🔍 步骤 1/5: 测试网络连接")
    print("=" * 70)
    
    try:
        # 测试DNS解析
        print("📡 测试DNS解析...")
        host = email_config.smtp_server
        ip = socket.gethostbyname(host)
        print(f"✅ {host} 解析成功")
        print(f"   IP地址: {ip}")
        
        # 测试端口连接
        print(f"\n📡 测试端口连接 ({host}:{email_config.smtp_port})...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, email_config.smtp_port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {email_config.smtp_port} 连接成功")
            return True
        else:
            print(f"❌ 端口 {email_config.smtp_port} 连接失败 (错误代码: {result})")
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 网络测试失败: {e}")
        return False


def test_smtp_connection():
    """测试SMTP连接"""
    print("\n" + "=" * 70)
    print("🔍 步骤 2/5: 测试SMTP连接")
    print("=" * 70)
    
    try:
        print("📧 连接SMTP服务器...")
        server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port, timeout=30)
        print("✅ SMTP连接成功")
        
        print("\n📧 启动TLS加密...")
        server.starttls()
        print("✅ TLS加密成功")
        
        server.quit()
        return True
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP连接错误: {e}")
        return False
    except socket.timeout:
        print("❌ 连接超时 - 可能是网络防火墙阻止")
        return False
    except Exception as e:
        print(f"❌ SMTP测试失败: {e}")
        return False


def test_authentication():
    """测试邮箱认证"""
    print("\n" + "=" * 70)
    print("🔍 步骤 3/5: 测试邮箱认证")
    print("=" * 70)
    
    if not email_config.sender_password:
        print("❌ 邮箱密码未配置")
        print("💡 请在 email_config.py 中设置 sender_password")
        return False
    
    try:
        print(f"📧 使用账号: {email_config.sender_email}")
        print("📧 尝试登录...")
        
        server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port, timeout=30)
        server.starttls()
        server.login(email_config.sender_email, email_config.sender_password)
        print("✅ 邮箱认证成功")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ 认证失败: {e}")
        print("\n💡 可能的原因:")
        print("   1. 应用专用密码错误")
        print("   2. Gmail账户未启用'不够安全的应用'访问权限")
        print("   3. 需要重新生成应用专用密码")
        return False
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")
        return False


def test_send_email():
    """测试发送邮件"""
    print("\n" + "=" * 70)
    print("🔍 步骤 4/5: 测试发送邮件")
    print("=" * 70)
    
    try:
        print(f"📧 发送测试邮件到: {email_config.recipient_email}")
        
        server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port, timeout=30)
        server.starttls()
        server.login(email_config.sender_email, email_config.sender_password)
        
        # 构建测试邮件
        msg = MIMEText("这是一封测试邮件，用于验证邮件系统配置。\n\n如果您收到此邮件，说明邮件系统工作正常！", 'plain', 'utf-8')
        msg['From'] = email_config.sender_email
        msg['To'] = email_config.recipient_email
        msg['Subject'] = "[测试] QT量化交易系统 - 邮件功能测试"
        
        server.send_message(msg)
        server.quit()
        
        print("✅ 测试邮件发送成功!")
        print(f"\n💡 请检查 {email_config.recipient_email}")
        print("   (包括垃圾邮件文件夹)")
        return True
        
    except Exception as e:
        print(f"❌ 发送邮件失败: {e}")
        return False


def check_configuration():
    """检查配置"""
    print("\n" + "=" * 70)
    print("🔍 步骤 5/5: 检查配置")
    print("=" * 70)
    
    print(f"📧 邮件服务: {'✅ 已启用' if email_config.enabled else '❌ 已禁用'}")
    print(f"📧 SMTP服务器: {email_config.smtp_server}")
    print(f"📧 SMTP端口: {email_config.smtp_port}")
    print(f"📧 发件人: {email_config.sender_email}")
    print(f"📧 收件人: {email_config.recipient_email}")
    print(f"📧 密码: {'✅ 已配置' if email_config.sender_password else '❌ 未配置'}")
    
    if not email_config.enabled:
        print("\n⚠️ 邮件服务已禁用")
        print("💡 在 src/notification/email_config.py 中启用")
    
    if not email_config.sender_password:
        print("\n⚠️ 邮箱密码未配置")
        print("💡 在 src/notification/email_config.py 中配置 sender_password")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("📊 QT量化交易系统 - 邮件系统诊断")
    print("=" * 70)
    print()
    
    # 检查配置
    check_configuration()
    
    if not email_config.enabled:
        print("\n❌ 邮件服务已禁用，无法进行测试")
        return
    
    # 测试网络
    network_ok = test_network_connectivity()
    
    if not network_ok:
        print("\n" + "=" * 70)
        print("❌ 网络连接失败，无法继续测试")
        print("=" * 70)
        print("\n💡 可能的原因:")
        print("   1. 没有网络连接")
        print("   2. 防火墙阻止了SMTP端口 (587)")
        print("   3. VPN或代理设置问题")
        print("\n💡 解决方法:")
        print("   1. 检查网络连接")
        print("   2. 关闭防火墙或添加例外规则")
        print("   3. 尝试使用其他网络")
        return
    
    # 测试SMTP连接
    smtp_ok = test_smtp_connection()
    
    if not smtp_ok:
        print("\n" + "=" * 70)
        print("❌ SMTP连接失败")
        print("=" * 70)
        return
    
    # 测试认证
    auth_ok = test_authentication()
    
    if not auth_ok:
        print("\n" + "=" * 70)
        print("❌ 邮箱认证失败")
        print("=" * 70)
        print("\n💡 解决步骤:")
        print("   1. 访问: https://myaccount.google.com/apppasswords")
        print("   2. 生成新的应用专用密码")
        print("   3. 设置环境变量: setx GMAIL_APP_PASSWORD \"新密码\"")
        print("   4. 重启PowerShell并重新测试")
        return
    
    # 测试发送
    send_ok = test_send_email()
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    print(f"✅ 网络连接: {'通过' if network_ok else '失败'}")
    print(f"✅ SMTP连接: {'通过' if smtp_ok else '失败'}")
    print(f"✅ 邮箱认证: {'通过' if auth_ok else '失败'}")
    print(f"✅ 发送邮件: {'通过' if send_ok else '失败'}")
    
    if network_ok and smtp_ok and auth_ok and send_ok:
        print("\n🎉 邮件系统完全正常!")
        print("💡 如果策略运行时仍无法收到邮件，可能是:")
        print("   1. 邮件被Gmail标记为垃圾邮件")
        print("   2. 策略没有生成新信号(检查信号日期)")
        print("   3. 查看策略执行日志中的错误信息")
    else:
        print("\n❌ 邮件系统存在问题，请根据上述提示修复")


if __name__ == "__main__":
    main()
