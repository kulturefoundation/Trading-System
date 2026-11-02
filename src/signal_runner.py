import requests
import pandas as pd
import json
import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load secret keys
load_dotenv()
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("Missing Telegram keys in .env file")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram Error: {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def fetch_binance_data(symbol="BTCUSDT", interval="1m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col])
        
    return df

def calculate_indicators(df):
    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
    
    df['tr0'] = abs(df['high'] - df['low'])
    df['tr1'] = abs(df['high'] - df['close'].shift())
    df['tr2'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    return df

def log_signal(timestamp, action, price, atr):
    os.makedirs("outputs", exist_ok=True)
    
    sl = price - (atr * 2.0) if action == "LONG" else price + (atr * 2.0)
    tp = price + (atr * 3.0) if action == "LONG" else price - (atr * 3.0)
    
    signal_data = {
        "timestamp": timestamp,
        "pair": "BTCUSDT",
        "action": action,
        "entry_price": price,
        "stop_loss": sl,
        "take_profit": tp
    }
    
    with open("outputs/signals.jsonl", "a") as f:
        f.write(json.dumps(signal_data) + "\n")
    
    # Send to Telegram
    msg = f"🚨 *{action} SIGNAL* 🚨\n\n*Pair:* BTCUSDT\n*Entry:* ${price:.2f}\n*SL:* ${sl:.2f}\n*TP:* ${tp:.2f}"
    send_telegram(msg)
    print(f"\n🚨 SIGNAL SENT TO TELEGRAM & LOGGED 🚨\n")

def run_loop():
    last_candle_time = None
    
    # Send a test message when it starts
    send_telegram("🤖 Scalper Bot is now online and watching the market!")
    
    while True:
        try:
            df = fetch_binance_data()
            df = calculate_indicators(df)
            
            last = df.iloc[-2]
            prev = df.iloc[-3]
            current_candle_time = last['timestamp']
            
            long_signal = (last['ema9'] > last['ema21']) and (prev['ema9'] <= prev['ema21'])
            short_signal = (last['ema9'] < last['ema21']) and (prev['ema9'] >= prev['ema21'])
            
            timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            candle_time = current_candle_time.strftime("%H:%M")
            
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("========================================")
            print(f" 🤖 BTC 1-MIN SCALPER - WATCHING...")
            print("========================================")
            print(f" Current Time: {timestamp}")
            print(f" Watching Candle: {candle_time}")
            print(f" Price: ${last['close']:.2f}")
            print(f" 9 EMA: ${last['ema9']:.2f}")
            print(f" 21 EMA: ${last['ema21']:.2f}")
            print("----------------------------------------")
            
            if current_candle_time != last_candle_time:
                if long_signal:
                    print(f" 🔥 LONG SIGNAL! Price crossed UP.")
                    log_signal(timestamp, "LONG", last['close'], last['atr'])
                elif short_signal:
                    print(f" 🩸 SHORT SIGNAL! Price crossed DOWN.")
                    log_signal(timestamp, "SHORT", last['close'], last['atr'])
                else:
                    if last['ema9'] > last['ema21']:
                        print(" Status: Waiting... (Trend is UP)")
                    else:
                        print(" Status: Waiting... (Trend is DOWN)")
                last_candle_time = current_candle_time
            else:
                print(" Status: Waiting for next candle to close...")
            
            print("========================================")
            print(" Press Ctrl+C to stop.")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nStopping bot...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_loop()
