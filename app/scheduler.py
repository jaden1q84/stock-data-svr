from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .db import get_db
from .fetcher import fetch_and_store

# 目标股票列表，可根据需要修改
TARGET_SYMBOLS = ['AAPL', 'MSFT', 'GOOG']

def scheduled_job():
    from .db import SessionLocal
    db = SessionLocal()
    for symbol in TARGET_SYMBOLS:
        fetch_and_store(symbol, db)
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, 'cron', hour=17, minute=0)
    scheduler.start() 