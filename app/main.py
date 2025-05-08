from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from .db import init_db, get_db, StockDaily
from .scheduler import start_scheduler

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()

@app.get("/stocks/{symbol}")
def get_stock_data(
    symbol: str,
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(StockDaily).filter(StockDaily.symbol == symbol)
    if start:
        q = q.filter(StockDaily.date >= start)
    if end:
        q = q.filter(StockDaily.date <= end)
    q = q.order_by(StockDaily.date)
    return [
        {
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
            "adj_close": r.adj_close
        }
        for r in q.all()
    ]

@app.get("/stocks/{symbol}/latest")
def get_latest_stock(symbol: str, db: Session = Depends(get_db)):
    r = db.query(StockDaily).filter(StockDaily.symbol == symbol).order_by(StockDaily.date.desc()).first()
    if not r:
        return {"error": "No data"}
    return {
        "date": r.date,
        "open": r.open,
        "high": r.high,
        "low": r.low,
        "close": r.close,
        "volume": r.volume,
        "adj_close": r.adj_close
    } 