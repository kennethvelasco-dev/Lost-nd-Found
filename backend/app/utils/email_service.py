import os
from flask import current_app

def send_email(to_email, subject, html_content):
    """ 
    Logs the email to the console instead of sending via a paid service.
    This ensures a 'zero dollar' deployment strategy.
    """
    print("\n" + "="*60)
    print(f"ZERO-COST EMAIL LOG (MOCK)")
    print(f"TO: {to_email}")
    print(f"SUBJECT: {subject}")
    print("-" * 30)
    # Keeping original content for console debugging.
    try:
        clean_text = html_content.replace("<p>", "\n").replace("</p>", "").replace("<h1>", "\n## ").replace("</h1>", "\n")
        print(clean_text)
    except:
        print(html_content)
    print("="*60 + "\n")
    return True

def send_verification_email(email, token):
    """ Logs a verification link to the console. """
    # In a real app, this URL would point to your frontend
    link = f"http://localhost:5000/api/auth/verify-email?token={token}"
    subject = "Verify your Lost & Found Account"
    html_content = f"""
    <h1>Welcome to Campus Lost & Found</h1>
    <p>Please verify your email by clicking the link below:</p>
    <a href="{link}">Verify Email</a>
    <p>If you didn't create an account, you can safely ignore this email.</p>
    """
    return send_email(email, subject, html_content)

def send_password_reset_email(email, token):
    """ Logs a password reset link to the console. """
    # In a real app, this URL would point to your frontend reset page
    link = f"http://localhost:3000/reset-password?token={token}"
    subject = "Reset your Lost & Found Password"
    html_content = f"""
    <h1>Password Reset Request</h1>
    <p>You requested to reset your password. Click the link below to set a new one:</p>
    <a href="{link}">Reset Password</a>
    <p>This link will expire in 1 hour. If you didn't request this, please ignore this email.</p>
    """
    return send_email(email, subject, html_content)
