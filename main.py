import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Smart Accountant Pro", page_icon="📊", layout="wide")

# --- 2. قاموس الترجمة المحدث ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "معالجة ذكية للجداول والبيانات", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب أو اختر ملف PDF", "btn": "ابدأ العملية"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Smart data processing system", "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)", "up": "Drag or choose PDF file", "btn": "Start Process"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système de traitement de données", "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)", "up": "Glissez ou choisissez un PDF", "btn": "Démarrer"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "ڈیٹا پروسیسنگ کا جدید نظام", "tab1": "📊 پی ڈی ایف کو ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)", "up": "فائل یہاں ڈریگ کریں", "btn": "شروع کریں"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"])
lang = translations[selected_lang]

# --- 3. تصميم النيون الاحترافي (CSS) ---
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* الإعدادات العامة */
    html, body {{ direction: {lang['dir']} !important; background: #050505 !important; color: #fff !important; }}
    
    /* مستطيل الرفع المتوهج بالنيون */
    [data-testid="stFileUploader"] {{
        border: 2px solid #30363d !important;
        border-radius: 15px !important;
        padding: 20px !important;
        transition: 0.4s !important;
        background: #0d0d0d !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border: 2px solid #00f2ff !important;
        box-shadow: 0 0 15px #00f2ff, inset 0 0 5px #00f2ff !important;
    }}

    /* الأزرار الاحترافية */
    .stButton > button {{
        width: 100%;
        background: transparent !important;
        border: 1px solid #00f2ff !important;
        color: #00f2ff !important;
        border-radius: 50px !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        transition: 0.3s !important;
    }}
    .stButton > button:hover {{
        background: #00f2ff !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00f2ff !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. الواجهة ---
st.markdown(f"<h1 style='text-align: center; color: #00f2ff;'>{lang['title']}</h1><p style='text-align: center;'>{lang['subtitle']}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    st.markdown(f"<i class='fa-solid fa-file-pdf' style='font-size:30px; color:#00f2ff;'></i>", unsafe_allow_html=True)
    file = st.file_uploader(lang["up"], type=["pdf"])
    if file and st.button(lang["btn"]):
        st.success("Processing...")

with tab2:
    st.markdown(f"<i class='fa-solid fa-camera' style='font-size:30px; color:#00f2ff;'></i>", unsafe_allow_html=True)
    img = st.file_uploader(lang["up"], type=["jpg", "png"])
    if img and st.button(lang["btn"]):
        st.info("Scanning...")
