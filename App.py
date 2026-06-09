import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# Page configuration optimized for mobile and professional dark UI
st.set_page_config(
    page_title="Premium Strategy Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styled CSS for modern dark theme and professional font scales
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; background-color: #0d1117; }
    h1, h2, h3, h4 { color: #ccff00 !important; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #30363d; }
    .reportview-container { background: #0d1117; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Market Inputs ---
st.sidebar.header("📊 MARKET INPUTS")
ticker_input = st.sidebar.text_input("Underlying Ticker", value="NVDA").upper().strip()

@st.cache_resource
def get_stock_details(ticker):
    try:
        stock = yf.Ticker(ticker)
        if stock.info and 'regularMarketPrice' in stock.info:
            return stock, stock.info['regularMarketPrice'], stock.info.get('longName', ticker)
        else:
            hist = stock.history(period="1d")
            if not hist.empty:
                return stock, hist['Close'].iloc[-1], ticker
            return None, None, None
    except:
        return None, None, None

stock_obj, price_now, company_name = get_stock_details(ticker_input)

if price_now is None:
    st.error(f"⚠️ Cloud Error: Unable to fetch live data for ({ticker_input}). Please verify ticker symbol.")
    st.stop()

# --- Main App Header ---
st.title("📈 PREMIUM STRATEGY ENGINE")
st.subheader(f"Active Ticker: {ticker_input} — {company_name}")

st.sidebar.metric(label=f"{ticker_input} Spot Price", value=f"${price_now:.2f}")
st.sidebar.markdown("---")

# --- Sidebar: Model Parameters ---
st.sidebar.header("🎛️ MODEL PARAMETERS")
dte = st.sidebar.slider("Days to Expiry (DTE)", 5, 365, 45)
iv = st.sidebar.slider("Implied Volatility (IV %)", 5, 120, 40)
ivp = st.sidebar.slider("IV Percentile (IVP %)", 0, 100, 50)
hv = st.sidebar.number_input("Historical Volatility (HV %)", value=15)

# Automatic Environment Analysis Badge
iv_hv_ratio = iv / hv if hv > 0 else 1.0
if iv_hv_ratio > 1.2:
    st.markdown(f"""
    <div style='padding: 15px; background-color: #2c1a04; border-left: 5px solid #ff9900; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #ff9900; font-size: 1.1rem;'>ELEVATED PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>Options premium is rich compared to real-world historical movement
