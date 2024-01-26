from pydantic import BaseModel, ConfigDict

import datetime


class OHLCV(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime.datetime


class BTC4H(OHLCV):
    model_config = ConfigDict(from_attributes=True)
