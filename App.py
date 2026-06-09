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
        # محاولة الجلب السريع للسعر المباشر
        if stock.info and 'regularMarketPrice' in stock.info and stock.info['regularMarketPrice'] is not null:
            return stock, float(stock.info['regularMarketPrice']), stock.info.get('longName', ticker)
        else:
            hist = stock.history(period="1d")
            if not hist.empty:
                return stock, float(hist['Close'].iloc[-1]), ticker
            
            # خيار احتياطي أمان في حال وجود حظر سحابي على الـ IP من ياهو فاينانس
            fallback_prices = {"NVDA": 208.64, "AAPL": 175.50, "TSLA": 180.20, "AMZN": 178.00, "MSFT": 420.00}
            price = fallback_prices.get(ticker, 150.00)
            return stock, price, f"{ticker} Corporation (Simulation Mode)"
    except Exception:
        # تأمين التطبيق من الانهيار تماماً وتوفير بيئة محاكاة مستقرة
        fallback_prices = {"NVDA": 208.64, "AAPL": 175.50, "TSLA": 180.20, "AMZN": 178.00, "MSFT": 420.00}
        price = fallback_prices.get(ticker, 150.00)
        return None, price, f"{ticker} Corporation (Simulation Mode)"

stock_obj, price_now, company_name = get_stock_details(ticker_input)

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
    badge_html = f"""
    <div style='padding: 15px; background-color: #2c1a04; border-left: 5px solid #ff9900; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #ff9900; font-size: 1.1rem;'>ELEVATED PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>Options premium is rich compared to real-world historical movement. Preferred Strategy: Credit Spreads (Net Short Vega).</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)
else:
    badge_html = f"""
    <div style='padding: 15px; background-color: #042416; border-left: 5px solid #198754; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #198754; font-size: 1.1rem;'>NEUTRAL / CHEAP ENVIRONMENT (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>Options premium is fair or underpriced. Preferred Strategy: Debit Spreads (Net Long Vega).</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

# --- Premium Matrix Grid ---
st.markdown("### 🗺️ PREMIUM MATRIX GRID")

spread_widths = [20.0, 22.5, 25.0, 27.5]
delta_rows = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70]

iv_factor = iv / 20.0
dte_factor = np.sqrt(dte / 45.0)

html_table = "<table style='width:100%; border-collapse: collapse; background-color: #161b22; color: #e2e8f0; text-align: center; font-family: monospace;'>"
html_table += "<tr style='background-color: #21262d; color: #ccff00; font-weight: bold; border-bottom: 2px solid #30363d;'>"
html_table += "<th style='padding: 12px; border: 1px solid #30363d;'>Δ - DELTA</th>"
for w in spread_widths:
    html_table += f"<th style='padding: 12px; border: 1px solid #30363d;'>${w} SPREAD</th>"
html_table += "</tr>"

for d_val in delta_rows:
    html_table += "<tr style='border-bottom: 1px solid #30363d;'>"
    html_table += f"<td style='padding: 10px; font-weight: bold; background-color: #1f242c; border: 1px solid #30363d;'>{d_val:.2f}</td>"
    
    for width in spread_widths:
        mid_premium = width * d_val * iv_factor * dte_factor
        lower_band = mid_premium * 0.88
        upper_band = mid_premium * 1.12
        premium_ratio = (mid_premium / width) * 100
        
        if premium_ratio < 28:
            bg_color = "#0f5132"       # Enhanced Dark emerald green
            text_color = "#d1e7dd"     # Crisp green text
        elif 28 <= premium_ratio < 42:
            bg_color = "#332701"       # Deep dark gold
            text_color = "#fff3cd"
        elif 42 <= premium_ratio < 58:
            bg_color = "#2c1a04"       # Deep dark orange
            text_color = "#ffe699"
        else:
            bg_color = "#2c0404"       # Muted deep burgundy
            text_color = "#f8d7da"
            
        cell_text = f"${lower_band:.1f} - ${upper_band:.1f}"
        html_table += f"<td style='padding: 10px; background-color: {bg_color}; color: {text_color}; font-weight: bold; border: 1px solid #30363d;'>{cell_text}</td>"
    html_table += "</tr>"

html_table += "</table>"
st.markdown(html_table, unsafe_
