import requests
import sqlite3
import os
from datetime import datetime
import time

# Constants
SMARTOLT_STATUS_URL = 'https://terabit.smartolt.com/api/onu/get_onus_statuses?olt_id=&board=&port=&zone='
SMARTOLT_DETAILS_URL = 'https://terabit.smartolt.com/api/onu/get_all_onus_details?olt_id=&board=&port=&zone=&odb='
SMARTOLT_TOKEN = '11631016cf9d466c81b6d7b2f565eb31'
SESSION_COOKIE = 'ci_session=dku3v3vta7rlhnfe5u7ugb35bh7c63f1'
DB_PATH = 'database/onustatus.db'

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def fetch_smartolt_data(url):
    headers = {
        'X-Token': SMARTOLT_TOKEN,
        'Cookie': SESSION_COOKIE,
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statuses (
            olt_name TEXT,
            status TEXT,
            count INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS onu_details (
            olt_name TEXT,
            zone_name TEXT,
            name TEXT,
            address TEXT,
            odb_name TEXT,
            duration TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_database(data, table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if table_name == 'statuses':
        cursor.executemany(
            '''INSERT INTO statuses (olt_name, status, count, timestamp) VALUES (?, ?, ?, ?)''', data
        )
    elif table_name == 'onu_details':
        cursor.executemany(
            '''INSERT INTO onu_details (olt_name, zone_name, name, address, odb_name, duration, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)''', data
        )
    conn.commit()
    conn.close()

def calculate_duration(last_status_change):
    status_time = datetime.strptime(last_status_change, "%Y-%m-%d %H:%M:%S")
    elapsed_time = datetime.now() - status_time
    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

if __name__ == "__main__":
    print("Initializing database...")
    init_database()

    print("Fetching ONU statuses...")
    status_data = fetch_smartolt_data(SMARTOLT_STATUS_URL)
    if status_data and 'response' in status_data:
        status_counts = {'Bumiagung': {'Online': 0, 'Power fail': 0, 'LOS': 0}, 'Caplek': {'Online': 0, 'Power fail': 0, 'LOS': 0}}
        onu_sn_status = {}

        for item in status_data['response']:
            olt_name = 'Bumiagung' if item['olt_id'] == '2' else 'Caplek'
            status = item['status']
            if status in status_counts[olt_name]:
                status_counts[olt_name][status] += 1
            if status in ['LOS', 'Power Fail']:
                onu_sn_status[item['sn']] = {'status': status, 'last_status_change': item['last_status_change']}

        status_entries = [
            (olt, stat, count, datetime.now()) for olt, stats in status_counts.items() for stat, count in stats.items()
        ]
        save_to_database(status_entries, 'statuses')

    print("Waiting 30 seconds before fetching ONU details...")
    time.sleep(30)

    print("Fetching ONU details...")
    details_data = fetch_smartolt_data(SMARTOLT_DETAILS_URL)
    if details_data and 'onus' in details_data:
        detail_entries = []
        for onu in details_data['onus']:
            if onu['status'] == 'LOS' and onu['zone_name'] != 'Zone 32':
                olt_name = 'Bumiagung' if onu['olt_id'] == '2' else 'Caplek'
                if onu['sn'] in onu_sn_status:
                    last_status_change = onu_sn_status[onu['sn']]['last_status_change']
                    duration = calculate_duration(last_status_change)
                    detail_entries.append(
                        (olt_name, onu['zone_name'], onu['name'], onu.get('address', 'N/A'), onu['odb_name'], duration, datetime.now())
                    )
        save_to_database(detail_entries, 'onu_details')

    print("Data fetched and saved successfully.")
