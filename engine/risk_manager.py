class RiskManager:
    def veto_trade(self, pa_signal, sentiment_signal):
        if pa_signal == "BUY" and sentiment_signal == "EXTREME_GREED":
            return True, "VETO: Trying to buy while retail is extremely greedy. Trap incoming."
        if pa_signal == "SELL" and sentiment_signal == "EXTREME_FEAR":
            return True, "VETO: Trying to short while retail is panicking. Short squeeze incoming."
        return False, "APPROVED"