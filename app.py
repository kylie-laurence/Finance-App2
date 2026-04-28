import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import qrcode
from io import BytesIO

st.title("📈 Individual Stock Analysis")

# --- URL for QR code (update after deployment) ---
APP_URL = "https://your-streamlit-app-url.com"

# --- Generate QR Code ---
def generate_qr(url):
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return buffer

st.subheader("📲 Scan to Open This App")
qr_img = generate_qr(APP_URL)
st.image(qr_img, width=200)

# --- User Input ---
ticker = st.text_input("Enter Stock Ticker:", "AAPL")

if ticker:
    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        st.error("No data found.")
    else:
        close = data['Close']

        st.line_chart(close)

        # --- Trend ---
        current_price = close.iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        if current_price > ma20 > ma50:
            trend = "Strong Uptrend"
        elif current_price < ma20 < ma50:
            trend = "Strong Downtrend"
        else:
            trend = "Mixed Trend"

        # --- RSI ---
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_latest = rsi.iloc[-1]

        if rsi_latest > 70:
            rsi_signal = "Overbought (Sell)"
        elif rsi_latest < 30:
            rsi_signal = "Oversold (Buy)"
        else:
            rsi_signal = "Neutral"

        # --- Volatility ---
        returns = close.pct_change()
        vol = returns.rolling(20).std() * np.sqrt(252)
        vol_latest = vol.iloc[-1]

        if vol_latest > 0.40:
            vol_level = "High"
        elif vol_latest >= 0.25:
            vol_level = "Medium"
        else:
            vol_level = "Low"

        # --- Recommendation ---
        if trend == "Strong Uptrend" and rsi_latest < 70:
            rec = "BUY"
            reason = "Uptrend with healthy momentum"
        elif trend == "Strong Downtrend" and rsi_latest > 30:
            rec = "SELL"
            reason = "Downtrend persists"
        else:
            rec = "HOLD"
            reason = "Mixed signals"

        # --- Output ---
        st.subheader("📊 Results")
        st.write(f"Price: ${current_price:.2f}")
        st.write(f"20MA: ${ma20:.2f}")
        st.write(f"50MA: ${ma50:.2f}")
        st.write(f"Trend: {trend}")

        st.write(f"RSI: {rsi_latest:.2f} → {rsi_signal}")
        st.write(f"Volatility: {vol_latest:.2%} ({vol_level})")

        st.subheader("📌 Recommendation")
        st.write(f"### {rec}")
        st.write(reason)
