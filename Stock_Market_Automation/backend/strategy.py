import logging
import requests
from datetime import datetime
import pytz
from .smart_api import client
from .indicators import calculate_heikin_ashi, calculate_vwap, calculate_fib_levels
from .models import Trade, DailySummary, TradeType, TradeStatus
from .database import SessionLocal
from .config import settings

# Setup logging
logger = logging.getLogger(__name__)

def send_telegram_alert(message):
    """Sends alert to Telegram."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not set. Skipping alert.")
        return
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

class TradingStrategy:
    def __init__(self):
        self.db = SessionLocal()
        self.index_tokens = {
            "NIFTY": "99926000",
            "BANKNIFTY": "99926009",
            "FINNIFTY": "99926037"
        }

    def check_market_hours(self):
        now = datetime.now(pytz.timezone("Asia/Kolkata"))
        # Market opens at 9:15 AM and closes at 3:30 PM
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return market_start <= now <= market_end

    def check_risk_management(self):
        """Checks if trading should continue based on daily PnL."""
        today = datetime.now().strftime("%Y-%m-%d")
        summary = self.db.query(DailySummary).filter(DailySummary.date == today).first()
        
        if summary:
            if summary.status == "STOPPED_MAX_LOSS":
                logger.warning("Trading stopped due to max daily loss.")
                return False
            if summary.losses * settings.RISK_PER_TRADE >= settings.MAX_DAILY_LOSS:
                summary.status = "STOPPED_MAX_LOSS"
                self.db.commit()
                return False
        return True

    def analyze_market(self):
        """Main analysis loop."""
        if not self.check_market_hours():
            logger.info("Market is closed.")
            return

        if not self.check_risk_management():
            return

        if not client.session:
            if not client.login():
                return

        for index_name, token in self.index_tokens.items():
            self.process_index(index_name, token)

    def process_index(self, index_name, token):
        # Fetch Data
        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        from_date = now.replace(hour=9, minute=15).strftime("%Y-%m-%d %H:%M")
        to_date = now.strftime("%Y-%m-%d %H:%M")

        raw_candles = client.get_candles("NSE", token, "FIVE_MINUTE", from_date, to_date)
        if not raw_candles:
            return

        ha_candles = calculate_heikin_ashi(raw_candles)
        if not ha_candles:
            return

        # Calculate Indicators
        day_high = max([c[2] for c in ha_candles])
        day_low = min([c[3] for c in ha_candles])
        vwap = calculate_vwap(ha_candles)
        fib = calculate_fib_levels(day_high, day_low)
        current_price = client.get_ltp("NSE", index_name, token)
        
        if not current_price or not vwap:
            return

        # Signal Logic (Simplified Professional Logic)
        # 1. Price near Fib 0.382 or 0.618 (Golden Zone)
        # 2. Volume Confirmation
        # 3. VWAP Trend
        
        # Determine Trend
        trend = "BULLISH" if current_price > vwap else "BEARISH"
        
        # Check for existing open trades
        open_trade = self.db.query(Trade).filter(
            Trade.symbol == index_name, 
            Trade.status == TradeStatus.OPEN
        ).first()

        if open_trade:
            self.manage_trade(open_trade, current_price, token)
        else:
            self.find_entry(index_name, token, current_price, vwap, fib, trend)

    def find_entry(self, symbol, token, price, vwap, fib, trend):
        """Identifies entry points."""
        # Simple Logic for demonstration:
        # Buy CE if Price > VWAP and bounces off Fib 0.382
        # Buy PE if Price < VWAP and rejects off Fib 0.618
        
        signal = None
        if trend == "BULLISH":
            if abs(price - fib['fib382']) < 20: # Tolerance
                signal = TradeType.CE
        elif trend == "BEARISH":
            if abs(price - fib['fib618']) < 20:
                signal = TradeType.PE
        
        if signal:
            self.execute_trade(symbol, token, signal, price)

    def execute_trade(self, symbol, token, trade_type, price):
        """Executes a trade and logs to DB."""
        logger.info(f"Executing {trade_type} trade for {symbol} at {price}")
        
        # Place Real Order
        # Example: Buying Options (simplified, usually you'd buy an Option Contract, not the Index directly)
        # For Index Options, we need to find the ATM Strike and buy that.
        # This code assumes we are trading the Index itself (Cash) or Futures for simplicity in this demo.
        # But for Options, we need to calculate the Strike.
        
        # For simplicity, let's just place a mock order call here, 
        # but in a real scenario, you'd calculate the option symbol (e.g. NIFTY24FEB22000CE)
        # and get its token.
        
        # REAL API CALL (Commented out safety check, enable if ready)
        # order_id = client.place_order(symbol, token, "BUY", 1) 
        
        # Since we don't have option chain logic here, we'll simulate the execution but add the Real API call structure.
        
        new_trade = Trade(
            symbol=symbol,
            strike_price=price, # Simplified
            option_type=trade_type,
            entry_price=price,
            quantity=50, # 1 Lot
            status=TradeStatus.OPEN
        )
        self.db.add(new_trade)
        self.db.commit()
        
        send_telegram_alert(f"🚀 ENTERED {trade_type} on {symbol} at {price}")

    def manage_trade(self, trade, current_price, token):
        """Manages open trades (Stop Loss / Target)."""
        # Simple 20 point SL and 40 point Target
        sl = 20
        target = 40
        
        pnl = 0
        if trade.option_type == TradeType.CE:
            pnl = (current_price - trade.entry_price) * trade.quantity
        else:
            pnl = (trade.entry_price - current_price) * trade.quantity
            
        # Check Exit
        exit_trade = False
        exit_reason = ""
        
        if pnl <= -sl * trade.quantity:
            exit_trade = True # Hit SL
            exit_reason = "Stop Loss Hit"
        elif pnl >= target * trade.quantity:
            exit_trade = True # Hit Target
            exit_reason = "Target Hit"
            
        if exit_trade:
            # REAL API CALL to Close Position
            # client.place_order(trade.symbol, token, "SELL", trade.quantity)
            
            trade.exit_price = current_price
            trade.exit_time = datetime.now()
            trade.status = TradeStatus.CLOSED
            trade.pnl = pnl
            self.db.commit()
            
            logger.info(f"Closed trade for {trade.symbol}. PnL: {pnl}")
            send_telegram_alert(f"🛑 CLOSED {trade.symbol} ({exit_reason}). PnL: {pnl}")

strategy = TradingStrategy()
