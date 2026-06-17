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
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة المحدث ---
translations = {
    "العربية": {
        "dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "معالجة ذكية للجداول والبيانات",
        "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", 
        "up": "اسحب أو اختر ملف PDF", "btn": "ابدأ العملية"
    },
    "English": {
        "dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Smart data processing system",
        "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)", 
        "up": "Drag or choose PDF file", "btn": "Start Process"
    },
    "Français": {
        "dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système de traitement de données",
        "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)", 
        "up": "Glissez ou choisissez un PDF", "btn": "Démarrer"
    },
    "اردو": {
        "dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "ڈیٹا پروسیسنگ کا جدید نظام",
        "tab1": "📊 پی ڈی ایف کو ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)", 
        "up": "فائل یہاں ڈریگ کریں", "btn": "شروع کریں"
    }
}

# --- 3. اختيار اللغة ---
selected_lang = st.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English", "Français", "اردو"], index=0)
lang = translations[selected_lang]

# --- 4. تنسيق النيون واللون الأبيض (الاحترافي) ---
st.markdown(f"""
<style>
    /* تطبيق اتجاه اللغة وتوحيد لون النصوص للأبيض */
    html, body, div, p, h1, h2, h3, span, label {{ 
        direction: {lang['dir']} !important; 
        text-align: {lang['align']} !important; 
        color: #ffffff !important; 
    }}
    
    .stApp {{ background-color: #07090e !important; }}

    /* القائمة المنسدلة (بيضاء بالكامل) */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{ 
        background-color: #ffffff !important; 
        color: #000000 !important; 
    }}
    [data-testid="stSelectbox"] div[data-baseweb="select"] span {{ color: #000000 !important; }}

    /* مستطيل الرفع المتوهج */
    [data-testid="stFileUploader"] {{
        background-color: #1a1a1a !important;
        border: 2px solid #30363d !important;
        border-radius: 15px !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border: 2px solid #00f2ff !important;
        box-shadow: 0 0 15px #00f2ff !important;
    }}

    /* الأزرار (نيون) */
    .stButton > button {{
        background: transparent !important;
        border: 2px solid #00f2ff !important;
        color: #ffffff !important;
        border-radius: 50px !important;
    }}
    .stButton > button:hover {{
        background: #00f2ff !important;
        color: #000 !important;
        box-shadow: 0 0 20px #00f2ff !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. الواجهة ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    file = st.file_uploader(lang["up"], type=["pdf"])
    if file and st.button(lang["btn"]):
        st.success("Processing...")

with tab2:
    img = st.file_uploader(lang["up"], type=["jpg", "png"])
    if img and st.button(lang["btn"]):
        st.info("Scanning...")
