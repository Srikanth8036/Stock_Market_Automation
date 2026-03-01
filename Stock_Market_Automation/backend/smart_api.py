import time
import logging
import pyotp
import requests
from SmartApi import SmartConnect
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

class SmartApiClient:
    def __init__(self):
        self.obj = None
        self.session = None
        self.retry_limit = 3
        self.retry_delay = 5

    def login(self):
        """Attempts login with retries."""
        for attempt in range(1, self.retry_limit + 1):
            try:
                self.obj = SmartConnect(api_key=settings.API_KEY)
                totp = pyotp.TOTP(settings.TOTP_SECRET).now()
                self.session = self.obj.generateSession(settings.CLIENT_ID, settings.PASSWORD, totp)

                if self.session.get('status'):
                    logging.info("Login Successful!")
                    return True
                else:
                    logging.error(f"Login attempt {attempt} failed: {self.session.get('message')}")

            except Exception as e:
                logging.error(f"Login error on attempt {attempt}: {e}")

            if attempt < self.retry_limit:
                time.sleep(self.retry_delay)
        
        logging.critical("Login failed after multiple attempts.")
        return False

    def get_ltp(self, exchange, symbol, token):
        """Fetches LTP safely."""
        try:
            data = self.obj.ltpData(exchange, symbol, token)
            if "data" in data and "ltp" in data["data"]:
                return data["data"]["ltp"]
        except Exception as e:
            logging.error(f"Error fetching LTP for {symbol}: {e}")
        return None

    def get_candles(self, exchange, token, interval, from_date, to_date):
        """Fetches historical candle data."""
        payload = {
            "exchange": exchange,
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date,
            "todate": to_date
        }
        try:
            data = self.obj.getCandleData(payload)
            if data and "data" in data:
                return data["data"]
        except Exception as e:
            logging.error(f"Error fetching candles for {token}: {e}")
        return []

    def place_order(self, symbol, token, transaction_type, quantity, product_type="INTRADAY", price=0.0, variety="NORMAL", order_type="MARKET"):
        """Places an order via SmartAPI."""
        try:
            orderparams = {
                "variety": variety,
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": transaction_type,
                "exchange": "NSE",
                "ordertype": order_type,
                "producttype": product_type,
                "duration": "DAY",
                "price": price,
                "squareoff": "0",
                "stoploss": "0",
                "quantity": quantity
            }
            order_id = self.obj.placeOrder(orderparams)
            logging.info(f"Order placed for {symbol}. ID: {order_id}")
            return order_id
        except Exception as e:
            logging.error(f"Order placement failed for {symbol}: {e}")
            return None

client = SmartApiClient()
