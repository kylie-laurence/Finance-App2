import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import qrcode
from io import BytesIO

st.set_page_config(page_title="Stock Analysis App", layout="centered")

st.title("📈 Individual Stock Analysis Dashboard")

# -----------------------------
# QR CODE SECTION
# -----------------------------
APP_URL = "https://your-streamlit-app-url.com"  # replace after deployment

def generate_qr(url):
    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

st.subheader("📲 Scan to Open App")
st.image(generate_qr(APP_URL), width=180)

st.markdown("---")

# -----------------------------
# USER INPUT
# -----------------------------
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, MSFT):", "AAPL")

if ticker:

    # -----------------------------
    # STEP 1: DATA COLLECTION
    # -----------------------------
    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        st.error("No data found for this ticker.")
    else:
        close = data["Close"]

        st.subheader("📊 Price Chart")
        st.line_chart(close)

        # -----------------------------
        # STEP 2: TREND ANALYSIS
        # -----------------------------
        current_price = close.iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        if current_price > ma20 > ma50:
            trend = "Strong Uptrend"
        elif current_price < ma20 < ma50:
            trend = "Strong Downtrend"
        else:
            trend = "Mixed Trend"

        # -----------------------------
        # STEP 3: RSI (MOMENTUM)
        # -----------------------------
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_latest = rsi.iloc[-1]

        if rsi_latest > 70:
            rsi_signal = "Overbought (Sell Signal)"
        elif rsi_latest < 30:
            rsi_signal = "Oversold (Buy Signal)"
        else:
            rsi_signal = "Neutral"

        # -----------------------------
        # STEP 4: VOLATILITY
        # -----------------------------
        returns = close.pct_change()
        volatility = returns.rolling(20).std() * np.sqrt(252)
        vol_latest = volatility.iloc[-1]

        if vol_latest > 0.40:
            vol_level = "High"
        elif vol_latest >= 0.25:
            vol_level = "Medium"
        else:
            vol_level = "Low"

        # -----------------------------
        # STEP 5: RECOMMENDATION
        # -----------------------------
        if trend == "Strong Uptrend" and rsi_latest < 70:
            recommendation = "BUY"
            reason = "Uptrend confirmed with no overbought condition."
        elif trend == "Strong Downtrend" and rsi_latest > 30:
            recommendation = "SELL"
            reason = "Downtrend with weak momentum recovery."
        else:
            recommendation = "HOLD"
            reason = "Mixed signals across trend and momentum."

        # -----------------------------
        # OUTPUT
        # -----------------------------
        st.subheader("📌 Analysis Results")

        st.write(f"**Current Price:** ${current_price:.2f}")
        st.write(f"**20-Day MA:** ${ma20:.2f}")
        st.write(f"**50-Day MA:** ${ma50:.2f}")
        st.write(f"**Trend:** {trend}")

        st.write(f"**RSI (14):** {rsi_latest:.2f} → {rsi_signal}")
        st.write(f"**Volatility:** {vol_latest:.2%} ({vol_level})")

        st.subheader("📢 Recommendation")
        st.write(f"### {recommendation}")
        st.write(reason)
