import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Pro Options Engine", layout="wide")

# --- تحسين المظهر ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1, h2, h3 { color: #ccff00; }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
st.sidebar.header("⚙️ Market Controls")
ticker_symbol = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()
dte = st.sidebar.slider("DTE", 1, 365, 45)
iv = st.sidebar.slider("IV (%)", 5, 150, 20)
hv = st.sidebar.number_input("HV", 1, 150, 15)

# --- جلب البيانات ---
try:
    ticker = yf.Ticker(ticker_symbol)
    spot_price = ticker.history(period="1d")['Close'].iloc[-1]
    st.sidebar.metric("Current Price", f"${spot_price:.2f}")
except:
    spot_price = 150.0
    st.sidebar.error("Could not fetch live price, using $150.0")

# --- عرض الميزات ---
st.title("📊 Premium Strategy Engine")

# 1. جدول المصفوفة الديناميكي
deltas = [0.10, 0.20, 0.30, 0.50]
spreads = [20.0, 25.0]

data = []
for d in deltas:
    row = {"Delta": d}
    for s in spreads:
        row[f"${s} Spread"] = f"${(d*s*iv/20):.2f}"
    data.append(row)

df = pd.DataFrame(data)
st.subheader("Premium Matrix")
st.table(df)

# 2. الرسوم البيانية (P&L Curve)
st.subheader("Risk/Reward Curve")
spread_width = st.selectbox("Select Spread Width", spreads)
x = np.linspace(spot_price*0.9, spot_price*1.1, 100)
y = [min(spread_width, max(-spread_width, spot_price - i)) for i in x]

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='P&L'))
fig.update_layout(template="plotly_dark", xaxis_title="Stock Price", yaxis_title="Profit/Loss")
st.plotly_chart(fig, use_container_width=True)

st.success("🏁 النظام الآن بكامل ميزاته (الرسوم، الجداول، والحسابات)!")
