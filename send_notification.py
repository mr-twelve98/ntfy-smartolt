import sqlite3
import requests
from datetime import datetime, timedelta

# Constants
DB_PATH = 'database/onustatus.db'
NTFY_TOPIC = 'https://ntfy.nomikomu.my.id/Smartolt_Notif'
IGNORED_ZONE = 'Zone 32'
LOS_THRESHOLD = 10
POWER_FAIL_THRESHOLD = 20

def query_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query for status summary
    cursor.execute('''
        SELECT olt_name, status, SUM(count) as total
        FROM statuses
        WHERE timestamp >= datetime('now', '-2 minutes')
        GROUP BY olt_name, status
    ''')
    status_summary = cursor.fetchall()

    # Query for ONU details (filtered by thresholds and ignored zone)
    cursor.execute(f'''
        SELECT olt_name, zone_name, name, address, odb_name, duration
        FROM onu_details
        WHERE timestamp >= datetime('now', '-2 minutes')
        AND zone_name != '{IGNORED_ZONE}'
    ''')
    onu_details = cursor.fetchall()

    conn.close()
    return status_summary, onu_details

def format_notification(status_summary, onu_details):
    messages = []

    # Status summary
    messages.append("🚨 **SmartOLT Status Update** 🚨")
    for olt_name, status, total in status_summary:
        messages.append(f"- **{olt_name}**: {status} = {total}")

    # Filter for thresholds
    los_count = sum(total for _, status, total in status_summary if status == 'LOS')
    power_fail_count = sum(total for _, status, total in status_summary if status == 'Power fail')

    if los_count > LOS_THRESHOLD or power_fail_count > POWER_FAIL_THRESHOLD:
        messages.append("\n🔎 **ONU Details (Threshold Exceeded)** 🔎")
        for olt_name, zone_name, name, address, odb_name, duration in onu_details:
            messages.append(
                f"- OLT: **{olt_name}** | Zone: **{zone_name}**\n"
                f"  Name: {name}\n"
                f"  Address: {address}\n"
                f"  ODB: {odb_name}\n"
                f"  Duration: {duration}"
            )

    return "\n".join(messages)

def send_notification(message):
    headers = {
        "Title": "SmartOLT Notification",
        "Priority": "high",
    }
    response = requests.post(NTFY_TOPIC, data=message.encode('utf-8'), headers=headers)

    if response.status_code == 200:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Querying database for status and ONU details...")
    status_summary, onu_details = query_database()

    print("Formatting notification...")
    notification_message = format_notification(status_summary, onu_details)

    print("Sending notification to ntfy.sh...")
    send_notification(notification_message)
