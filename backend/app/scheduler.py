
import schedule
import time
import threading
from app.metrics_fetcher import fetch_metrics
from app.database import save_metrics

def job():
    metrics = fetch_metrics()
    save_metrics(metrics)
    print("Metrics fetched and saved successfully!")

def run_scheduler():
    schedule.every(1).hour.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()