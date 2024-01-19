from pydantic import BaseModel
import datetime

class OHLCV(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime.datetime
