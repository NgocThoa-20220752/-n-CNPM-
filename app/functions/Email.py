import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from app.core.config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class EmailService:
    """Service quản lý gửi email"""

    def __init__(self):
        self.smtp_server = config.MAIL_SERVER
        self.smtp_port = config.MAIL_PORT
        self.username = config.MAIL_USERNAME
        self.password = config.MAIL_PASSWORD
        self.default_sender = config.MAIL_DEFAULT_SENDER
        self.use_tls = config.MAIL_USE_TLS
        self.use_ssl = config.MAIL_USE_SSL

        # Thiết lập Jinja2 template engine cho email templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'email')
        if os.path.exists(template_dir):
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            self.jinja_env = None
            logger.warning(f"Email template directory not found: {template_dir}")

    def _create_connection(self):
        """Tạo kết nối SMTP"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            if self.username and self.password:
                server.login(self.username, self.password)

            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {str(e)}")
            raise

    def send_email(
            self,
            to_email: str | List[str],
            subject: str,
            body: str,
            html_body: Optional[str] = None,
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None,
            attachments: Optional[List[str]] = None,
            sender: Optional[str] = None
    ) -> bool:
        """
        Gửi email

        Args:
            to_email: Email người nhận (hoặc list emails)
            subject: Tiêu đề email
            body: Nội dung text plain
            html_body: Nội dung HTML (optional)
            cc: Danh sách CC (optional)
            bcc: Danh sách BCC (optional)
            attachments: Danh sách file đính kèm (optional)
            sender: Email người gửi (optional, default từ config)

        Returns:
            True nếu gửi thành công, False nếu thất bại
        """
        try:
            # Chuẩn bị message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender or self.default_sender

            # Xử lý recipients
            if isinstance(to_email, str):
                to_email = [to_email]
            msg['To'] = ', '.join(to_email)

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Attach text và HTML body
            msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Attach files nếu có
            if attachments:
                for file_path in attachments:
                    self._attach_file(msg, file_path)

            # Kết nối và gửi email
            with self._create_connection() as server:
                recipients = to_email + (cc or []) + (bcc or [])
                server.sendmail(sender or self.default_sender, recipients, msg.as_string())

            logger.info(f"Email sent successfully to {', '.join(to_email)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def _attach_file( msg: MIMEMultipart, file_path: str):
        """Đính kèm file vào email"""
        try:
            with open(file_path, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {str(e)}")

    def send_verification_email(
            self,
            to_email: str,
            verification_code: str,
            user_name: Optional[str] = None
    ) -> bool:
        """
        Gửi email xác thực tài khoản

        Args:
            to_email: Email người nhận
            verification_code: Mã xác thực
            user_name: Tên người dùng (optional)

        Returns:
            True nếu gửi thành công
        """
        subject = "Xác thực tài khoản của bạn"

        # Tạo nội dung HTML từ template hoặc hardcode
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template('verification.html')
                html_body = template.render(
                    user_name=user_name or "Người dùng",
                    verification_code=verification_code,
                    expires_in=config.EMAIL_VERIFICATION_CODE_EXPIRES // 60
                )
            except Exception as e:
                logger.error(f"Failed to load email template: {str(e)}")
                html_body = self._get_default_verification_html(verification_code, user_name)
        else:
            html_body = self._get_default_verification_html(verification_code, user_name)

        # Text plain version
        body = f"""
        Xin chào {user_name or "bạn"},

        Mã xác thực của bạn là: {verification_code}

        Mã này sẽ hết hạn sau {config.EMAIL_VERIFICATION_CODE_EXPIRES // 60} phút.

        Nếu bạn không yêu cầu xác thực này, vui lòng bỏ qua email này.

        Trân trọng,
        Đội ngũ hỗ trợ
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )

    @staticmethod
    def _get_default_verification_html(
            verification_code: str,
            user_name: Optional[str] = None
    ) -> str:
        """Tạo HTML mặc định cho email xác thực"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .code-box {{ 
                    background: #f4f4f4; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 32px; 
                    font-weight: bold; 
                    letter-spacing: 5px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Xác thực tài khoản</h2>
                <p>Xin chào {user_name or "bạn"},</p>
                <p>Mã xác thực của bạn là:</p>
                <div class="code-box">{verification_code}</div>
                <p>Mã này sẽ hết hạn sau {config.EMAIL_VERIFICATION_CODE_EXPIRES // 60} phút.</p>
                <p>Nếu bạn không yêu cầu xác thực này, vui lòng bỏ qua email này.</p>
                <div class="footer">
                    <p>Trân trọng,<br>Đội ngũ hỗ trợ</p>
                </div>
            </div>
        </body>
        </html>
        """

    def send_password_reset_email(
            self,
            to_email: str,
            reset_token: str,
            user_name: Optional[str] = None
    ) -> bool:
        """
        Gửi email đặt lại mật khẩu

        Args:
            to_email: Email người nhận
            reset_token: Token reset password
            user_name: Tên người dùng (optional)

        Returns:
            True nếu gửi thành công
        """
        subject = "Đặt lại mật khẩu"

        # Tạo link reset (giả sử có frontend URL)
        reset_link = f"https://yourapp.com/reset-password?token={reset_token}"

        body = f"""
        Xin chào {user_name or "bạn"},

        Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.

        Vui lòng click vào link sau để đặt lại mật khẩu:
        {reset_link}

        Link này sẽ hết hạn sau 1 giờ.

        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

        Trân trọng,
        Đội ngũ hỗ trợ
        """

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{ 
                    display: inline-block;
                    padding: 12px 30px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Đặt lại mật khẩu</h2>
                <p>Xin chào {user_name or "bạn"},</p>
                <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                <p>Vui lòng click vào nút bên dưới để đặt lại mật khẩu:</p>
                <a href="{reset_link}" class="button">Đặt lại mật khẩu</a>
                <p>Hoặc copy link sau vào trình duyệt:</p>
                <p style="word-break: break-all;">{reset_link}</p>
                <p>Link này sẽ hết hạn sau 1 giờ.</p>
                <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.</p>
                <div class="footer">
                    <p>Trân trọng,<br>Đội ngũ hỗ trợ</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )

    def send_welcome_email(
            self,
            to_email: str,
            user_name: str
    ) -> bool:
        """
        Gửi email chào mừng người dùng mới

        Args:
            to_email: Email người nhận
            user_name: Tên người dùng

        Returns:
            True nếu gửi thành công
        """
        subject = "Chào mừng bạn đến với hệ thống"

        body = f"""
        Xin chào {user_name},

        Chào mừng bạn đã đăng ký tài khoản thành công!

        Bạn có thể bắt đầu sử dụng các tính năng của chúng tôi ngay bây giờ.

        Nếu bạn có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với chúng tôi.

        Trân trọng,
        Đội ngũ hỗ trợ
        """

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .welcome-box {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="welcome-box">
                    <h1>🎉 Chào mừng!</h1>
                    <h2>{user_name}</h2>
                </div>
                <p>Chúc mừng bạn đã đăng ký tài khoản thành công!</p>
                <p>Bạn có thể bắt đầu sử dụng các tính năng của chúng tôi ngay bây giờ.</p>
                <p>Nếu bạn có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với chúng tôi.</p>
                <div class="footer">
                    <p>Trân trọng,<br>Đội ngũ hỗ trợ</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body
        )


# Singleton instance
email_service = EmailService()