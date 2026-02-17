"""
APScheduler - daily at 6 PM (18:00).
Fetch market, news, sentiment, stability; store in DB.
"""
import logging
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler

from database import SessionLocal, init_db
from services.market_service import fetch_and_store_market_data
from services.news_service import fetch_and_store_news
from services.stability_service import compute_and_store

logger = logging.getLogger(__name__)


def daily_job():
    """Run at 6 PM daily."""
    logger.info("Daily scheduler job started")
    db = SessionLocal()
    try:
        init_db()
        fetch_and_store_market_data(db)
        fetch_and_store_news(db)
        compute_and_store(db)
        logger.info("Daily job completed")
    except Exception as e:
        logger.exception("Daily job error: %s", e)
    finally:
        db.close()


def start_scheduler():
    """Start APScheduler with 6 PM daily cron."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_job, "cron", hour=18, minute=0)
    scheduler.start()
    logger.info("Scheduler started - daily at 18:00")
