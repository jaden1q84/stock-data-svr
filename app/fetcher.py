import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .db import StockDaily

def fetch_and_store(symbol: str, db: Session, start_date=None, end_date=None):
    # 默认抓取最近30天
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    df = yf.download(symbol, start=start_date, end=end_date)
    if df.empty:
        return 0
    count = 0
    for idx, row in df.iterrows():
        date = idx.date()
        # 检查是否已存在
        exists = db.query(StockDaily).filter_by(symbol=symbol, date=date).first()
        if exists:
            continue
        record = StockDaily(
            symbol=symbol,
            date=date,
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            volume=row['Volume'],
            adj_close=row.get('Adj Close', row['Close'])
        )
        db.add(record)
        count += 1
    db.commit()
    return count 