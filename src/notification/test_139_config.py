"""
139邮箱 SMTP 配置测试工具
测试不同的端口和加密方式
"""
import smtplib
import socket
from email.mime.text import MIMEText
from email.header import Header
import time

configs = [
    {
        "name": "配置1: 端口25 + TLS",
        "server": "smtp.139.com",
        "port": 25,
        "use_ssl": False,
        "use_tls": True,
    },
    {
        "name": "配置2: 端口465 + SSL",
        "server": "smtp.139.com",
        "port": 465,
        "use_ssl": True,
        "use_tls": False,
    },
    {
        "name": "配置3: 端口587 + TLS",
        "server": "smtp.139.com",
        "port": 587,
        "use_ssl": False,
        "use_tls": True,
    },
]

username = "qsoft@139.com"
password = "574a283d502db51ea200"
recipient = "qsswgl@gmail.com"


def test_config(config):
    """测试指定配置"""
    print(f"\n{'=' * 80}")
    print(f"🔍 测试: {config['name']}")
    print(f"{'=' * 80}")
    print(f"服务器: {config['server']}")
    print(f"端口: {config['port']}")
    print(f"SSL: {config['use_ssl']}")
    print(f"TLS: {config['use_tls']}")
    print()
    
    server = None
    try:
        # 创建连接
        print(f"[1/5] 📡 连接服务器...")
        start = time.time()
        
        if config['use_ssl']:
            server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=30)
            print(f"    ✅ SSL连接成功 (耗时: {time.time()-start:.2f}秒)")
        else:
            server = smtplib.SMTP(config['server'], config['port'], timeout=30)
            print(f"    ✅ 连接成功 (耗时: {time.time()-start:.2f}秒)")
        
        # TLS加密
        if config['use_tls'] and not config['use_ssl']:
            print(f"\n[2/5] 🔒 启动TLS加密...")
            start = time.time()
            server.starttls()
            print(f"    ✅ TLS加密成功 (耗时: {time.time()-start:.2f}秒)")
        else:
            print(f"\n[2/5] ⏭️  跳过TLS (已使用SSL)")
        
        # 登录
        print(f"\n[3/5] 🔑 登录账号...")
        print(f"    用户: {username}")
        start = time.time()
        server.login(username, password)
        print(f"    ✅ 登录成功 (耗时: {time.time()-start:.2f}秒)")
        
        # 发送邮件
        print(f"\n[4/5] 📧 发送测试邮件...")
        start = time.time()
        
        msg = MIMEText("139邮箱配置测试", 'plain', 'utf-8')
        msg['From'] = Header(username, 'utf-8')
        msg['To'] = Header(recipient, 'utf-8')
        msg['Subject'] = Header(f'[测试] {config["name"]}', 'utf-8')
        
        server.send_message(msg)
        print(f"    ✅ 邮件发送成功 (耗时: {time.time()-start:.2f}秒)")
        
        print(f"\n[5/5] 🎉 完整流程成功!")
        print(f"{'=' * 80}")
        print(f"✅ 最佳配置: {config['name']}")
        print(f"{'=' * 80}")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n    ❌ 认证失败: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"\n    ❌ SMTP错误: {e}")
        return False
    except socket.timeout:
        print(f"\n    ❌ 连接超时")
        return False
    except Exception as e:
        print(f"\n    ❌ 错误: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except:
                pass


def main():
    print("=" * 80)
    print("📊 139邮箱 SMTP 配置测试")
    print("=" * 80)
    print()
    print(f"📧 发件人: {username}")
    print(f"📧 收件人: {recipient}")
    print()
    
    success_configs = []
    
    for config in configs:
        if test_config(config):
            success_configs.append(config)
            break  # 找到一个可用配置就停止
        time.sleep(2)  # 间隔2秒再测试下一个
    
    print(f"\n{'=' * 80}")
    if success_configs:
        print("✅ 找到可用配置!")
        print("=" * 80)
        for config in success_configs:
            print(f"\n📝 推荐配置:")
            print(f"   smtp_server: {config['server']}")
            print(f"   smtp_port: {config['port']}")
            print(f"   use_ssl: {config['use_ssl']}")
            print(f"   use_tls: {config['use_tls']}")
    else:
        print("❌ 所有配置都失败")
        print("=" * 80)
        print()
        print("💡 可能的原因:")
        print("   1. 139邮箱SMTP服务未开启")
        print("   2. 授权码不正确")
        print("   3. 需要先在网页版发送邮件激活")
        print("   4. 网络防火墙限制")
        print()
        print("📖 请参考: 139_EMAIL_SETUP.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
