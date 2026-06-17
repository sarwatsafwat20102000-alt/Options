import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. الإعدادات الأساسية
st.set_page_config(page_title="Premium Strategy Engine", layout="wide")

# 2. تنسيق CSS لضمان المظهر الاحترافي المظلم
st.markdown("""
<style>
    .block-container { background-color: #0d1117; color: #e2e8f0; }
    h1, h2, h3 { color: #ccff00 !important; font-family: monospace; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية (Market Controls)
st.sidebar.header("⚙️ Market Controls")
ticker = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()
dte = st.sidebar.slider("DTE", 5, 365, 45)
iv = st.sidebar.slider("IV (%)", 5, 120, 20)
hv = st.sidebar.number_input("HV", value=15)
stock = yf.Ticker(ticker)
price = stock.history(period="1d")['Close'].iloc[-1] if not stock.history(period="1d").empty else 150.0
st.sidebar.metric("Current Price", f"${price:.2f}")

# 4. العنوان والإشارات (التحليلات الذكية المدمجة)
st.title("📊 Premium Strategy Engine")
st.subheader(f"رمز السهم النشط: {ticker}")

# منطق حساب الإشارات (الفنية والأساسية)
hist = stock.history(period="5d")
tech = "🚨 ضغط بيع (فني)" if len(hist)>2 and hist['Close'].iloc[-1] < hist['Close'].iloc[-2] < hist['Close'].iloc[-3] else "✅ مستقر"
fund = "🟢 قيمة جذابة" if stock.info.get('forwardPE', 20) < 25 else "🟡 تقييم مرتفع"
macro = "🟢 إيجابي" if hist['Close'].iloc[-1] > hist['Close'].iloc[-5] else "🟡 حذر"

c1, c2, c3 = st.columns(3)
c1.metric("الفني", tech)
c2.metric("الأساسي", fund)
c3.metric("الماكرو", macro)

# 5. جدول العقود (Premium Matrix Grid)
st.markdown("### 🗺️ Premium Matrix Grid")
spreads = [20.0, 22.5, 25.0, 27.5]
deltas = [0.1, 0.2, 0.3, 0.5]
matrix_data = []
for d in deltas:
    row = {"Delta": d}
    for s in spreads:
        row[f"${s} Spread"] = f"${d*s*1.2:.1f} - ${d*s*1.5:.1f}"
    matrix_data.append(row)
st.table(pd.DataFrame(matrix_data))

# 6. الرسوم البيانية (P&L و IV)
st.markdown("### 📊 الرسوم البيانية المتقدمة")
col1, col2 = st.columns(2)

with col1:
    fig_pnl = go.Figure().add_trace(go.Scatter(y=[0, 5, 10, 15], x=[270, 280, 290, 300], line=dict(color='#ccff00')))
    fig_pnl.update_layout(template="plotly_dark", title="P&L Curve")
    st.plotly_chart(fig_pnl, use_container_width=True)

with col2:
    fig_iv = go.Figure().add_trace(go.Scatter(y=[1, 5, 10, 15], x=[20, 40, 80, 120], line=dict(color='#ff9900')))
    fig_iv.update_layout(template="plotly_dark", title="IV Sensitivity")
    st.plotly_chart(fig_iv, use_container_width=True)
