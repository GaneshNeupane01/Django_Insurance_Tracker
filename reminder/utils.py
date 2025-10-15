# utils.py
import requests

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(token, title, body):
    """
    Send push notification to a specific device token
    """
    print(f"Sending notification to token: {token}")
    print(f"Title: {title}")
    print(f"Body: {body}")
    
    payload = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body,
        "priority": "high",
        "channelId": "default"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(EXPO_PUSH_URL, json=payload, headers=headers)
        print(f"Notification response: {response.status_code} - {response.text}")
        return response.json()
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return {"error": str(e)}
