import sqlite3
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ONU_Details (
        sn TEXT PRIMARY KEY,
        zone TEXT,
        name TEXT,
        address TEXT,
        odb_name TEXT,
        updated_at DATETIME
    )
    ''')

    conn.commit()
    conn.close()

def upsert_onu(sn, zone, name, address, odb_name):
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO ONU_Details (sn, zone, name, address, odb_name, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(sn) DO UPDATE SET
        zone=excluded.zone,
        name=excluded.name,
        address=excluded.address,
        odb_name=excluded.odb_name,
        updated_at=excluded.updated_at
    ''', (sn, zone, name, address, odb_name, datetime.now()))

    conn.commit()
    conn.close()

def get_onus_with_los():
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM ONU_Details')
    data = cursor.fetchall()

    conn.close()
    return data
