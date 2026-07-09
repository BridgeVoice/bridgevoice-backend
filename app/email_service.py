import os
import smtplib
from email.message import EmailMessage


def send_welcome_email(to_email: str, full_name: str) -> bool:
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    email_port = int(os.getenv("EMAIL_PORT", "587"))

    if not email_username or not email_password:
        print("Email service not configured. Skipping welcome email.")
        return False

    message = EmailMessage()
    message["Subject"] = "Welcome to BridgeVoice!"
    message["From"] = email_username
    message["To"] = to_email

    plain_text = f"""
Hi {full_name},

Welcome to BridgeVoice!

Your account has been created successfully.
You can now start practicing English conversations, building confidence, and tracking your progress.

Thank you for joining BridgeVoice.

Best,
BridgeVoice Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
  <body style="margin:0; padding:0; background-color:#f4f4f7; font-family:Arial, sans-serif;">
    <div style="max-width:600px; margin:30px auto; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e5e7eb;">
      
      <div style="background:linear-gradient(90deg,#7c3aed,#2563eb); padding:28px; text-align:center;">
        <h1 style="color:#ffffff; margin:0; font-size:28px;">BridgeVoice</h1>
        <p style="color:#e0e7ff; margin:8px 0 0; font-size:15px;">Build English confidence through practice</p>
      </div>

      <div style="padding:32px;">
        <h2 style="color:#111827; margin-top:0;">Welcome, {full_name}! 🎉</h2>

        <p style="color:#374151; font-size:16px; line-height:1.6;">
          Your BridgeVoice account has been created successfully.
        </p>

        <p style="color:#374151; font-size:16px; line-height:1.6;">
          You can now start practicing English conversations, building confidence,
          and tracking your progress with personalized learning support.
        </p>

        <div style="background:#f5f3ff; border-left:4px solid #7c3aed; padding:16px; margin:24px 0; border-radius:8px;">
          <p style="margin:0; color:#4c1d95; font-size:15px;">
            Start with onboarding so BridgeVoice can personalize your learning journey.
          </p>
        </div>

        <p style="color:#374151; font-size:16px; line-height:1.6;">
          Thank you for joining BridgeVoice.
        </p>

        <p style="color:#111827; font-size:16px; margin-bottom:0;">
          Best,<br/>
          <strong>BridgeVoice Team</strong>
        </p>
      </div>

      <div style="background:#f9fafb; padding:18px; text-align:center; color:#6b7280; font-size:12px;">
        © 2026 BridgeVoice. This is an automated welcome email.
      </div>
    </div>
  </body>
</html>
"""

    message.set_content(plain_text)
    message.add_alternative(html_content, subtype="html")

    try:
        if email_port == 465:
            # Implicit SSL (encrypted from the first byte)
            with smtplib.SMTP_SSL(email_host, email_port, timeout=15) as server:
                server.login(email_username, email_password)
                server.send_message(message)
        else:
            # STARTTLS (start plain, upgrade to encrypted) — e.g. port 587
            with smtplib.SMTP(email_host, email_port, timeout=15) as server:
                server.starttls()
                server.login(email_username, email_password)
                server.send_message(message)

        return True

    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False
    
    # try:
    #    with smtplib.SMTP(email_host, email_port) as server:
    #        server.starttls()
    #        server.login(email_username, email_password)
    #        server.send_message(message)

    #    return True

    # except Exception as e:
    #    print(f"Failed to send welcome email: {e}")
    #    return False