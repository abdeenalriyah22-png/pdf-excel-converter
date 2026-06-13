import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide")

# --- 2. قاموس الترجمة ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "menu": "🛠️ الأدوات", "excel": "📊 تحويل PDF إلى إكسيل", "ocr": "🔍 OCR", "merge": "📂 دمج PDF", "delete": "✂️ حذف صفحات", "reorder": "🔀 ترتيب الصفحات", "sign": "✍️ التوقيع"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "menu": "🛠️ Tools", "excel": "📊 PDF to Excel", "ocr": "🔍 OCR", "merge": "📂 Merge PDF", "delete": "✂️ Delete Pages", "reorder": "🔀 Reorder Pages", "sign": "✍️ Sign"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "menu": "🛠️ ٹولز", "excel": "📊 پی ڈی ایف ٹو ایکسل", "ocr": "🔍 OCR", "merge": "📂 ضم پی ڈی ایف", "delete": "✂️ صفحات حذف کریں", "reorder": "🔀 ترتیب دیں", "sign": "✍️ دستخط"}
}

# --- 3. Sidebar مع التحكم باللغة والمظهر ---
with st.sidebar:
    selected_lang = st.selectbox("🌐 Language", ["العربية", "English", "اردو"])
    lang = translations[selected_lang]
    
    theme = st.radio("🌓 Theme", ["Dark Mode 🌑", "Light Mode ☀️"])
    
    st.markdown("---")
    current_tool = st.radio(lang["menu"], [lang["excel"], lang["ocr"], lang["merge"], lang["delete"], lang["reorder"], lang["sign"]])

# --- 4. تطبيق التنسيق (تم إصلاح أقواس الـ CSS هنا) ---
theme_bg = "#0b0f19" if theme == "Dark Mode 🌑" else "#ffffff"
theme_text = "#f8fafc" if theme == "Dark Mode 🌑" else "#000000"

st.markdown(f"""
<style>
    /* تطبيق اتجاه الصفحة والخط */
    html, body, [class*="st-emotion-cache"], div {{
        direction: {lang["dir"]} !important;
        text-align: {lang["align"]} !important;
        font-family: 'Cairo', sans-serif !important;
    }}
    .stApp {{
        background-color: {theme_bg} !important;
        color: {theme_text} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 15, 26, 0.95) !important;
    }}
    h1 {{ color: #00f2fe !important; }}
</style>
""", unsafe_allow_html=True)

# --- 5. عرض العنوان ---
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

# --- 6. المنطق البرمجي (مثال لأداة واحدة) ---
if current_tool == lang["excel"]:
    st.subheader(lang["excel"])
    uploaded_file = st.file_uploader("ارفع ملف PDF", type=["pdf"])
    if uploaded_file and st.button("بدء التحويل"):
        st.write("جاري المعالجة...")
        # هنا تضع كود tabula الخاص بك
elif current_tool == lang["ocr"]:
    st.subheader(lang["ocr"])
    # كود الـ OCR
# يمكنك تكملة باقي الأدوات بنفس الطريقة هنا...

# --- 7. الإعلانات (مخفية في الـ sidebar) ---
components.html("<script async src='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781'></script>", height=0)
