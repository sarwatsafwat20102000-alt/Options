import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. إعدادات الصفحة الموحدة
st.set_page_config(page_title="Premium Intelligence Engine", layout="wide", initial_sidebar_state="expanded")

# 2. التنسيق الموحد (CSS) - يضمن ظهور الألوان والخطوط كما في صورك
st.markdown("""
<style>
    .block-container { background-color: #0d1117; color: #e2e8f0; }
    h1, h2, h3 { color: #ccff00 !important; font-family: monospace; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. الدوال البرمجية (دالة واحدة شاملة)
@st.cache_resource
def get_full_analysis(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="10d")
    # منطق الإشارات الذكية
    price_drop = (hist['Close'].iloc[-1] < hist['Close'].iloc[-2]) and (hist['Close'].iloc[-2] < hist['Close'].iloc[-3])
    vol_inc = (hist['Volume'].iloc[-1] > hist['Volume'].iloc[-2]) and (hist['Volume'].iloc[-2] > hist['Volume'].iloc[-3])
    tech = "🚨 ضغط بيع (فني)" if (price_drop and vol_inc) else "✅ مستقر"
    pe = stock.info.get('forwardPE', 20)
    fund = "🟢 قيمة جذابة" if pe < 25 else "🟡 تقييم مرتفع"
    macro = "🟢 إيجابي" if hist['Close'].iloc[-1] > hist['Close'].iloc[-5] else "🟡 حذر"
    return tech, fund, macro, hist, stock.info.get('longName', ticker)

# 4. واجهة المستخدم
st.sidebar.header("📊 MARKET INPUTS")
ticker = st.sidebar.text_input("Ticker", value="NVDA").upper().strip()
tech, fund, macro, hist, company_name = get_full_analysis(ticker)

st.title("📈 PREMIUM STRATEGY ENGINE")
st.subheader(f"رمز السهم النشط: {ticker} — {company_name}")

c1, c2, c3 = st.columns(3)
c1.metric("الفني", tech)
c2.metric("الأساسي", fund)
c3.metric("الماكرو", macro)

st.markdown("---")
# (هنا يوضع كود الجدول والرسوم الذي تملكه، وسيعمل بشكل سليم الآن)
