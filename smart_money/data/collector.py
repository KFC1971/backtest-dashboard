from typing import Dict, Any
import pandas as pd
import yfinance as yf

from ..config import YF_HISTORY_PERIOD_DEFAULT
from .sec import SECDataAPI
from .whale import WhaleAlertAPI


class DataCollector:
    def __init__(self) -> None:
        self.sec_api = SECDataAPI()
        self.whale_api = WhaleAlertAPI()

    def collect_all_data(self, symbol: str) -> Dict[str, Any]:
        try:
            price_volume = yf.Ticker(symbol).history(period=YF_HISTORY_PERIOD_DEFAULT)
        except Exception:
            price_volume = pd.DataFrame()

        return {
            "13f_data": self.sec_api.get_13f_holdings(symbol),
            "insider_data": self.sec_api.get_insider_trading(symbol),
            "price_volume": price_volume,
            "whale_data": self.whale_api.get_large_transactions(),
        }
