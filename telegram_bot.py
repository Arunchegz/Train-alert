import requests

BOT_TOKEN = "7669839735:AAFw6DOheN69uuTDuQ13BqFnf9YDJvnXBM0"

def send_alert(chat_id, message):

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )
