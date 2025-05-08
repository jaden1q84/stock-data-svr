from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
from .db import get_db
from .fetcher import fetch_and_store

# 从配置文件读取配置
def load_config():
    config_path = os.getenv("CONFIG_PATH", "config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

def scheduled_job():
    from .db import SessionLocal
    db = SessionLocal()
    config = load_config()
    for symbol in config['target_symbols']:
        fetch_and_store(symbol, db)
    db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    config = load_config()
    scheduler.add_job(scheduled_job, 'cron', 
                     hour=config['scheduler']['hour'],
                     minute=config['scheduler']['minute'])
    scheduler.start() 