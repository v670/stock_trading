import pandas as pd
import numpy as np
import talib
import yfinance as yf
from twilio.rest import Client
import time

# Twilio Credentials (Replace with your actual credentials)
TWILIO_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio Sandbox Number
YOUR_WHATSAPP_NUMBER = "whatsapp:+91XXXXXXXXXX"  # Your WhatsApp Number

# Initialize Twilio Client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(message):
    """Send WhatsApp message using Twilio"""
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=YOUR_WHATSAPP_NUMBER
    )

# List of stocks to monitor
stocks = ["AVANTIFEED.NS", "TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFC.NS"]

# Store alerts to avoid duplicate messages
sent_alerts = {}

# Function to check trading signals
def check_signals(symbol):
    df = yf.download(symbol, period="1y", interval="1d")

    # Calculate Indicators
    df["EMA_10"] = talib.EMA(df["Close"], timeperiod=10)
    df["EMA_50"] = talib.EMA(df["Close"], timeperiod=50)
    df["RSI"] = talib.RSI(df["Close"], timeperiod=14)
    df["MACD"], df["MACD_Signal"], _ = talib.MACD(df["Close"], fastperiod=12, slowperiod=26, signalperiod=9)

    # Generate Buy/Sell Signals
    df["Buy_Signal"] = (df["EMA_10"] > df["EMA_50"]) & (df["RSI"] < 40) & (df["MACD"] > df["MACD_Signal"])
    df["Sell_Signal"] = (df["Close"] >= df["Close"].shift(1) * 1.20) | (df["RSI"] > 70) | (df["EMA_10"] < df["EMA_50"]) | (df["MACD"] < df["MACD_Signal"])

    # Check latest signal
    latest_data = df.iloc[-1]
    latest_price = latest_data["Close"]

    if latest_data["Buy_Signal"] and sent_alerts.get(symbol) != "BUY":
        message = f"🔔 BUY Alert: {symbol}\nPrice: ₹{latest_price:.2f}\nReason: EMA Crossover, RSI & MACD Confirmation"
        send_whatsapp_message(message)
        print(message)
        sent_alerts[symbol] = "BUY"

    elif latest_data["Sell_Signal"] and sent_alerts.get(symbol) != "SELL":
        message = f"🚨 SELL Alert: {symbol}\nPrice: ₹{latest_price:.2f}\nReason: RSI Overbought / 20% Profit Reached"
        send_whatsapp_message(message)
        print(message)
        sent_alerts[symbol] = "SELL"

    else:
        print(f"{symbol}: No trade signal today.")

# Run for each stock
for stock in stocks:
    check_signals(stock)
    time.sleep(2)  # Avoid API rate limits
