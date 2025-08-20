# Network AI Monitor

This project captures live network packets, classifies them using a trained ML model, and sends email alerts when suspicious traffic is detected.

## Setup

```bash
git clone https://github.com/yourname/network-ai-monitor.git
cd network-ai-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo python3 monitor.py
