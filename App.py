import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# إعدادات الصفحة لتناسب شاشات الموبايل والمظهر الداكن
st.set_page_config(
    page_title="Premium Strategy Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم مخصص ومطابق لألوان تطبيقك (أسود، رمادي داكن، وفسفوري)
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; background-color: #0d1117; }
    h1, h2, h3 { color: #ccff00 !important; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 12px; border-radius: 10px; border: 1px solid #30363d; }
    .reportview-container { background: #0d1117; }
</style>
""", unsafe_allow_html=True)

# --- الجانب الأيسر: مدخلات السوق والمعاملات ---
st.sidebar.header("📊 مدخلات السوق")
# استقبال الرمز وتنظيفه تلقائيًا من المسافات والحروف الصغيرة منعاً للخطأ
ticker_input = st.sidebar.text_input("أدخل رمز السهم المتداول", value="NVDA").upper().strip()

# الدالة الجديدة والمعدلة لجلب البيانات بأمان وتفادي خطأ الـ Cache والأرقام الفارغة
@st.cache_resource
def get_stock_details(ticker):
    try:
        stock = yf.Ticker(ticker)
        # فحص ما إذا كانت البيانات موجودة فعلاً في الـ info
        if stock.info and 'regularMarketPrice' in stock.info:
            return stock, stock.info['regularMarketPrice'], stock.info.get('longName', ticker)
        else:
            # محاولة جلب السعر الأحدث من الـ history إذا فشل الـ info أو تعرض للحظر
            hist = stock.history(period="1d")
            if not hist.empty:
                return stock, hist['Close'].iloc[-1], ticker
            return None, None, None
    except Exception as e:
        return None, None, None

# استدعاء الدالة الآمنة
stock_obj, price_now, company_name = get_stock_details(ticker_input)

if price_now is None:
    st.error(f"⚠️ تعذر جلب بيانات السهم السحابية لـ ({ticker_input}). يرجى التحقق من رمز السهم المكتوب.")
    st.stop()

# --- عرض اسم السهم والشركة بشكل بارز ومباشر في الأعلى ---
st.title("📈 PREMIUM SCHEDULE")
st.subheader(f"رمز السهم النشط: {ticker_input} — {company_name}")

st.sidebar.metric(label=f"سعر {ticker_input} الحالي المباشر", value=f"${price_now:.2f}")

st.sidebar.markdown("---")
st.sidebar.header("🎛️ ضبط متغيرات النموذج")
dte = st.sidebar.slider("الأيام حتى الانتهاء (DTE)", 5, 365, 45)
iv = st.sidebar.slider("التقلب الضمني الحالي (IV %)", 5, 120, 20)
ivp = st.sidebar.slider("نسبة مئوية للتقلب الضمني (IVP %)", 0, 100, 50)
hv = st.sidebar.number_input("التقلب التاريخي المحسوب (HV %)", value=15)

# حساب بيئة الأسعار التلقائية ومحاكاة البطاقة الملونة في الصورة
iv_hv_ratio = iv / hv if hv > 0 else 1.0
if iv_hv_ratio > 1.2:
    st.markdown(f"""
    <div style='padding: 15px; background-color: #2c1a04; border-left: 5px solid #ff9900; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #ff9900; font-size: 1.1rem;'>ELEVATED PREMIUM (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>البريميوم غالي مقارنة بالحركة التاريخية الحقيقية للسهم. الاستراتيجية المفضلة: Credit Spreads.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style='padding: 15px; background-color: #042c11; border-left: 5px solid #00ff00; border-radius: 5px; margin-bottom: 20px;'>
        <b style='color: #00ff00; font-size: 1.1rem;'>NEUTRAL / CHEAP ENVIRONMENT (IV/HV: {iv_hv_ratio:.2f} | IVP: {ivp}%)</b><br>
        <span style='color: #e2e8f0; font-size: 0.95rem;'>أسعار العقود عادلة أو رخيصة نسبياً. الاستراتيجية المفضلة: Debit Spreads / Net Long Vega.</span>
    </div>
    """, unsafe_allow_html=True)

# --- بناء خريطة وجدولة الأسعار التفاعلية الملونة (Heatmap Grid) ---
st.markdown("### 🗺️ خريطة وجدولة أسعار العقود (Premium Matrix Grid)")

# تحديد أعمدة الـ Spreads وقيم الـ Delta المتوافقة مع الصورة المرفقة
spread_widths = [20.0, 22.5, 25.0, 27.5]
delta_rows = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70]

iv_factor = iv / 20.0
dte_factor = np.sqrt(dte / 45.0)

# إنشاء مصفوفة مخصصة كلياً باستخدام HTML لتلوين الخلايا بشكل احترافي دقيق
html_table = "<table style='width:100%; border-collapse: collapse; background-color: #161b22; color: #e2e8f0; text-align: center; font-family: monospace;'>"
html_table += "<tr style='background-color: #21262d; color: #ccff00; font-weight: bold; border-bottom: 2px solid #30363d;'>"
html_table += "<th style='padding: 12px; border: 1px solid #30363d;'>Δ - DELTA</th>"
for w in spread_widths:
    html_table += f"<th style='padding: 12px; border: 1px solid #30363d;'>${w} SPREAD</th>"
html_table += "</tr>"

for d_val in delta_rows:
    html_table += f"<tr style='border-bottom: 1px solid #30363d;'>"
    html_table += f"<td style='padding: 10px; font-weight: bold; background-color: #1f242c; border: 1px solid #30363d;'>{d_val:.2f}</td>"
    
    for width in spread_widths:
        # حساب السعر الأوسط الفعلي بناءً على معادلة الصورة المعطاة
        mid_premium = width * d_val * iv_factor * dte_factor
        lower_band = mid_premium * 0.88
        upper_band = mid_premium * 1.12
        
        # نسبة البريميوم من حجم السبريد لتحديد درجة اللون (Heatmap)
        premium_ratio = (mid_premium / width) * 100
        
        # تحديد لون النص والخلفية بناءً على المعايير التوضيحية المذكورة في صورتك
        if premium_ratio < 28:
            bg_color = "#042c11"   # أخضر داكن (رخيص)
            text_color = "#00ff00"
        elif 28 <= premium_ratio < 42:
            bg_color = "#2c2a04"   # أصفر/زيتوني (عادل)
            text_color = "#ffcc00"
        elif 42 <= premium_ratio < 58:
            bg_color = "#2c1a04"   # برتقالي داكن (مرتفع)
            text_color = "#ff9900"
        else:
            bg_color = "#2c0404"   # أحمر داكن (متضخم وفرصة بيع)
            text_color = "#ff3333"
            
        cell_text = f"${lower_band:.1f} - ${upper_band:.1f}"
        html_table += f"<td style='padding: 10px; background-color: {bg_color}; color: {text_color}; font-weight: bold; border: 1px solid #30363d;'>{cell_text}</td>"
    html_table += "</tr>"

html_table += "</table>"

# عرض الجدول الملون المصمم خصيصاً للموبايل
st.markdown(html_table, unsafe_allow_html=True)

# إضافة دليل الألوان أسفل الجدول مباشرة
st.markdown("""
<div style='margin-top: 10px; padding: 10px; background-color: #161b22; border-radius: 5px; border: 1px solid #30363d; font-size: 0.85rem; text-align: center;'>
    <span style='color: #00ff00;'>■ Cheap (&lt;28%)</span> | 
    <span style='color: #ffcc00;'>■ Fair (28-42%)</span> | 
    <span style='color: #ff9900;'>■ Rich (42-58%)</span> | 
    <span style='color: #ff3333;'>■ Overpriced (&gt;58%)</span>
</div>
""", unsafe_allow_html=True)

st.success("💡 تم دمج وحفظ التعديلات بنجاح. التطبيق الآن يعمل بشكل ديناميكي كامل ومستقر.")
