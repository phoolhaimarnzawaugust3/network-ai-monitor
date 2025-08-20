import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
import numpy as np

load_dotenv()

def send_email_alert(subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not (sender and password and receiver):
        print("⚠️ Email not configured in .env")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print("📧 Email alert sent")
    except Exception as e:
        print("❌ Failed to send email:", e)


def preprocess_packet(packet):
    """Extract very simple features for demo purposes."""
    try:
        length = len(packet)
        src = packet[0][1].src
        dst = packet[0][1].dst
        sport = packet[0][2].sport if hasattr(packet[0][2], "sport") else 0
        dport = packet[0][2].dport if hasattr(packet[0][2], "dport") else 0
    except Exception:
        length, src, dst, sport, dport = 0, "0", "0", 0, 0

    # Features: length, sport, dport
    return np.array([length, sport, dport]).reshape(1, -1)
