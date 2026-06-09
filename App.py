import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go

# إعدادات الشاشة والمظهر الداكن المتوافق مع الجوال
st.set_page_config(page_title="AI Options Pricing & Strategy Engine", layout="wide", initial_sidebar_state="expanded")

# تصميم مخصص للواجهة لمنع تداخل النصوص والخطوط
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; color: #e2e8f0; }
    .sidebar .sidebar-content { background: #1a1f2c; }
    div.stButton > button:first-child { background-color: #ff4b4b; color:white; }
    h1, h2, h3 { color: #ccff00 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .metric-box { padding: 15px; background: #1a1f2c; border-radius: 8px; border-left: 5px solid #ccff00; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# 1️⃣ بيانات الـ API Key الخاص بك من منصة Massive Data
MASSIVE_API_KEY = "pfjR_9mPAIHwbw8GqBc07DcXEMeLrEO4"

@st.cache_data(ttl=5)  # تحديث سريع جداً للفحص
def get_stock_price_massive(ticker):
    sym = ticker.upper().strip()
    
    # قائمة بالروابط المحتملة لتجربتها بشكل ديناميكي بناءً على توثيق منصة ماسيف
    endpoints = [
        f"https://api.massive.com/v1/market/prices?ticker={sym}",
        f"https://api.massive.com/v1/prices/{sym}",
        f"https://api.massive.com/v1/market/tickers/{sym}"
    ]
    
    headers = {
        "Authorization": f"Bearer {MASSIVE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    last_error = ""
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=4)
            
            if response.status_code == 200:
                res_data = response.json()
                
                # فحص واستخراج السعر بكافة الأشكال البرمجية المتوقعة
                price = None
                if isinstance(res_data, dict):
                    price = (res_data.get("price") or 
                             res_data.get("last_price") or 
                             res_data.get("last") or
                             res_data.get("data", {}).get("price") or
                             res_data.get("results", [{}])[0].get("price"))
                
                if price is not None:
                    return float(price), f"{sym} (المباشر الحقيقي ✅)", None
            else:
                last_error = f"رابط {url.split('/v1/')[1]} أعاد كود خطأ: {response.status_code}"
        except Exception as e:
            last_error = f"فشل الاتصال: {str(e)}"
            
    # إذا فشلت كل المحاولات، نعود للبيانات الاحتياطية ونمرر نص الخطأ لعرضه
    fallbacks = {"NVDA": 305.50, "AAPL": 180.25, "TSLA": 175.40, "AMZN": 185.10, "MSFT": 425.00}
    return fallbacks.get(sym, 150.00), f"{sym} (وضع الاحتياط ⚠️)", last_error

# --- الواجهة الجانبية (شريط التحكم) ---
st.sidebar.markdown("### 📊 MARKET INPUTS / مدخلات السوق")
ticker_input = st.sidebar.text_input("Underlying Ticker / رمز السهم النشط", value="AAPL").upper()

# جلب السعر المحدث مع فحص الأخطاء
spot_price, company_name, error_log = get_stock_price_massive(ticker_input)

st.sidebar.markdown(f"""
<div class='metric-box'>
    <span style='font-size:0.85rem; color:#8892b0;'>السعر الحالي لـ {ticker_input}</span><br>
    <span style='font-size:1.8rem; font-weight:bold; color:#ccff00;'>${spot_price:,.2f}</span>
</div>
""", unsafe_allow_html=True)

# نافذة تشخيص الأخطاء الذكية: ستظهر فقط إذا كان هناك مشكلة في الربط مع ماسيف لتعلمنا بالسبب فوراً
if error_log:
    st.sidebar.error(f"🔍 **تقرير تشخيص الاتصال (Massive Debug):**\n\n{error_log}")

st.sidebar.markdown("### ⚙️ ضبط متغيرات النموذج")
dte = st.sidebar.slider("(DTE) الأيام حتى الانتهاء", min_value=1, max_value=365, value=45)
iv = st.sidebar.slider("التقلب الضمني الحالي (%) IV", min_value=5, max_value=150, value=20)
ivp = st.sidebar.slider("(IVP %) النسبة المئوية للتقلب", min_value=0, max_value=100, value=50)
hv = st.sidebar.number_input("(HV) التقلب التاريخي المحسوب", min_value=1, max_value=150, value=15)

# --- الشاشة الرئيسية ---
st.markdown("<h2>📊 PREMIUM STRATEGY ENGINE</h2>", unsafe_allow_html=True)
st.markdown(f"### 🎯 رمز السهم النشط: {ticker_input} — {company_name}")

# حساب نسبة بيئة البريميوم وعرض البطاقة الإرشادية
iv_hv_ratio = iv / hv if hv > 0 else 1.0

if iv_hv_ratio > 1.25:
    status_color = "#d97706"
    status_text = f"ELEVATED PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)"
    recommendation = "Options premium is rich compared to real-world historical movement. PREFERENCE: Credit Spreads / Scaling out of Net Long Vega positions."
elif iv_hv_ratio < 0.85:
    status_color = "#059669"
    status_text = f"CHEAP PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)"
    recommendation = "Options premium is underpriced relative to historical volatility. PREFERENCE: Debit Spreads / Net Long Vega positions."
else:
    status_color = "#1e293b"
    status_text = f"FAIRLY PRICED PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)"
    recommendation = "Premium is in-line with current historical movement. Focus on directional structure or Theta collection."

st.markdown(f"""
<div style='background-color:{status_color}; padding:15px; border-radius:5px; border-left:5px solid #ccff00; margin-bottom:25px;'>
    <b style='color:#ffffff; font-size:1.05rem;'>{status_text}</b><br>
    <span style='color:#e2e8f0; font-size:0.95rem;'>{recommendation}</span>
</div>
""", unsafe_allow_html=True)

# 2️⃣ بناء وحساب مصفوفة شبكة الأسعار (Premium Matrix Grid)
st.markdown("### 🗺️ خريطة وجدولة أسعار العقود (Premium Matrix Grid)")

deltas = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.75]
spread_widths = [20.0, 22.5, 25.0, 27.5]

dte_decay = np.sqrt(dte / 45.0)
iv_scaling = iv / 20.0

html_table = """
<table style='width:100%; border-collapse: collapse; text-align:center; background-color:#111622; font-family:monospace;'>
    <thead>
        <tr style='background-color:#1e2538; color:#ccff00; font-weight:bold; font-size:0.95rem;'>
            <th style='padding:12px; border:1px solid #2e374f;'>Δ - DELTA</th>
            <th style='padding:12px; border:1px solid #2e374f;'>$20.0 SPREAD</th>
            <th style='padding:12px; border:1px solid #2e374f;'>$22.5 SPREAD</th>
            <th style='padding:12px; border:1px solid #2e374f;'>$25.0 SPREAD</th>
            <th style='padding:12px; border:1px solid #2e374f;'>$27.5 SPREAD</th>
        </tr>
    </thead>
    <tbody>
"""

def get_cell_bg_color(ratio):
    if ratio < 0.28: return "#064e3b"   
    elif ratio < 0.42: return "#78350f" 
    elif ratio < 0.58: return "#9a3412" 
    else: return "#4c0519"              

for d_val in deltas:
    html_table += f"<tr style='border-bottom:1px solid #2e374f;'><td style='padding:12px; font-weight:bold; color:#a0aec0; border:1px solid #2e374f;'>{d_val:.2f}</td>"
    for width in spread_widths:
        mid_premium = width * d_val * iv_scaling * dte_decay
        lower
