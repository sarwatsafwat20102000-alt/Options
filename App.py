import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# محاولة استيراد yfinance بشكل آمن
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

st.set_page_config(page_title="Options Engine", layout="wide")

st.sidebar.header("⚙️ Market Controls")
ticker_symbol = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()
dte = st.sidebar.slider("DTE", 1, 365, 45)
iv = st.sidebar.slider("IV (%)", 5, 150, 20)
hv = st.sidebar.number_input("HV", 1, 150, 15)

# جلب السعر
spot_price = 150.0 # قيمة افتراضية
if YFINANCE_AVAILABLE:
    try:
        ticker = yf.Ticker(ticker_symbol)
        spot_price = ticker.history(period="1d")['Close'].iloc[-1]
    except:
        pass

st.sidebar.metric("Current Price", f"${spot_price:.2f}")

st.title("📊 Premium Strategy Engine")

# مصفوفة الأسعار
deltas = [0.10, 0.20, 0.30, 0.50]
spreads = [20.0, 25.0]
data = []
for d in deltas:
    row = {"Delta": d}
    for s in spreads:
        row[f"${s} Spread"] = f"${(d*s*iv/20):.2f}"
    data.append(row)

st.table(pd.DataFrame(data))

# الرسم البياني
spread_width = st.selectbox("Select Spread Width", spreads)
x = np.linspace(spot_price*0.9, spot_price*1.1, 100)
y = [min(spread_width, max(-spread_width, spot_price - i)) for i in x]

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='P&L'))
fig.update_layout(template="plotly_dark", title="Risk/Reward Curve")
st.plotly_chart(fig, use_container_width=True)
