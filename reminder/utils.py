# utils.py
import requests

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(token, title, body):
    payload = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body
    }
    response = requests.post(EXPO_PUSH_URL, json=payload)
    return response.json()
