import requests
from db_manager import get_onus_with_los

def send_notifications():
    onus = get_onus_with_los()

    for onu in onus:
        message = f"""
        📡 {onu[1]} - ONU Details with LOS Status
        📍   Zone Name: {onu[1]}
        🏷️ Name: {onu[2]}
        📍   Address: {onu[3]}
        🔂 ODP Name: {onu[4]}
        ⏱  Duration in LOS: 1h 30m
        """

        headers = {
            "Title": f"{onu[1]} - ONU Alert",
            "Priority": "5",
        }

        requests.post("https://ntfy.sh/Smartolt_Notif", data=message, headers=headers)

if __name__ == "__main__":
    send_notifications()
