import os
import time
from dotenv import load_dotenv
from engine.data import DataAgent
from engine.price_action import PriceActionAgent
from engine.sentiment import SentimentAgent
from engine.risk_manager import RiskManager
from telegram_utils import send_telegram

load_dotenv()

def run_war_room():
    data_agent = DataAgent()
    pa_agent = PriceActionAgent()
    sent_agent = SentimentAgent()
    risk_agent = RiskManager()
    
    print("War Room checking market...")
    
    try:
        df, funding_rate = data_agent.get_market_data()
        
        pa_signal, pa_reason = pa_agent.evaluate(df)
        sent_signal, sent_reason = sent_agent.evaluate(funding_rate)
        
        veto, risk_reason = risk_agent.veto_trade(pa_signal, sent_signal)
        
        print("========================================")
        print(f" WAR ROOM | Price: ${df['close'].iloc[-1]:.2f} | Funding: {funding_rate*100:.4f}%")
        print("========================================")
        print(f" [Price Action]: {pa_signal} ({pa_reason})")
        print(f" [Sentiment]: {sent_signal} ({sent_reason})")
        print(f" [Risk Manager]: {'VETO' if veto else 'PASS'} ({risk_reason})")
        print("========================================")
        
        if pa_signal in ["BUY", "SELL"] and not veto:
            # Calculate Stop Loss and Take Profit
            atr = df['high'].rolling(14).max() - df['low'].rolling(14).min()
            current_atr = atr.iloc[-1]
            
            if pa_signal == "BUY":
                sl = df['close'].iloc[-1] - (current_atr * 1.5)
                tp = df['close'].iloc[-1] + (current_atr * 2.0)
            else:
                sl = df['close'].iloc[-1] + (current_atr * 1.5)
                tp = df['close'].iloc[-1] - (current_atr * 2.0)
            
            msg = (f"🚨 *TRADE APPROVED* 🚨\n\n"
                   f"Action: {pa_signal}\n"
                   f"Entry: ${df['close'].iloc[-1]:.2f}\n"
                   f"Stop Loss: ${sl:.2f}\n"
                   f"Take Profit: ${tp:.2f}\n\n"
                   f"PA: {pa_reason}\n"
                   f"Sent: {sent_reason}")
            
            send_telegram(msg)
            print(" SENT TO TELEGRAM!")
        else:
            print("No trade approved this run. Waiting for next check.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_war_room()