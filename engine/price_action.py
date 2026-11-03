class PriceActionAgent:
    def evaluate(self, df):
        ema21 = df['close'].ewm(span=21, adjust=False).mean().iloc[-2]
        current_close = df['close'].iloc[-1]
        
        candle_range = df['high'].iloc[-1] - df['low'].iloc[-1]
        close_position = (current_close - df['low'].iloc[-1]) / candle_range if candle_range > 0 else 0
        
        is_strong_bull = close_position > 0.75
        
        if current_close > ema21 and is_strong_bull:
            return "BUY", "Price above 21 EMA + Strong Bull Bar"
        elif current_close < ema21 and close_position < 0.25:
            return "SELL", "Price below 21 EMA + Strong Bear Bar"
        
        return "WAIT", "No clear price action setup"