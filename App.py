import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. إعدادات الصفحة
st.set_page_config(page_title="Premium Strategy Engine", layout="wide")

# 2. الدوال البرمجية (مع معالجة الأخطاء)
@st.cache_resource
def get_safe_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="10d")
        info = stock.info
        
        # تحليل فني آمن
        price_drop = (hist['Close'].iloc[-1] < hist['Close'].iloc[-2]) if len(hist) > 2 else False
        vol_inc = (hist['Volume'].iloc[-1] > hist['Volume'].iloc[-2]) if len(hist) > 2 else False
        tech = "🚨 ضغط بيع (فني)" if (price_drop and vol_inc) else "✅ مستقر"
        
        # تحليل أساسي آمن (استخدام .get لتجنب الخطأ إذا كان الحقل مفقوداً)
        pe = info.get('forwardPE', 20)
        fund = "🟢 قيمة جذابة" if pe < 25 else "🟡 تقييم مرتفع"
        macro = "🟢 إيجابي" if len(hist) > 0 and hist['Close'].iloc[-1] > hist['Close'].iloc[0] else "🟡 حذر"
        
        return tech, fund, macro, info.get('longName', ticker), hist
    except:
        return "N/A", "N/A", "N/A", "Error Loading Data", pd.DataFrame()

# 3. الواجهة
st.sidebar.header("📊 MARKET INPUTS")
ticker = st.sidebar.text_input("Ticker", value="NVDA").upper().strip()

tech, fund, macro, name, hist = get_safe_data(ticker)

st.title("📈 PREMIUM STRATEGY ENGINE")
st.subheader(f"رمز السهم: {ticker} — {name}")

c1, c2, c3 = st.columns(3)
c1.metric("الفني", tech)
c2.metric("الأساسي", fund)
c3.metric("الماكرو", macro)

st.markdown("---")
st.write("التطبيق يعمل الآن.")
