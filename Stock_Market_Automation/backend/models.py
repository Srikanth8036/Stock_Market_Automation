from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from sqlalchemy.sql import func
import enum
from .database import Base

class TradeType(str, enum.Enum):
    CE = "CE"  # Call Option
    PE = "PE"  # Put Option

class TradeStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # e.g., NIFTY
    strike_price = Column(Float)         # e.g., 22000
    option_type = Column(String)         # CE or PE
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Integer)
    status = Column(String, default=TradeStatus.OPEN)
    entry_time = Column(DateTime(timezone=True), server_default=func.now())
    exit_time = Column(DateTime(timezone=True), nullable=True)
    pnl = Column(Float, default=0.0)
    strategy_name = Column(String, default="VWAP_Fib")
    notes = Column(String, nullable=True)

class DailySummary(Base):
    __tablename__ = "daily_summary"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True)  # YYYY-MM-DD
    total_trades = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE")  # ACTIVE, STOPPED_MAX_LOSS, STOPPED_TARGET_HIT
