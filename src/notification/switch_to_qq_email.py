"""
快速切换到QQ邮箱配置

使用方法:
1. 先在QQ邮箱开通SMTP服务并获取授权码
2. 运行此脚本: python switch_to_qq_email.py
3. 按提示输入QQ邮箱和授权码
"""

def switch_to_qq_email():
    print("=" * 80)
    print("📧 切换到QQ邮箱配置")
    print("=" * 80)
    print()
    
    print("⚠️  准备工作:")
    print("   1. 登录 QQ邮箱 (https://mail.qq.com)")
    print("   2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务")
    print("   3. 开启 'POP3/SMTP服务'")
    print("   4. 生成授权码（不是QQ密码！）")
    print()
    
    input("完成以上步骤后按Enter键继续...")
    print()
    
    # 获取QQ邮箱信息
    print("=" * 80)
    print("📝 输入配置信息")
    print("=" * 80)
    print()
    
    qq_email = input("请输入QQ邮箱 (例如: 123456789@qq.com): ").strip()
    if not qq_email.endswith("@qq.com"):
        print("❌ 错误: 必须是 @qq.com 结尾的邮箱")
        return
    
    qq_auth_code = input("请输入QQ邮箱授权码 (16位字符): ").strip()
    if len(qq_auth_code) < 10:
        print("❌ 错误: 授权码长度不正确")
        return
    
    recipient = input("接收邮件的邮箱 (直接回车使用默认 qsswgl@gmail.com): ").strip()
    if not recipient:
        recipient = "qsswgl@gmail.com"
    
    print()
    print("=" * 80)
    print("✅ 配置信息确认")
    print("=" * 80)
    print(f"发件人: {qq_email}")
    print(f"授权码: {'*' * (len(qq_auth_code)-4) + qq_auth_code[-4:]}")
    print(f"收件人: {recipient}")
    print(f"SMTP服务器: smtp.qq.com:587 (TLS)")
    print()
    
    confirm = input("确认修改配置? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ 已取消")
        return
    
    # 生成新的配置文件
    config_content = f'''"""
邮件配置
"""
from pydantic import BaseModel


class EmailConfig(BaseModel):
    """邮件配置"""
    enabled: bool = True
    sender_email: str = "{qq_email}"
    sender_password: str = "{qq_auth_code}"
    recipient_email: str = "{recipient}"
    
    # QQ邮箱SMTP服务器配置
    smtp_server: str = "smtp.qq.com"
    smtp_port: int = 587
    use_tls: bool = True
    use_ssl: bool = False


# 全局配置实例
email_config = EmailConfig()
'''
    
    # 备份原配置
    import shutil
    from pathlib import Path
    
    config_file = Path(__file__).parent / "email_config.py"
    backup_file = Path(__file__).parent / "email_config_gmail_backup.py"
    
    if config_file.exists():
        shutil.copy(config_file, backup_file)
        print(f"✅ 已备份原配置到: {backup_file.name}")
    
    # 写入新配置
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ 配置已更新: {config_file}")
    print()
    
    # 测试新配置
    print("=" * 80)
    print("🧪 测试新配置")
    print("=" * 80)
    print()
    
    test = input("是否立即测试邮件发送? (yes/no): ").strip().lower()
    if test in ['yes', 'y']:
        print()
        print("正在测试...")
        print()
        
        try:
            from email_service import EmailService
            service = EmailService()
            
            success = service.send_signal_alert(
                symbol="TSLA",
                action="BUY",
                quantity=100,
                price=250.0,
                reason="配置测试",
                signal_date="2025-11-14"
            )
            
            if success:
                print()
                print("=" * 80)
                print("✅ 测试邮件发送成功!")
                print("=" * 80)
                print()
                print("💡 请检查你的邮箱:")
                print(f"   {recipient}")
                print()
            else:
                print()
                print("=" * 80)
                print("❌ 测试邮件发送失败")
                print("=" * 80)
                print()
                print("💡 可能的原因:")
                print("   1. 授权码不正确")
                print("   2. SMTP服务未开启")
                print("   3. 网络连接问题")
                print()
                print(f"💡 如需恢复Gmail配置，请运行:")
                print(f"   copy {backup_file.name} email_config.py")
                print()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✅ 配置完成!")
    print("=" * 80)
    print()
    print("📝 下一步:")
    print("   1. 如果测试成功，可以运行策略检查:")
    print("      .\\daily_strategy_check.bat")
    print()
    print("   2. 如需恢复Gmail配置:")
    print(f"      copy {backup_file.name} email_config.py")
    print()


if __name__ == "__main__":
    try:
        switch_to_qq_email()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
