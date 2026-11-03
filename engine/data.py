import requests
import pandas as pd

class DataAgent:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol

    def get_market_data(self):
        url = f"https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval=1m&limit=100"
        data = requests.get(url).json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_vol', 'trades', 'taker_base', 'taker_quote', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        
        funding_url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={self.symbol}"
        funding_data = requests.get(funding_url).json()
        funding_rate = float(funding_data['lastFundingRate'])
        
        return df, funding_rate