"""Send a one-off test email via the configured EmailManager.

Used by the daily-summary workflow's `test_email` dispatch input to verify
SMTP credentials and delivery without running the full pipeline.
"""

from src.services.email import EmailManager
from src.storage.manager import StorageManager


def main() -> None:
    config = StorageManager().load_config()
    if not config.email or not config.email.enabled:
        raise SystemExit("email.enabled is false in data/config.json")

    manager = EmailManager(config.email)
    recipients = config.email.recipients
    if not recipients:
        raise SystemExit("email.recipients is empty in data/config.json")

    body = (
        "# Personal Horizon 邮件测试\n\n"
        "这是一封测试邮件，用于验证 SMTP 配置。\n\n"
        "- SMTP 服务器: smtp.qq.com (465, SSL)\n"
        "- 如果你收到这封邮件，说明每日简报投递已就绪。\n"
    )
    manager.send_daily_summary(body, "Personal Horizon 邮件投递测试", recipients)
    print(f"Test email dispatched to {len(recipients)} recipient(s).")


if __name__ == "__main__":
    main()
