from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import os
import asyncio
import logging
from .db import get_db
from .fetcher import fetch_and_store

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从配置文件读取配置
def load_config():
    try:
        config_path = os.getenv("CONFIG_PATH", "config.json")
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"配置文件格式错误: {config_path}")
        raise
    except Exception as e:
        logger.error(f"加载配置文件时发生错误: {str(e)}")
        raise

async def scheduled_job():
    db = None
    try:
        from .db import SessionLocal
        db = SessionLocal()
        config = load_config()
        
        # 获取并发配置，默认为4
        max_concurrent = config.get('max_concurrent', 4)
        
        # 创建信号量来控制并发
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(symbol):
            try:
                async with semaphore:
                    return await fetch_and_store(symbol, db)
            except Exception as e:
                logger.error(f"处理股票 {symbol} 时发生错误: {str(e)}")
                return None
        
        # 创建所有任务
        tasks = [fetch_with_semaphore(symbol) for symbol in config['target_symbols']]
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉失败的任务
        successful_results = [r for r in results if r is not None]
        failed_count = len(results) - len(successful_results)
        
        if failed_count > 0:
            logger.warning(f"有 {failed_count} 个任务执行失败")
        
        return successful_results
        
    except Exception as e:
        logger.error(f"调度任务执行时发生错误: {str(e)}")
        raise
    finally:
        if db:
            db.close()

def start_scheduler():
    try:
        scheduler = BackgroundScheduler()
        config = load_config()
        
        if 'scheduler' not in config or 'hour' not in config['scheduler'] or 'minute' not in config['scheduler']:
            raise ValueError("配置文件中缺少调度器配置")
            
        scheduler.add_job(lambda: asyncio.run(scheduled_job()), 'cron', 
                         hour=config['scheduler']['hour'],
                         minute=config['scheduler']['minute'])
        scheduler.start()
        logger.info("调度器已成功启动")
    except Exception as e:
        logger.error(f"启动调度器时发生错误: {str(e)}")
        raise 