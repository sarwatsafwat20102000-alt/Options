import streamlit as st
import yfinance as yf
import ta
import pandas as pd
import numpy as np

# 1. إعدادات الصفحة الفنية والتوافق مع الموبايل
st.set_page_config(
    page_title="Advanced AI Options Engine",
    layout="wide",
    initial_sidebar_state="collapsed"  # لتوفير مساحة رؤية كاملة على شاشة الموبايل
)

# تحسين مظهر الواجهة عبر CSS مخصص ليناسب الموبايل والألوان المتقدمة
st.markdown("""
<style>
    .reportview-container .main .block-container { max-width: 100%; padding-top: 1rem; padding-bottom: 1rem; }
    .stDataFrame { width: 100% !important; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Options Pricing & Strategy Engine")
st.write("نظام سحابي متقدم يربط التحليل الفني للتشارت بحسابات الأوبشن الأُسّية وتوجيه الاستراتيجيات تلقائياً.")

# --- 2. جلب البيانات الحية والتحليل الفني من التشارت ---
st.sidebar.header("📈 مدخلات السوق")
ticker_input = st.sidebar.text_input("أدخل رمز السهم (مثال: NVDA, AAPL, TSLA)", value="NVDA").upper()

@st.cache_data(ttl=300)  # تحديث البيانات تلقائياً كل 5 دقائق
def get_market_data(ticker):
    try:
        # جلب بيانات حركة السعر لآخر 6 أشهر
        df = yf.download(ticker, period="6mo", interval="1d")
        if df.empty: 
            return None, None, None
        
        # حساب المؤشرات الفنية مباشرة من التشارت
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        # حساب التقلب التاريخي الفعلي (HV) المستنتج من حركة السعر لضمان دقة مدخلات الـ IV
        df['Returns'] = df['Close'].pct_change()
        hv = float(df['Returns'].std() * np.sqrt(252) * 100)
        
        latest_price = float(df['Close'].iloc[-1])
        latest_rsi = float(df['RSI'].iloc[-1])
        
        return latest_price, latest_rsi, hv
    except Exception as e:
        return None, None, None

current_price, rsi_val, calculated_hv = get_market_data(ticker_input)

if current_price is None:
    st.error("⚠️ تعذر جلب بيانات السهم السحابية. يرجى التحقق من رمز السهم المكتوب (مثال: AAPL).")
    st.stop()

# --- 3. لوحة التحكم التفاعلية المدعومة ببيانات السوق الحية ---
st.sidebar.markdown("---")
st.sidebar.header("🎛️ ضبط متغيرات النموذج")

# إذا كان السهم يحتوي على تقلب محسوب نضعه كقيمة افتراضية، وإلا نضع 40%
default_iv = int(calculated_hv) if (calculated_hv and 5 <= calculated_hv <= 150) else 40

dte = st.sidebar.slider("الأيام حتى الانتهاء (Days to Expiry - DTE)", min_value=1, max_value=365, value=45)
iv = st.sidebar.slider("التقلب الضمني الحالي (ATM Implied Volatility - IV %)", min_value=5, max_value=150, value=default_iv)
ivp = st.sidebar.slider("نسبة مئوية التقلب الضمني (IV Percentile - IVP %)", min_value=0, max_value=100, value=13)

# --- 4. محرك توجيه الاستراتيجيات (محاكاة الصندوق الأزرق الذكي) ---
st.markdown("### 🔵 AI Strategy Coordinator")

# تحديد حالة السوق والاستراتيجية الموصى بها بناءً على الفلاتر المدخلة وصور الأنماط السابقة
if ivp < 20:
    market_condition = "QUIET PREMIUM CREEP (العقود رخيصة جداً والسوق هادئ)"
    recommended_strategy = "CALENDAR / DIAGONAL SPREAD (شراء عقود بعيدة وبيع قريبة للاستفادة من الاضمحلال أُسّياً)"
    strategy_color = "#00E5FF"  # أزرق فسفوري متناسق
else:
    if rsi_val > 65:
        market_condition = "BEARISH REVERSAL EXPECTED (السهم متضخم فنياً على التشارت ويقترب من قمة)"
        recommended_strategy = "CREDIT CALL SPREAD (استراتيجية ائتمانية للاستفادة من هبوط السعر أو ثباته)"
        strategy_color = "#FF3D00"  # أحمر تذكيري بالهبوط
    else:
        market_condition = "BULLISH MOMENTUM (السهم مستقر أو صاعد في مسار فني إيجابي)"
        recommended_strategy = "DEBIT CALL SPREAD (استراتيجية مدفوعة للاستفادة من الصعود مع تقليل المخاطرة)"
        strategy
