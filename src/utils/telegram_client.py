import requests

from api_keys import TELEGRAM_BOT_API_KEY, TELEGRAM_CHAT_ID
from src.configs import TELEGRAM_API_URL

def send_message_to_bot(symbol, price):
    message = f"<i><strong>ALERT</strong></i>\n\nPair: <b>{symbol}</b>\nPrice: <b>{price}</b>"
    url = f"{TELEGRAM_API_URL}{TELEGRAM_BOT_API_KEY}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "html"}
    r = requests.get(url, params=params)