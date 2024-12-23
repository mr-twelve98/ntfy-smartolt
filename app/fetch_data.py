from db_manager import upsert_onu

def fetch_and_store():
    # Simulated data fetching from API
    data = [
        {'sn': '12345', 'zone': 'Zone 1', 'name': 'John Doe', 'address': '123 Street', 'odb_name': 'ODP-1'},
        {'sn': '67890', 'zone': 'Zone 2', 'name': 'Jane Doe', 'address': '456 Avenue', 'odb_name': 'ODP-2'},
    ]

    for onu in data:
        upsert_onu(onu['sn'], onu['zone'], onu['name'], onu['address'], onu['odb_name'])

if __name__ == "__main__":
    fetch_and_store()
