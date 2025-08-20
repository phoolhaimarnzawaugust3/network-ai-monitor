TEST_MODE =True 
#!/usr/bin/env python3
from scapy.all import sniff
import joblib
import smtplib
from email.message import EmailMessage
import netifaces
from dotenv import load_dotenv
import os

load_dotenv() # Loads variables from .env

# -----------------------------
# Configuration
# -----------------------------
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# -----------------------------
# Load trained model and encoders
# -----------------------------
print("🔹 Loading model and encoders...")
model = joblib.load("model.pkl")
encoder_proto = joblib.load("encoder_col1.pkl")
encoder_service = joblib.load("encoder_col2.pkl")
encoder_flag = joblib.load("encoder_col3.pkl")

# -----------------------------
# Email alert function
# -----------------------------
def send_alert(pkt):
    msg = EmailMessage()
    msg.set_content(f"⚠️ Suspicious packet detected:\n{pkt.summary()}")
    msg['Subject'] = "Network Alert"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print("📧 Alert sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# -----------------------------
# Feature mapping function
# -----------------------------
def map_packet_to_features(pkt):
    # Protocol
    if pkt.haslayer('TCP'):
        proto = 'tcp'
    elif pkt.haslayer('UDP'):
        proto = 'udp'
    elif pkt.haslayer('ICMP'):
        proto = 'icmp'
    else:
        proto = 'other'

    # Service
    service_map = {80:'http',21:'ftp',22:'ssh',53:'domain'}
    if pkt.haslayer('TCP') or pkt.haslayer('UDP'):
        dport = pkt.dport
        service = service_map.get(dport,'other')
    else:
        service = 'other'

    # Flag
    tcp_flags = pkt['TCP'].flags if pkt.haslayer('TCP') else 0
    flag_map = {0:'SF',1:'S0',2:'REJ'}
    flag = flag_map.get(tcp_flags,'SF')

    # Numeric features
    src_bytes = len(pkt.payload) if hasattr(pkt,'payload') else 0
    dst_bytes = 0
    others = [0]*36

    # Encode categorical features
    try:
        proto_num = encoder_proto.transform([proto])[0]
    except:
        proto_num = 0  # fallback if unseen

    try:
        service_num = encoder_service.transform([service])[0]
    except:
        service_num = 0  # fallback

    try:
        flag_num = encoder_flag.transform([flag])[0]
    except:
        flag_num = 0  # fallback

    features = [proto_num, service_num, flag_num, src_bytes, dst_bytes] + others
    return features

# -----------------------------
# Monitoring function
# -----------------------------
def monitor(pkt):
    features = map_packet_to_features(pkt)
    try:
        pred = model.predict([features])
        if TEST_MODE or pred[0] != 0:  # attack detected
            send_alert(pkt)
            print("⚠️ Attack predicted:", pkt.summary())
    except Exception as e:
        print("❌ Prediction error:", e)

# -----------------------------
# Auto-detect active interface
# -----------------------------
def get_active_interface():
    for iface in netifaces.interfaces():
        if iface == 'lo':
            continue
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            return iface
    return None

iface = get_active_interface()
if iface is None:
    print("❌ No active interface found")
    exit()
print("🔹 Using interface:", iface)

# -----------------------------
# Start packet capture
# -----------------------------
print("🔹 Starting live packet capture (CTRL+C to stop)...")
sniff(prn=monitor, iface=iface, store=False)

