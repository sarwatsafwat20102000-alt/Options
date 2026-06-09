import streamlit as st
import yfinance as yf
import ta
import pandas as pd
import numpy as np
import requests
from scipy.stats import norm
import plotly.graph_objects as go
from datetime import datetime

# 1. إعدادات شاشة الموبايل والواجهة العريضة
st.set_page_config(
    page_title="Core AI Options Analytics Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تجميل التصميم ومحاذاة النصوص البرمجية لتبدو احترافية على الهاتف
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 2.2rem !important; color: #1E88E5; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 8px; border: 1px solid #262730; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Deep-Quant AI Options & Strategy Engine")
st.write("محرك كمّي متقدم لتحليل الجوانب اليونانية (Greeks)، والتقلبات الضمنية، ورسم خرائط الأرباح والخسائر الحية.")

# --- دالة الحماية لضمان جلب البيانات وتفادي الحظر المؤقت ---
def get_backup_price(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5).json()
        return float(response['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return None

@st.cache_data(ttl=120)
def fetch_complete_market_data(ticker):
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        stock = yf.Ticker(ticker, session=session)
        
        # جلب البيانات التاريخية للتشارت
        df = stock.history(period="6mo", interval="1d")
        if df.empty:
            return None, None, None, None
            
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['Returns'] = df['Close'].pct_change()
        hv = float(df['Returns'].std() * np.sqrt(252) * 100)
        
        latest_price = float(df['Close'].iloc[-1])
        latest_rsi = float(df['RSI'].iloc[-1]) if not np.isnan(df['RSI'].iloc[-1]) else 50.0
        
        return latest_price, latest_rsi, hv, stock
    except:
        bp = get_backup_price(ticker)
        if bp:
            return bp, 50.0, 35.0, None
        return None, None, None, None

# --- 2. التحكم في المدخلات من القائمة الجانبية ---
st.sidebar.header("📈 مراقبة الرمز")
ticker_input = st.sidebar.text_input("رمز السهم الأساسي", value="NVDA").upper()

current_price, rsi_val, calculated_hv, stock_obj = fetch_complete_market_data(ticker_input)

if current_price is None:
    st.error("⚠️ تعذر الاتصال بمزود البيانات الحية. يرجى التأكد من الرمز وإعادة المحاولة.")
    st.stop()

# عرض السعر والمؤشرات الرئيسية فوراً كـ Dynamic Cards
st.sidebar.metric(label="السعر الحالي الحقيقي", value=f"${current_price:.2f}")
st.sidebar.metric(label="التقلب التاريخي المستنتج (HV)", value=f"{calculated_hv:.2f}%")

st.sidebar.markdown("---")
st.sidebar.header("🎛️ المعاملات والبيئة الحسابية")
default_iv = int(calculated_hv) if (5 <= calculated_hv <= 150) else 40
iv = st.sidebar.slider("التقلب الضمني المتوقع (IV %)", 5, 150, default_iv) / 100.0
dte = st.sidebar.slider("الأيام المتبقية للانتهاء (DTE)", 1, 365, 45)
r = st.sidebar.slider("معدل الفائدة الخالي من المخاطر %", 0.0, 6.0, 5.25) / 100.0

# --- 3. محرك رياضيات Black-Scholes لحساب الـ Greeks ديناميكياً ---
def calculate_greeks(S, K, T, r, sigma, option_type="call"):
    if T <= 0: T = 0.0001
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
        theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = (S * np.sqrt(T) * norm.pdf(d1)) / 100
    return price, delta, gamma, theta, vega

# --- 4. عرض خريطة التشارت الفنية الديناميكية (Plotly Chart) ---
st.markdown("### 📊 الخريطة الفنية وهيكل حركة السعر")
if stock_obj is not None:
    hist_df = stock_obj.history(period="3mo")
    fig = go.Figure(data=[go.Candlestick(x=hist_df.index,
                    open=hist_df['Open'], high=hist_df['High'],
                    low=hist_df['Low'], close=hist_df['Close'], name='السعر')])
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# --- 5. الذكاء الاصطناعي وتوليد الاستراتيجية والمصفوفة الكمية ---
st.markdown("### 🔵 AI Strategy Coordinator & Real-time Greeks")

# تحديد strike قريب من السعر الحالي تلقائياً لجعل الحساب واقعي ومطاطي
strike_atm = round(current_price)

T_years = dte / 365.0
c_price, c_del, gamma, c_th, vega = calculate_greeks(current_price, strike_atm, T_years, r, iv, "call")
p_price, p_del, _, p_th, _ = calculate_greeks(current_price, strike_atm, T_years, r, iv, "put")

# تحديد التوجيه الاستراتيجي الشامل بناءً على الـ RSI والتقلبات
if iv < 0.25:
    rec_strat = "Long Straddle / Calendar Spread (العقود رخيصة والتقلب منخفض)"
    strat_desc = "شراء عقود Call و Put بنفس سعر التنفيذ للاستفادة من أي انفجار سعري قادم."
else:
    if rsi_val > 65:
        rec_strat = "Bear Call Credit Spread (السهم متضخم فنياً)"
        strat_desc = "بيع عقد Call قريب وشراء عقد Call أبعد لتجميع الأرباح من ثبات السعر أو هبوطه."
    else:
        rec_strat = "Bull Debit Call Spread (صعود مستقر)"
        strat_desc = "شراء عقد Call عند السعر وبيع عقد أبعد لتقليل تكلفة الدخول الإجمالية."

st.info(f"**الاستراتيجية المقترحة ديناميكياً:** {rec_strat}\n\n*آلية العمل:* {strat_desc}")

# عرض مصفوفة المعاملات المؤثرة واليونانيات (Greeks Table)
st.markdown("#### 🎯 مصفوفة قياس المخاطر الفورية لعقود الـ ATM (Strike: ${})".format(strike_atm))
greeks_data = {
    "نوع العقد": ["Call Option 🍏", "Put Option 🍎"],
    "السعر النظري (BS)": [f"${c_price:.2f}", f"${p_price:.2f}"],
    "Delta (الاتجاه)": [f"{c_del:.3f}", f"{p_del:.3f}"],
    "Gamma (التسارع)": [f"{gamma:.4f}", f"{gamma:.4f}"],
    "Theta (الاضمحلال الزمني)": [f"{c_th:.3f}", f"{p_th:.3f}"],
    "Vega (الحساسية للتقلب)": [f"{vega:.3f}", f"{vega:.3f}"]
}
st.table(pd.DataFrame(greeks_data))

# --- 6. رسم محاكاة منحنى الأرباح والخسائر (Dynamic P&L Simulation Chart) ---
st.markdown("#### 📈 محاكاة منحنى الأرباح والخسائر (P&L Graph)")
price_range = np.linspace(strike_atm * 0.8, strike_atm * 1.2, 50)

if "Spread" in rec_strat or "Bear" in rec_strat:
    # محاكاة لـ Spread مبسط
    pnl_profile = [calculate_greeks(p, strike_atm, T_years, r, iv, "call")[0] - c_price for p in price_range]
else:
    # محاكاة لشراء عقد Call فردي
    pnl_profile = [max(0, p - strike_atm) - c_price for p in price_range]

fig_pnl = go.Figure()
fig_pnl.add_trace(go.Scatter(x=price_range, y=pnl_profile, mode='lines', name='P&L عند الانتهاء', line=dict(color='#00FF00', width=3)))
fig_pnl.add_hline(y=0, line_dash="dash", line_color="white")
fig_pnl.update_layout(template="plotly_dark", height=300, xaxis_title="سعر السهم عند الانتهاء", yaxis_title="الربح / الخسارة ($)")
st.plotly_chart(fig_pnl, use_container_width=True)
