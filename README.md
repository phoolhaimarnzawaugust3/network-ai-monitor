# Network AI Monitor

This project captures live network packets, classifies them using a trained ML model, and sends email alerts when suspicious traffic is detected.

## Setup

```bash
git clone https://github.com/yourname/network-ai-monitor.git
cd network-ai-monitor


##After this, you need to update .env.environment with your email address and application password.
##You need 2-Step Verification of your email-address on to get application password.

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo python3 monitor.py


