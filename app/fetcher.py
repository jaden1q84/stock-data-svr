import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
from .db import StockDaily
import pandas as pd
import asyncio
from functools import partial

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def fetch_and_store(symbol: str, db: Session, start_date=None, end_date=None):
    logger.info(f"开始获取股票 {symbol} 的数据")
    
    # 默认抓取最近180天
    if not end_date:
        end_date = datetime.now().date() + timedelta(days=1)
    if not start_date:
        start_date = end_date - timedelta(days=180)
    
    logger.info(f"获取时间范围: {start_date} 到 {end_date}")
    
    # 使用线程池执行 yfinance 下载操作
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, partial(yf.download, symbol, start=start_date, end=end_date))
    
    if df.empty:
        logger.warning(f"未找到股票 {symbol} 的数据")
        return {"status": "error", "message": "未找到数据", "count": 0}
    
    count = 0
    skipped = 0
    for idx, row in df.iterrows():
        date = idx.date()
        # 检查是否已存在
        exists = db.query(StockDaily).filter_by(symbol=symbol, date=date).with_for_update().first()
        if exists:
            skipped += 1
            continue
            
        record = StockDaily(
            symbol=symbol,
            date=date,
            open=float(row['Open'].iloc[0]) if isinstance(row['Open'], pd.Series) else float(row['Open']),
            high=float(row['High'].iloc[0]) if isinstance(row['High'], pd.Series) else float(row['High']),
            low=float(row['Low'].iloc[0]) if isinstance(row['Low'], pd.Series) else float(row['Low']),
            close=float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close']),
            volume=float(row['Volume'].iloc[0]) if isinstance(row['Volume'], pd.Series) else float(row['Volume'])
        )
        db.add(record)
        count += 1
    
    try:
        db.commit()
        logger.info(f"成功保存 {count} 条记录，跳过 {skipped} 条已存在记录")
        return {
            "status": "success",
            "message": "数据获取并保存成功",
            "count": count,
            "skipped": skipped,
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        db.rollback()
        logger.error(f"保存数据时发生错误: {str(e)}")
        return {
            "status": "error",
            "message": f"保存数据时发生错误: {str(e)}",
            "count": 0
        } 