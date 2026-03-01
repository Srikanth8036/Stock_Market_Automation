import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # SmartAPI Credentials
    API_KEY: str = os.getenv("SMART_API_KEY", "")
    CLIENT_ID: str = os.getenv("SMART_CLIENT_ID", "")
    PASSWORD: str = os.getenv("SMART_PASSWORD", "")
    TOTP_SECRET: str = os.getenv("SMART_TOTP_SECRET", "")

    # Telegram Credentials
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Database
    DATABASE_URL: str = "sqlite:///./trading.db"

    # Risk Management
    MAX_DAILY_LOSS: float = 2000.0  # Stop trading if loss exceeds this
    MAX_TRADES_PER_DAY: int = 5     # Avoid overtrading
    RISK_PER_TRADE: float = 500.0   # Max risk per trade

    class Config:
        env_file = ".env"

settings = Settings()
