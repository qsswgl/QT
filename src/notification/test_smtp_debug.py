"""
SMTP连接详细调试工具
用于诊断Gmail SMTP连接的具体问题
"""
import smtplib
import socket
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.notification.email_config import email_config


def test_smtp_with_timeout():
    """测试不同超时时间下的SMTP连接"""
    
    print("=" * 80)
    print("📧 SMTP连接详细诊断")
    print("=" * 80)
    print()
    
    timeouts = [10, 30, 60, 120]  # 测试不同的超时时间
    
    for timeout_seconds in timeouts:
        print(f"\n{'=' * 80}")
        print(f"🔍 测试超时时间: {timeout_seconds}秒")
        print("=" * 80)
        
        server = None
        start_time = time.time()
        
        try:
            # 步骤1: 创建连接
            print(f"\n[1/4] 📡 创建连接 (超时{timeout_seconds}秒)...")
            step_start = time.time()
            server = smtplib.SMTP(
                email_config.smtp_server, 
                email_config.smtp_port,
                timeout=timeout_seconds
            )
            step_time = time.time() - step_start
            print(f"    ✅ 连接成功 (耗时: {step_time:.2f}秒)")
            
            # 步骤2: TLS握手
            print(f"\n[2/4] 🔒 启动TLS加密...")
            step_start = time.time()
            server.starttls()
            step_time = time.time() - step_start
            print(f"    ✅ TLS加密成功 (耗时: {step_time:.2f}秒)")
            
            # 步骤3: SMTP登录
            print(f"\n[3/4] 🔑 SMTP登录...")
            print(f"    用户: {email_config.sender_email}")
            step_start = time.time()
            server.login(email_config.sender_email, email_config.sender_password)
            step_time = time.time() - step_start
            print(f"    ✅ 登录成功 (耗时: {step_time:.2f}秒)")
            
            # 步骤4: 发送测试邮件
            print(f"\n[4/4] 📧 发送测试邮件...")
            step_start = time.time()
            
            from email.mime.text import MIMEText
            from email.header import Header
            
            msg = MIMEText(f"SMTP调试测试 (超时{timeout_seconds}秒)", 'plain', 'utf-8')
            msg['From'] = Header(email_config.sender_email, 'utf-8')
            msg['To'] = Header(email_config.recipient_email, 'utf-8')
            msg['Subject'] = Header(f'[测试] SMTP调试 ({timeout_seconds}s超时)', 'utf-8')
            
            server.send_message(msg)
            step_time = time.time() - step_start
            print(f"    ✅ 邮件发送成功 (耗时: {step_time:.2f}秒)")
            
            # 总结
            total_time = time.time() - start_time
            print(f"\n{'=' * 80}")
            print(f"✅ 完整流程成功! 总耗时: {total_time:.2f}秒")
            print(f"{'=' * 80}")
            
            # 成功后退出
            server.quit()
            print(f"\n💡 建议: 使用 {timeout_seconds}秒 作为超时时间")
            return timeout_seconds
            
        except socket.timeout as e:
            elapsed = time.time() - start_time
            print(f"\n    ❌ 超时错误 (已等待{elapsed:.2f}秒): {e}")
            print(f"    💡 建议: 尝试更长的超时时间")
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"\n    ❌ 认证失败: {e}")
            print(f"    💡 建议: 检查邮箱地址和应用专用密码")
            break  # 认证错误不用继续测试
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n    ❌ 错误 (已等待{elapsed:.2f}秒): {type(e).__name__}: {e}")
            
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass
    
    print(f"\n{'=' * 80}")
    print("❌ 所有超时设置均失败")
    print("=" * 80)
    print()
    print("💡 可能的原因:")
    print("   1. 网络防火墙阻止SMTP连接")
    print("   2. ISP限制Gmail SMTP访问")
    print("   3. 需要使用VPN/代理")
    print("   4. 考虑换用国内邮箱(QQ/163)")
    print()
    return None


def test_simple_socket():
    """测试原始socket连接"""
    print("\n" + "=" * 80)
    print("🔍 原始Socket连接测试")
    print("=" * 80)
    print()
    
    try:
        print(f"📡 连接 {email_config.smtp_server}:{email_config.smtp_port}...")
        
        # 测试原始TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        start_time = time.time()
        sock.connect((email_config.smtp_server, email_config.smtp_port))
        elapsed = time.time() - start_time
        
        print(f"✅ TCP连接成功 (耗时: {elapsed:.2f}秒)")
        
        # 接收SMTP欢迎消息
        welcome = sock.recv(1024).decode()
        print(f"📧 SMTP欢迎消息: {welcome.strip()}")
        
        sock.close()
        
    except socket.timeout:
        print("❌ Socket连接超时")
        print("   这说明网络层面无法访问Gmail SMTP服务器")
        print("   💡 建议: 使用VPN或换用其他邮箱")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")


def main():
    print("\n")
    print("=" * 80)
    print("📊 QT量化交易系统 - SMTP详细诊断工具")
    print("=" * 80)
    print()
    print("📋 配置信息:")
    print(f"   SMTP服务器: {email_config.smtp_server}")
    print(f"   SMTP端口: {email_config.smtp_port}")
    print(f"   发件人: {email_config.sender_email}")
    print(f"   收件人: {email_config.recipient_email}")
    print()
    
    # 测试1: 原始socket连接
    test_simple_socket()
    
    print("\n" + "=" * 80)
    input("按Enter键继续测试SMTP连接...")
    print("=" * 80)
    
    # 测试2: SMTP连接（不同超时时间）
    recommended_timeout = test_smtp_with_timeout()
    
    if recommended_timeout:
        print(f"\n{'=' * 80}")
        print("✅ 诊断完成!")
        print("=" * 80)
        print()
        print(f"📝 建议配置:")
        print(f"   在 email_service.py 的 _send_email 方法中设置:")
        print(f"   timeout = {recommended_timeout}  # 秒")
        print()
    else:
        print(f"\n{'=' * 80}")
        print("❌ 网络问题诊断完成")
        print("=" * 80)
        print()
        print("📝 详细排查方案请查看:")
        print("   K:\\QT\\EMAIL_NETWORK_TROUBLESHOOTING.md")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
