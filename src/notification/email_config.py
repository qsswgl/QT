"""
邮件推送配置
"""
import os
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """邮件配置"""
    
    # 发件人信息
    sender_email: str = "qsswgl@gmail.com"
    sender_password: str = "clhbzzxtafvinvni"  # Gmail应用专用密码(16位,已去掉空格)
    
    # 收件人信息
    recipient_email: str = "qsswgl@gmail.com"  # 接收提醒的邮箱
    
    # SMTP服务器配置
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587  # Gmail标准TLS端口
    use_ssl: bool = False  # 不使用SSL
    use_tls: bool = True   # 使用TLS(Gmail要求)
    
    # 邮件主题前缀
    subject_prefix: str = "[TSLA策略]"
    
    # 是否启用邮件推送
    enabled: bool = True


# 全局配置实例
email_config = EmailConfig()
