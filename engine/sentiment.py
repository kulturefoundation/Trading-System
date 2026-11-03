class SentimentAgent:
    def evaluate(self, funding_rate):
        if funding_rate > 0.0005:
            return "EXTREME_GREED", "Funding rate too high. Retail is over-leveraged long."
        elif funding_rate < -0.0005:
            return "EXTREME_FEAR", "Funding rate too low. Retail is over-leveraged short."
        return "NEUTRAL", "Sentiment is balanced."