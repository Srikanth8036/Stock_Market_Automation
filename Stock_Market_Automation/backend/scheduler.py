from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .strategy import strategy
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        # Schedule the market analysis every 1 minute
        # Only during market hours (Mon-Fri, 9:15 - 15:30)
        trigger = CronTrigger(
            day_of_week='mon-fri',
            hour='9-15',
            minute='*',
            second='0',
            timezone='Asia/Kolkata'
        )
        
        scheduler.add_job(
            strategy.analyze_market,
            trigger=trigger,
            id='market_analysis_job',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started. Market analysis will run every minute during market hours.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
