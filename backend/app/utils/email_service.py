import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def send_email(to_email, subject, html_content):
    """ 
    Sends an email using the built-in smtplib.
    Falls back to console logging if SMTP settings are missing or if it fails.
    """
    smtp_server = current_app.config.get("SMTP_SERVER")
    smtp_port = current_app.config.get("SMTP_PORT", 587)
    smtp_username = current_app.config.get("SMTP_USERNAME")
    smtp_password = current_app.config.get("SMTP_PASSWORD")
    smtp_use_tls = current_app.config.get("SMTP_USE_TLS", True)
    from_email = current_app.config.get("SMTP_FROM_EMAIL", "onboarding@yourdomain.com")

    if not smtp_server or not smtp_username or not smtp_password:
        logger.warning("SMTP credentials not fully configured. Falling back to console logging.")
        _mock_send(to_email, subject, html_content)
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if smtp_use_tls:
                server.starttls()
                
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        logger.info(f"Email sent successfully to {to_email}.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email} via SMTP: {str(e)}")
        # Fallback to local console so it acts as an email mockup instead of crashing
        _mock_send(to_email, subject, html_content)
        return True

def _mock_send(to_email, subject, html_content):
    """Mock sending an email by printing to the console."""
    print("\n" + "="*60)
    print(f"ZERO-COST EMAIL LOG (MOCK)")
    print(f"TO: {to_email}")
    print(f"SUBJECT: {subject}")
    print("-" * 30)
    try:
        clean_text = html_content.replace("<p>", "\n").replace("</p>", "").replace("<h1>", "\n## ").replace("</h1>", "\n")
        print(clean_text)
    except:
        print(html_content)
    print("="*60 + "\n")

def send_verification_email(email, token):
    """ Sends a verification link via email. """
    # In production, BASE_URL should come from config
    base_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
    link = f"{base_url}/verify-email?token={token}"
    subject = "Verify your Lost & Found Account"
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto;">
        <h1 style="color: #4f46e5;">Welcome to Campus Lost & Found</h1>
        <p>Thank you for signing up! Please verify your email by clicking the button below:</p>
        <div style="margin: 30px 0;">
            <a href="{link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Verify Email Address</a>
        </div>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="color: #6b7280; font-size: 14px;">{link}</p>
        <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 30px 0;" />
        <p style="font-size: 12px; color: #9ca3af;">If you didn't create an account, you can safely ignore this email.</p>
    </div>
    """
    return send_email(email, subject, html_content)

def send_password_reset_email(email, token):
    """ Sends a password reset link via email. """
    base_url = current_app.config.get("FRONTEND_URL", "http://localhost:3000")
    link = f"{base_url}/reset-password?token={token}"
    subject = "Reset your Lost & Found Password"
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto;">
        <h1 style="color: #4f46e5;">Password Reset Request</h1>
        <p>You requested to reset your password. Click the button below to set a new one:</p>
        <div style="margin: 30px 0;">
            <a href="{link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Reset Password</a>
        </div>
        <p>This link will expire in 1 hour. If you didn't request this, please ignore this email.</p>
        <p style="color: #6b7280; font-size: 14px;">{link}</p>
    </div>
    """
    return send_email(email, subject, html_content)
