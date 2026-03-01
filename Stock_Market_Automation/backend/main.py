from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import engine, Base, get_db
from .models import Trade, DailySummary
from .scheduler import start_scheduler, stop_scheduler
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Market Automation API")

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class TradeSchema(BaseModel):
    id: int
    symbol: str
    option_type: str
    entry_price: float
    exit_price: float | None
    pnl: float
    status: str
    entry_time: datetime
    
    class Config:
        from_attributes = True

class SummarySchema(BaseModel):
    date: str
    total_trades: int
    wins: int
    losses: int
    total_pnl: float
    
    class Config:
        from_attributes = True

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

@app.get("/")
def read_root():
    return {"status": "running", "message": "Stock Market Automation Bot is Active"}

@app.get("/trades", response_model=List[TradeSchema])
def get_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    trades = db.query(Trade).order_by(Trade.entry_time.desc()).offset(skip).limit(limit).all()
    return trades

@app.get("/summary", response_model=List[SummarySchema])
def get_summary(limit: int = 7, db: Session = Depends(get_db)):
    summaries = db.query(DailySummary).order_by(DailySummary.date.desc()).limit(limit).all()
    return summaries

@app.post("/control/start")
def start_bot():
    start_scheduler()
    return {"message": "Bot started"}

@app.post("/control/stop")
def stop_bot():
    stop_scheduler()
    return {"message": "Bot stopped"}
