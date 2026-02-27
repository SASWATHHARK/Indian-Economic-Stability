"""
Indian Economic Stability Dashboard – Production API (v2).
Modular FastAPI app: routes, DB, ML, sentiment, caching, scheduler.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import api_router
from app.utils.log import get_logger

logger = get_logger(__name__)


def _prewarm_forecast():
    """Background: pre-train Prophet so first /forecast request is fast."""
    if getattr(settings, "FORCE_SAMPLE_DATA", False):
        return
    try:
        from app.routes.forecast import forecaster, _data_fetcher
        if not _data_fetcher or forecaster.is_trained:
            return
        df = _data_fetcher.get_historical_dataframe("^NSEI", "3mo") or _data_fetcher.get_sample_dataframe("3mo")
        if df is not None and len(df) >= 30:
            forecaster.train_model(df)
            logger.info("Forecast model pre-warmed")
    except Exception as e:
        logger.debug("Forecast pre-warm skipped: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    import threading
    t = threading.Thread(target=_prewarm_forecast, daemon=True)
    t.start()
    if settings.SCHEDULER_ENABLED:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from app.routes.refresh import do_refresh
            from app.database import SessionLocal
            scheduler = BackgroundScheduler()
            def job():
                db = SessionLocal()
                try:
                    do_refresh(db)
                finally:
                    db.close()
            scheduler.add_job(job, "cron", hour=0, minute=30)
            scheduler.start()
            logger.info("Daily refresh scheduler started (00:30 UTC)")
        except Exception as e:
            logger.warning("Scheduler not started: %s", e)
    yield
    # shutdown
    logger.info("Shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready Economic Intelligence System – market data, forecasting, sentiment, stability score.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Economic Stability Prediction API is running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "available_endpoints": [
            "GET /market-data",
            "GET /forecast",
            "GET /model-metrics",
            "GET /sentiment",
            "GET /stability-score",
            "POST /refresh-data",
            "GET /health",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
