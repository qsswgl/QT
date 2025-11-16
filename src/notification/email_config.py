"""
邮件推送配置
"""
import os
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class EmailAccountConfig:
    """单个邮件账户配置"""
    name: str              # 账户名称
    sender_email: str      # 发件邮箱
    sender_password: str   # 发件密码/授权码
    smtp_server: str       # SMTP服务器
    smtp_port: int         # SMTP端口
    use_ssl: bool          # 是否使用SSL
    use_tls: bool          # 是否使用TLS
    
    def __repr__(self):
        return f"EmailAccount({self.name}: {self.sender_email})"


@dataclass
class EmailConfig:
    """邮件配置 - 支持多账户故障转移"""
    
    # 收件人信息
    recipient_email: str = "qsswgl@gmail.com"  # 接收提醒的邮箱
    
    # 邮件主题前缀
    subject_prefix: str = "[TSLA策略]"
    
    # 是否启用邮件推送
    enabled: bool = True
    
    # 多个发件账户配置 (按优先级顺序)
    accounts: List[EmailAccountConfig] = None
    
    def __post_init__(self):
        """初始化多账户配置"""
        if self.accounts is None:
            self.accounts = [
                # 账户1: QQ邮箱 (13794881@qq.com)
                EmailAccountConfig(
                    name="QQ邮箱",
                    sender_email="13794881@qq.com",
                    sender_password="zkoaojnharnqcacf",
                    smtp_server="smtp.qq.com",
                    smtp_port=587,
                    use_ssl=False,
                    use_tls=True
                ),
                # 账户2: Gmail (qsswgl@gmail.com)
                EmailAccountConfig(
                    name="Gmail",
                    sender_email="qsswgl@gmail.com",
                    sender_password="rqkk tqts kqvs uyej",  # Gmail应用专用密码
                    smtp_server="smtp.gmail.com",
                    smtp_port=587,
                    use_ssl=False,
                    use_tls=True
                ),
                # 账户3: 139邮箱 (qsoft@139.com)
                EmailAccountConfig(
                    name="139邮箱",
                    sender_email="qsoft@139.com",
                    sender_password="64e0f3e5ac0a4de0a28d",
                    smtp_server="smtp.139.com",
                    smtp_port=465,
                    use_ssl=True,
                    use_tls=False
                ),
            ]
    
    @property
    def sender_email(self) -> str:
        """获取主发件邮箱 (向后兼容)"""
        return self.accounts[0].sender_email if self.accounts else ""
    
    @property
    def sender_password(self) -> str:
        """获取主发件密码 (向后兼容)"""
        return self.accounts[0].sender_password if self.accounts else ""
    
    @property
    def smtp_server(self) -> str:
        """获取主SMTP服务器 (向后兼容)"""
        return self.accounts[0].smtp_server if self.accounts else ""
    
    @property
    def smtp_port(self) -> int:
        """获取主SMTP端口 (向后兼容)"""
        return self.accounts[0].smtp_port if self.accounts else 587
    
    @property
    def use_ssl(self) -> bool:
        """获取主SSL配置 (向后兼容)"""
        return self.accounts[0].use_ssl if self.accounts else False
    
    @property
    def use_tls(self) -> bool:
        """获取主TLS配置 (向后兼容)"""
        return self.accounts[0].use_tls if self.accounts else True


# 全局配置实例
email_config = EmailConfig()
