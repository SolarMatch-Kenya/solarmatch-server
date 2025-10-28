import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_email(to_email, subject, body, html_body=None):
    """
    Send email using Gmail SMTP or fallback to console logging

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Plain text email body
        html_body (str, optional): HTML email body

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Check if Gmail SMTP is properly configured
    app_password = current_app.config.get('GMAIL_APP_PASSWORD')

    if not app_password or app_password.strip() == "":
        logging.warning(
            "Gmail SMTP not configured, using fallback email service")
        return send_email_fallback(to_email, subject, body, html_body)

    try:
        # Gmail SMTP settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = current_app.config.get(
            'GMAIL_FROM_EMAIL', 'solarmatchke@gmail.com')

        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = sender_email
        message['To'] = to_email
        message['Subject'] = subject

        # Add plain text part
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)

        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

        # Create secure connection and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, message.as_string())

        logging.info(f"Email sent successfully via SMTP to {to_email}")
        return True

    except Exception as e:
        logging.error(f"Failed to send email via SMTP to {to_email}: {e}")
        logging.info("Falling back to console logging")
        return send_email_fallback(to_email, subject, body, html_body)


def send_password_reset_email(user_email, reset_token):
    """
    Send password reset email with reset token

    Args:
        user_email (str): User's email address
        reset_token (str): Password reset token

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "SolarMatch - Password Reset Request"

    # Create reset link (you'll need to update this with your frontend URL)
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"

    plain_body = f"""
Hello,

You requested a password reset for your SolarMatch account.

Click the link below to reset your password:
{reset_link}

If you didn't request this password reset, please ignore this email.

Best regards,
SolarMatch Team
    """.strip()

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #f79436;">SolarMatch - Password Reset</h2>
            
            <p>Hello,</p>
            
            <p>You requested a password reset for your SolarMatch account.</p>
            
            <p>Click the button below to reset your password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #f79436; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_link}</p>
            
            <p>If you didn't request this password reset, please ignore this email.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #666; font-size: 14px;">
                Best regards,<br>
                SolarMatch Team
            </p>
        </div>
    </body>
    </html>
    """.strip()

    return send_email(user_email, subject, plain_body, html_body)


def send_email_fallback(to_email, subject, body, html_body=None):
    """
    Fallback email service that logs to console (for testing)

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Plain text email body
        html_body (str, optional): HTML email body

    Returns:
        bool: Always returns True for testing
    """
    print("=" * 60)
    print("📧 EMAIL NOTIFICATION (Fallback Mode)")
    print("=" * 60)
    print(f"To: {to_email}")
    print(
        f"From: {current_app.config.get('GMAIL_FROM_EMAIL', 'solarmatchke@gmail.com')}")
    print(f"Subject: {subject}")
    print("-" * 60)
    print("PLAIN TEXT BODY:")
    print(body)
    print("-" * 60)
    if html_body:
        print("HTML BODY:")
        print(html_body)
    print("=" * 60)
    print("✅ Email logged successfully (Fallback mode)")
    print("💡 To enable real email sending, set GMAIL_APP_PASSWORD environment variable")
    print("=" * 60)
    return True
