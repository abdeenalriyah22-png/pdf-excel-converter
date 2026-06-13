import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# --- قاموس الترجمة ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "menu": "🛠️ الأدوات الذكية", "theme": "🌓 المظهر", "excel": "📊 تحويل PDF إلى إكسيل", "ocr": "🔍 استخراج النصوص (OCR)", "merge": "📂 دمج ملفات PDF", "delete": "✂️ حذف صفحات", "reorder": "🔀 إعادة ترتيب الصفحات", "sign": "✍️ التوقيع الإلكتروني", "motto": "الفصل في الذمة.. الوصل في الأمانة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "menu": "🛠️ Smart Tools", "theme": "🌓 Theme", "excel": "📊 PDF to Excel", "ocr": "🔍 Smart OCR", "merge": "📂 Merge PDF", "delete": "✂️ Delete Pages", "reorder": "🔀 Reorder Pages", "sign": "✍️ Digital Sign", "motto": "Separation of liability... connection in trust"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "menu": "🛠️ سمارٹ ٹولز", "theme": "🌓 تھیم", "excel": "📊 پی ڈی ایف ٹو ایکسل", "ocr": "🔍 OCR", "merge": "📂 ضم پی ڈی ایف", "delete": "✂️ صفحات حذف کریں", "reorder": "🔀 ترتیب دیں", "sign": "✍️ دستخط", "motto": "الفصل في الذمة.. الوصل في الأمانة"}
}

# --- القائمة الجانبية ---
with st.sidebar:
    selected_lang = st.selectbox("🌐 اللغة / Language", ["العربية", "English", "اردو"])
    lang = translations[selected_lang]
    theme_choice = st.radio(lang["theme"], ["Dark Mode 🌑", "Light Mode ☀️"])
    
    st.markdown("---")
    current_tool = st.radio(lang["menu"], [lang["excel"], lang["ocr"], lang["merge"], lang["delete"], lang["reorder"], lang["sign"]])

# --- المنطق البرمجي للألوان ---
is_dark = ("Dark" in theme_choice)
bg_app = "#0b0f19" if is_dark else "#ffffff"
text_app = "#f8fafc" if is_dark else "#000000"
bg_sidebar = "#0f172a" if is_dark else "#f1f5f9"

# --- التنسيق الاحترافي (مُصحح) ---
st.markdown(f"""
<style>
    /* الإعدادات العامة */
    html, body, [class*="st-emotion-cache"] {{
        direction: {lang["dir"]} !important;
        text-align: {lang["align"]} !important;
        font-family: 'Cairo', sans-serif !important;
    }}
    .stApp {{ background-color: {bg_app} !important; color: {text_app} !important; }}
    
    /* القائمة الجانبية */
    [data-testid="stSidebar"] {{ background-color: {bg_sidebar} !important; }}
    [data-testid="stSidebar"] label {{ font-size: 18px !important; font-weight: bold !important; color: {text_app} !important; }}
    
    /* العنوان */
    h1 {{ color: #00f2fe !important; text-align: center; }}
    
    /* البطاقات */
    .custom-card {{ background: {('#1e293b' if is_dark else '#e2e8f0')}; padding: 20px; border-radius: 15px; border: 1px solid #00f2fe; }}
</style>
""", unsafe_allow_html=True)

# --- عرض المحتوى ---
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

if current_tool == lang["excel"]:
    st.markdown(f"<div class='custom-card'><h3>{lang['excel']}</h3></div>", unsafe_allow_html=True)
    st.file_uploader("اختر ملفات PDF", type=["pdf"], accept_multiple_files=True)

elif current_tool == lang["ocr"]:
    st.markdown(f"<div class='custom-card'><h3>{lang['ocr']}</h3></div>", unsafe_allow_html=True)
    st.file_uploader("اختر ملف صورة أو PDF", type=["pdf", "png", "jpg"])

# --- التذييل ---
st.markdown(f"<div style='text-align:center; padding:50px; color:#94a3b8;'>{lang['motto']} | 2026 ©</div>", unsafe_allow_html=True)
