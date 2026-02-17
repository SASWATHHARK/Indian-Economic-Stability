"""
Market data service - yfinance for NIFTY (^NSEI), SENSEX (^BSESN).
2 years historical, store OHLCV in DB.
"""
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from models import MarketData

logger = logging.getLogger(__name__)

NIFTY_TICKER = "^NSEI"
SENSEX_TICKER = "^BSESN"
PERIOD = "2y"


def fetch_and_store_market_data(db: Session) -> Dict:
    """Fetch NIFTY & SENSEX 2y data, store in DB. Return latest snapshot."""
    result = {"nifty": None, "sensex": None, "stored": 0}
    try:
        nifty_df = yf.Ticker(NIFTY_TICKER).history(period=PERIOD)
        sensex_df = yf.Ticker(SENSEX_TICKER).history(period=PERIOD)
        if nifty_df.empty or sensex_df.empty:
            logger.warning("yfinance returned empty data")
            return result

        common_idx = nifty_df.index.intersection(sensex_df.index)
        for idx in common_idx:
            d = idx.date() if hasattr(idx, "date") else pd.Timestamp(idx).date()
            n_row = nifty_df.loc[idx]
            s_row = sensex_df.loc[idx]
            vol = float(getattr(n_row, "Volume", 0) or 0) + float(getattr(s_row, "Volume", 0) or 0)
            existing = db.query(MarketData).filter(MarketData.date == d).first()
            if existing:
                existing.nifty_close = float(n_row["Close"])
                existing.nifty_open = float(n_row["Open"])
                existing.nifty_high = float(n_row["High"])
                existing.nifty_low = float(n_row["Low"])
                existing.sensex_close = float(s_row["Close"])
                existing.sensex_open = float(s_row["Open"])
                existing.sensex_high = float(s_row["High"])
                existing.sensex_low = float(s_row["Low"])
                existing.volume = vol
            else:
                row = MarketData(
                    date=d,
                    nifty_close=float(n_row["Close"]),
                    nifty_open=float(n_row["Open"]),
                    nifty_high=float(n_row["High"]),
                    nifty_low=float(n_row["Low"]),
                    sensex_close=float(s_row["Close"]),
                    sensex_open=float(s_row["Open"]),
                    sensex_high=float(s_row["High"]),
                    sensex_low=float(s_row["Low"]),
                    volume=vol,
                )
                db.add(row)
            result["stored"] = result.get("stored", 0) + 1
        db.commit()

        # Latest
        latest = db.query(MarketData).order_by(MarketData.date.desc()).first()
        if latest:
            result["nifty"] = {
                "close": latest.nifty_close,
                "open": latest.nifty_open,
                "high": latest.nifty_high,
                "low": latest.nifty_low,
            }
            result["sensex"] = {
                "close": latest.sensex_close,
                "open": latest.sensex_open,
                "high": latest.sensex_high,
                "low": latest.sensex_low,
            }
    except Exception as e:
        logger.exception("market_service fetch error: %s", e)
    return result


def get_latest_market(db: Session) -> Optional[Dict]:
    """Get latest market record from DB."""
    row = db.query(MarketData).order_by(MarketData.date.desc()).first()
    if not row:
        return None
    return {
        "nifty": {
            "close": row.nifty_close,
            "open": row.nifty_open,
            "high": row.nifty_high,
            "low": row.nifty_low,
        },
        "sensex": {
            "close": row.sensex_close,
            "open": row.sensex_open,
            "high": row.sensex_high,
            "low": row.sensex_low,
        },
        "volume": row.volume,
        "date": row.date.isoformat(),
    }


def get_historical_dataframe(db: Session, ticker: str, days: int = 730) -> pd.DataFrame:
    """Get historical close prices as DataFrame for forecast training."""
    rows = db.query(MarketData).order_by(MarketData.date.desc()).limit(days).all()
    rows = list(reversed(rows))
    if not rows:
        return pd.DataFrame()
    col = "nifty_close" if "nifty" in ticker.lower() or ticker == "^NSEI" else "sensex_close"
    data = [(r.date, getattr(r, col)) for r in rows if getattr(r, col) is not None]
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data, columns=["date", "Close"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    return df
