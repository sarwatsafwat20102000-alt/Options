import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# إعداد الواجهة لتكون مظلمة (Dark Mode)
st.set_page_config(page_title="Premium Strategy Engine", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #e2e8f0; }
    .stSidebar { background-color: #1a1f2c; }
    h1, h2, h3 { color: #ccff00 !important; }
    .metric-box { background: #1a1f2c; padding: 20px; border-radius: 10px; border-left: 5px solid #ccff00; }
    </style>
""", unsafe_allow_html=True)

# القائمة الجانبية
st.sidebar.header("📊 MARKET INPUTS")
ticker = st.sidebar.text_input("Ticker", "AAPL")
dte = st.sidebar.slider("DTE", 1, 365, 45)
iv = st.sidebar.slider("IV (%)", 5, 150, 20)
hv = st.sidebar.number_input("HV", 1, 100, 15)

# الحسابات
spot_price = 180.25 # يمكنك ربطه بـ API لاحقاً
premium_ratio = iv / hv if hv > 0 else 1

st.title("🚀 Premium Strategy Engine")
st.markdown(f"### 🎯 Ticker: {ticker}")

# بطاقة التنبيه (تطابق الشكل المرجعي)
status = "ELEVATED PREMIUM" if premium_ratio > 1.2 else "FAIR PREMIUM"
color = "#d97706" if status == "ELEVATED PREMIUM" else "#059669"
st.markdown(f"""
<div style='background-color:{color}; padding:15px; border-radius:5px;'>
    <b>{status} (IV/HV: {premium_ratio:.2f})</b><br>
    Preference: Credit Spreads / Scaling out of Net Long Vega.
</div>
""", unsafe_allow_html=True)

# جدول المصفوفة (Matrix Grid)
st.subheader("🗺️ Premium Matrix Grid")
deltas = [0.10, 0.20, 0.30, 0.50, 0.70]
widths = [20.0, 22.5, 25.0, 27.5]
data = []
for d in deltas:
    row = {"Delta": d}
    for w in widths:
        val = w * d * (iv/20) * np.sqrt(dte/45)
        row[f"${w}"] = f"${val:.1f} - ${val*1.2:.1f}"
    data.append(row)

st.table(pd.DataFrame(data))

# الرسوم البيانية
st.subheader("📈 Risk/Reward Curves")
col1, col2 = st.columns(2)
with col1:
    st.line_chart(np.random.randn(20, 2)) # نموذج أولي للرسم
with col2:
    st.line_chart(np.random.randn(20, 2))
