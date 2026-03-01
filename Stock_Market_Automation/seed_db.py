from backend.database import SessionLocal, engine, Base
from backend.models import Trade, DailySummary, TradeType, TradeStatus
from datetime import datetime, timedelta
import random

# Create tables
Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    
    # Clear existing data
    db.query(Trade).delete()
    db.query(DailySummary).delete()
    
    print("Seeding data...")

    # Create last 7 days of summary
    today = datetime.now().date()
    for i in range(7):
        date = today - timedelta(days=i)
        
        # Randomize stats
        wins = random.randint(1, 5)
        losses = random.randint(0, 3)
        total_trades = wins + losses
        pnl = (wins * 1500) - (losses * 500) # Avg win 1500, avg loss 500
        
        summary = DailySummary(
            date=date.strftime("%Y-%m-%d"),
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            total_pnl=float(pnl),
            max_drawdown=float(random.randint(500, 2000)),
            status="ACTIVE"
        )
        db.add(summary)

    # Create some trades for today
    symbols = ["NIFTY", "BANKNIFTY", "FINNIFTY"]
    for i in range(5):
        is_win = random.choice([True, False])
        entry_price = random.uniform(100, 500)
        pnl = random.uniform(500, 2000) if is_win else random.uniform(-500, -100)
        
        trade = Trade(
            symbol=random.choice(symbols),
            strike_price=round(random.uniform(20000, 45000), 0),
            option_type=random.choice(["CE", "PE"]),
            entry_price=round(entry_price, 2),
            exit_price=round(entry_price + (pnl/50), 2), # approx
            quantity=50,
            status=TradeStatus.CLOSED,
            entry_time=datetime.now() - timedelta(hours=random.randint(1, 5)),
            exit_time=datetime.now(),
            pnl=round(pnl, 2),
            strategy_name="VWAP_Fib"
        )
        db.add(trade)

    # Add one OPEN trade
    open_trade = Trade(
        symbol="NIFTY",
        strike_price=22500,
        option_type="CE",
        entry_price=150.0,
        quantity=50,
        status=TradeStatus.OPEN,
        entry_time=datetime.now(),
        pnl=0.0,
        strategy_name="VWAP_Fib"
    )
    db.add(open_trade)

    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
