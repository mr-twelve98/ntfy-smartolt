import time
import subprocess

def run_fetch():
    subprocess.run(["python", "fetch_data.py"])

def run_notify():
    subprocess.run(["python", "send_notification.py"])

if __name__ == "__main__":
    while True:
        run_fetch()
        time.sleep(600)  # Fetch every 10 minutes
        run_notify()
        time.sleep(3600 - 600)  # Notify every hour
