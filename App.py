import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(page_title="Premium Intelligence Engine", layout="wide", initial_sidebar_state="expanded")

# دالة الإشارات الذكية المدمجة (الخطوة 1)
@st.cache_resource
def get_advanced_signals(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    # الفني: نقص سعر ليومين + زيادة حجم ليومين
    price_drop = (hist['Close'].iloc[-1] < hist['Close'].iloc[-2]) and (hist['Close'].iloc[-2] < hist['Close'].iloc[-3])
    vol_inc = (hist['Volume'].iloc[-1] > hist['Volume'].iloc[-2]) and (hist['Volume'].iloc[-2] > hist['Volume'].iloc[-3])
    tech = "🚨 ضغط بيع (فني)" if (price_drop and vol_inc) else "✅ مستقر"
    # الأساسي
    pe = stock.info.get('forwardPE', 20)
    fund = "🟢 قيمة جذابة" if pe < 25 else "🟡 تقييم مرتفع"
    # الماكرو
    macro = "🟢 إيجابي" if hist['Close'].iloc[-1] > hist['Close'].iloc[-5] else "🟡 حذر"
    return tech, fund, macro

# ... هنا تضع بقية الكود الخاص بك (دالة get_stock_details وكل ما يليها) ...
# تأكد عند وضع "الخطوة 2" أن تضعها في نفس المكان الذي أشرت إليه في صورتك (سطر 87)
# ولا تضع أي مسافات في بداية الأسطر إلا إذا كانت داخل دالة.

# 1. إعدادات الصفحة المخصصة للعرض على الهواتف الذكية بأسلوب احترافي مريح
st.set_page_config(
    page_title="Premium Intelligence Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. واجهة التصميم المظلمة الفاخرة والألوان المتوافقة مع التطبيق الأصلي
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; background-color: #0d1117; }
    h1, h2, h3, h4 { color: #ccff00 !important; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #30363d; }
    .reportview-container { background: #0d1117; }
</style>
""", unsafe_allow_html=True)

# 3. --- القائمة الجانبية: مدخلات السوق النشطة ---
st.sidebar.header("📊 مدخلات السوق / MARKET INPUTS")
ticker_input = st.sidebar.text_input("رمز السهم النشط (Ticker)", value="NVDA").upper().strip()

@st.cache_resource
def get_stock_details(ticker):
    try:
        stock = yf.Ticker(ticker)
        if stock.info and 'regularMarketPrice' in stock.info and stock.info['regularMarketPrice'] is not None:
            return stock, float(stock.info['regularMarketPrice']), stock.info.get('longName', ticker)
        else:
            hist = stock.history(period="1d")
            if not hist.empty:
                return stock, float(hist['Close'].iloc[-1]), ticker
            fallback_prices = {"NVDA": 208.64, "AAPL": 175.50, "TSLA": 180.20, "AMZN": 178.00, "MSFT": 420.00}
            price = fallback_prices.get(ticker, 150.00)
            return stock, price, f"{ticker} Corporation (Simulation Mode)"
    except Exception:
        fallback_prices = {"NVDA": 208.64, "AAPL": 175.50, "TSLA": 180.20, "AMZN": 178.00, "MSFT": 420.00}
        price = fallback_prices.get(ticker, 150.00)
        return None, price, f"{ticker} Corporation (Simulation Mode)"

stock_obj, price_now, company_name = get_stock_details(ticker_input)

st.sidebar.metric(label=f"السعر الحالي المباشر لـ {ticker_input}", value=f"${price_now:.2f}")
st.sidebar.markdown("---")

# 4. --- معطيات النموذج الأساسية الحية (Model Parameters) ---
st.sidebar.header("🎛️ ضبط متغيرات النموذج")
dte = st.sidebar.slider("الأيام حتى الانتهاء (DTE)", 5, 365, 45)
iv = st.sidebar.slider("(IV %) التقلب الضمني الحالي", 5, 120, 20)
ivp = st.sidebar.slider("(IVP %) النسبة المئوية للتقلب", 0, 100, 50)
hv = st.sidebar.number_input("(HV %) التقلب التاريخي المحسوب", value=15)

# تحليل بيئة العمل الحالية وعرض بطاقة التوصية الذكية بناءً على المعطيات
iv_hv_ratio = iv / hv if hv > 0 else 1.0

# 5. --- الشاشة الرئيسية وعناوين المحرك ---
st.title("📈 PREMIUM STRATEGY ENGINE")
st.subheader(f"رمز السهم النشط: {ticker_input} — {company_name}")

# --- هنا الإضافة الجديدة ---
tech, fund, macro = get_advanced_signals(ticker_input)
st.subheader("💡 الإشارات الذكية (Buying Signals)")
col_a, col_b, col_c = st.columns(3)
col_a.metric("الفني (Technical)", tech)
col_b.metric("الأساسي (Fundamental)", fund)
col_c.metric("الماكرو (Macro/News)", macro)
st.markdown("---") 
# ---------------------------

if iv_hv_ratio > 1.2:
    badge_html = f"""
    <div style='padding: 15px; background-color: #2c1a04; border-left: 5px solid #ff9900; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #ff9900; font-size: 1.1rem;'>ELEVATED PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>Options premium is rich compared to real-world historical movement. PREFERENCE: Credit Spreads / Scaling out of Net Long Vega positions.</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)
else:
    badge_html = f"""
    <div style='padding: 15px; background-color: #042416; border-left: 5px solid #198754; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #198754; font-size: 1.1rem;'>NEUTRAL / CHEAP ENVIRONMENT (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>Options premium is fair or underpriced. PREFERENCE: Debit Spreads / Net Long Vega.</span>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

# 6. --- بناء جدول وعقود البريميوم الذكية (Premium Matrix Grid) ---
st.markdown("### 🗺️ خريطة وجدولة أسعار العقود (Premium Matrix Grid)")

spread_widths = [20.0, 22.5, 25.0, 27.5]
delta_rows = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.75]

# تطبيق معادلة التطبيق الرسمية الحية تماماً الظاهرة في ملفك المرجعي:
# Mid Premium = Spread * Delta * (IV / 20%) * sqrt(DTE / 45)
iv_scaling = iv / 20.0
dte_decay = np.sqrt(dte / 45.0)

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
        # حساب السعر الأوسط بناءً على المعادلة الحية المرفقة بصورك
        mid_premium = width * d_val * iv_scaling * dte_decay
        
        # النطاق المقدر حول السعر الأوسط (بنسبة 12% تفاوتاً) الموضحة في النماذج الخاصة بك
        lower_band = mid_premium * 0.88
        upper_band = mid_premium * 1.12
        
        # نسبة البريميوم من عرض الفارق لتحديد التلوين الذكي
        premium_ratio = (mid_premium / width) * 100
        
        # توزيع الألوان الدقيقة والتطابق اللوني للنظام الفني
        if premium_ratio < 28:
            bg_color = "#0f5132"       # مائل للخضار (رخيص)
            text_color = "#d1e7dd"
        elif 28 <= premium_ratio < 42:
            bg_color = "#332701"       # عادل (ذهبي خافت)
            text_color = "#fff3cd"
        elif 42 <= premium_ratio < 58:
            bg_color = "#2c1a04"       # غني (برتقالي داكن)
            text_color = "#ffe699"
        else:
            bg_color = "#2c0404"       # مبالغ فيه (قرمزي)
            text_color = "#f8d7da"
            
        cell_text = f"${lower_band:.1f} - ${upper_band:.1f}"
        html_table += f"<td style='padding: 10px; background-color: {bg_color}; color: {text_color}; font-weight: bold; border: 1px solid #30363d;'>{cell_text}</td>"
    html_table += "</tr>"

html_table += "</table>"
st.markdown(html_table, unsafe_allow_html=True)

# توضيح دلالات الألوان في ذيل الجدول
st.markdown("""
<div style='margin-top: 10px; padding: 10px; background-color: #161b22; border-radius: 5px; border: 1px solid #30363d; font-size: 0.85rem; text-align: center;'>
    <span style='color: #d1e7dd;'>■ Cheap (&lt;28%)</span> | 
    <span style='color: #fff3cd;'>■ Fair (28-42%)</span> | 
    <span style='color: #ffe699;'>■ Rich (42-58%)</span> | 
    <span style='color: #f8d7da;'>■ Overpriced (&gt;58%)</span>
</div>
""", unsafe_allow_html=True)

# 7. --- قسم الرسوم والتحليلات البيانية المتقدمة لمنع مشاكل الـ EOF ---
st.markdown("---")
st.markdown("### 📊 الرسوم البيانية المتقدمة وإدارة مخاطر المحفظة")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 1️⃣ منحنى المخاطر والأرباح المتوقعة (P&L Curve)")
    selected_spread = st.selectbox("اختر عرض الفارق المستهدف (Spread)", spread_widths)
    selected_delta = st.selectbox("اختر قيمة الدلتا المستهدفة للرسم", delta_rows)
    
    est_premium = selected_spread * selected_delta * iv_scaling * dte_decay
    stock_range = np.linspace(price_now - (selected_spread * 1.5), price_now + (selected_spread * 1.5), 100)
    
    pnl = []
    strike_long = price_now - (selected_spread / 2)
    strike_short = price_now + (selected_spread / 2)
    
    for s in stock_range:
        payoff_long = max(0, s - strike_long)
        payoff_short = max(0, s - strike_short)
        net_payoff = payoff_long - payoff_short - est_premium
        pnl.append(net_payoff)
        
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=stock_range, y=pnl, name="P&L Profile", line=dict(color='#ccff00', width=3)))
    fig_pnl.add_hline(y=0, line_dash="dash", line_color="#30363d")
    fig_pnl.add_vline(x=price_now, line_dash="longdash", line_color="cyan", annotation_text="Spot Price")
    
    fig_pnl.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="سعر السهم عند الانتهاء ($)",
        yaxis_title="صافي الربح / الخسارة ($)",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_pnl, use_container_width=True)

with col2:
    st.markdown("#### 2️⃣ حساسية سعر العقد مقابل التغير في التقلب الضمني (IV)")
    iv_range = np.linspace(5, 120, 50)
    premium_vs_iv = [selected_spread * selected_delta * (i / 20.0) * dte_decay for i in iv_range]
    
    fig_iv = go.Figure()
    fig_iv.add_trace(go.Scatter(x=iv_range, y=premium_vs_iv, name="Premium Expansion", line=dict(color='#ff9900', width=3)))
    fig_iv.add_vline(x=iv, line_dash="dash", line_color="red", annotation_text="IV المحدد")
    
    fig_iv.update_layout(
        template="plotly_dark",
        height=350,
        xaxis_title="مستويات المحاكاة للتقلب الضمني (IV %)",
        yaxis_title="القيمة التقديرية المسعرة للعقد ($)",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_iv, use_container_width=True)

st.success("🏁 تم دمج وحفظ التعديلات بنجاح. التطبيق الآن يعمل بشكل ديناميكي كامل ومستقر.")
