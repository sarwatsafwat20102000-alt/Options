import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. إعدادات الصفحة
st.set_page_config(page_title="Premium Intelligence Engine", layout="wide", initial_sidebar_state="expanded")

# 2. تنسيق الواجهة
st.markdown("""
<style>
    .block-container { padding-top: 1rem; background-color: #0d1117; }
    h1, h2, h3 { color: #ccff00 !important; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية ومدخلات السوق
st.sidebar.header("📊 MARKET INPUTS")
ticker_input = st.sidebar.text_input("رمز السهم (Ticker)", value="NVDA").upper().strip()

@st.cache_resource
def get_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    price = float(hist['Close'].iloc[-1])
    return hist, price, stock

hist, price_now, stock = get_data(ticker_input)

# --- كود إشارات الشراء (Buying Signals Logic) ---
def analyze_signals(df, stock_info):
    # الفني: نقص السعر يومين + زيادة حجم التداول يومين
    price_drop = (df['Close'].iloc[-1] < df['Close'].iloc[-2]) and (df['Close'].iloc[-2] < df['Close'].iloc[-3])
    vol_inc = (df['Volume'].iloc[-1] > df['Volume'].iloc[-2]) and (df['Volume'].iloc[-2] > df['Volume'].iloc[-3])
    
    # الأساسي: مكرر الربحية
    pe = stock_info.info.get('forwardPE', 20)
    
    # بناء النتيجة
    signals = []
    if price_drop and vol_inc:
        signals.append(("🚨 ضغط بيع (فني)", "فرصة للمراقبة / Credit Spreads"))
    
    fund_msg = "🟢 تقييم جذاب" if pe < 25 else "🟡 تقييم مرتفع"
    signals.append(("📊 التحليل الأساسي", fund_msg))
    
    return signals

signals = analyze_signals(hist, stock)

# عرض الإشارات في أعلى الصفحة
st.subheader("💡 الإشارات الذكية (Buying Signals)")
cols = st.columns(len(signals))
for i, (title, msg) in enumerate(signals):
    cols[i].metric(title, msg)

st.sidebar.metric("السعر الحالي", f"${price_now:.2f}")

# --- باقي الكود الخاص بك (المتغيرات والجدول والرسوم) ---
# [قم بلصق باقي كود الجدول والرسوم الذي أرفقته سابقاً هنا تحت هذا السطر]
