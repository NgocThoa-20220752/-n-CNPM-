"""
Email HTML templates
"""


def get_verification_email_template(user_name: str, verification_code: str, expires_in: int) -> str:
    """Template email xác thực"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .code-box {{
                background: #f8f9fa;
                border: 2px dashed #667eea;
                padding: 20px;
                text-align: center;
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
                margin: 30px 0;
                border-radius: 8px;
                color: #667eea;
            }}
            .info-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Xác Thực Tài Khoản</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Cảm ơn bạn đã đăng ký! Để hoàn tất quá trình đăng ký, vui lòng sử dụng mã xác thực bên dưới:</p>

                <div class="code-box">
                    {verification_code}
                </div>

                <div class="info-box">
                    <strong>⏰ Lưu ý:</strong> Mã xác thực này sẽ hết hạn sau <strong>{expires_in} phút</strong>.
                </div>

                <p>Nếu bạn không yêu cầu xác thực này, vui lòng bỏ qua email này.</p>
            </div>
            <div class="footer">
                <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                <p>&copy; 2024 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_password_reset_email_template(user_name: str, reset_link: str) -> str:
    """Template email đặt lại mật khẩu"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 40px;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                text-decoration: none;
                border-radius: 50px;
                margin: 20px 0;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
            }}
            .warning-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            .link-box {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                word-break: break-all;
                margin: 15px 0;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 Đặt Lại Mật Khẩu</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                <p>Nhấn vào nút bên dưới để tạo mật khẩu mới:</p>

                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Đặt Lại Mật Khẩu</a>
                </div>

                <p>Hoặc copy đường link sau vào trình duyệt:</p>
                <div class="link-box">
                    {reset_link}
                </div>

                <div class="warning-box">
                    <strong>⚠️ Bảo mật:</strong> Link này sẽ hết hạn sau <strong>1 giờ</strong>. 
                    Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                </div>
            </div>
            <div class="footer">
                <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                <p>&copy; 2024 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_welcome_email_template(user_name: str) -> str:
    """Template email chào mừng"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 50px 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 36px;
            }}
            .emoji {{
                font-size: 60px;
                margin: 20px 0;
            }}
            .content {{
                padding: 30px;
            }}
            .feature-box {{
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="emoji">🎉</div>
                <h1>Chào Mừng!</h1>
                <h2 style="margin: 10px 0; font-weight: normal;">{user_name}</h2>
            </div>
            <div class="content">
                <p>Chúc mừng bạn đã đăng ký tài khoản thành công!</p>
                <p>Chúng tôi rất vui được chào đón bạn tham gia cộng đồng của chúng tôi.</p>

                <h3>🚀 Bắt đầu ngay:</h3>

                <div class="feature-box">
                    <strong>✓ Hoàn thiện hồ sơ</strong><br>
                    Cập nhật thông tin cá nhân để trải nghiệm tốt hơn
                </div>

                <div class="feature-box">
                    <strong>✓ Khám phá tính năng</strong><br>
                    Tìm hiểu các tính năng hữu ích của hệ thống
                </div>

                <div class="feature-box">
                    <strong>✓ Liên hệ hỗ trợ</strong><br>
                    Đội ngũ của chúng tôi luôn sẵn sàng hỗ trợ bạn
                </div>

                <p>Nếu bạn có bất kỳ câu hỏi nào, đừng ngần ngại liên hệ với chúng tôi!</p>
            </div>
            <div class="footer">
                <p>Trân trọng,<br><strong>Đội ngũ hỗ trợ</strong></p>
                <p>&copy; 2024 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def get_otp_email_template(user_name: str, otp_code: str, purpose: str, expires_in: int) -> str:
    """Template email OTP"""
    purpose_text = {
        'login': 'đăng nhập',
        'transaction': 'xác thực giao dịch',
        'password_reset': 'đặt lại mật khẩu',
        'registration': 'đăng ký tài khoản'
    }

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .otp-box {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                font-size: 40px;
                font-weight: bold;
                letter-spacing: 10px;
                margin: 30px 0;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }}
            .warning-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Mã OTP</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Đây là mã OTP để {purpose_text.get(purpose, 'xác thực')} của bạn:</p>

                <div class="otp-box">
                    {otp_code}
                </div>

                <div class="warning-box">
                    <strong>⏰ Quan trọng:</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>Mã OTP có hiệu lực trong <strong>{expires_in} phút</strong></li>
                        <li>Không chia sẻ mã này với bất kỳ ai</li>
                        <li>Nếu không phải bạn yêu cầu, vui lòng bỏ qua email này</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                <p>&copy; 2024 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """