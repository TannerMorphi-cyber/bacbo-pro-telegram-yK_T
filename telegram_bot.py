import requests
import os

def send_telegram_signal(message: str):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not token or not chat_id:
        print("ERROR: BOT_TOKEN o CHAT_ID no configurados")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"Telegram enviado: {response.status_code}")
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")
