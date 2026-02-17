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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
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
