import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب أو اختر ملف PDF", "btn": "ابدأ العملية"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system for data", "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)", "up": "Drag or choose PDF file", "btn": "Start Process"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé pour données", "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)", "up": "Glissez ou choisissez un PDF", "btn": "Démarrer"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "ڈیٹا پروسیسنگ کا جدید نظام", "tab1": "📊 PDF کو ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)", "up": "فائل یہاں ڈریگ کریں", "btn": "شروع کریں"}
}

# --- 3. التنسيق الجذري (النيون + المحاذاة + القائمة المصغرة) ---
st.markdown("""
<style>
    /* القائمة المنسدلة مصغرة في الأعلى */
    div[data-testid="stSelectbox"] { width: 250px !important; margin-bottom: 20px !important; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] { background-color: #000 !important; border: 2px solid #2ea043 !important; color: #2ea043 !important; }
    
    /* خلفية وتوحيد الخطوط */
    .stApp { background-color: #07090e !important; color: #ffffff !important; }
    
    /* مستطيل الرفع نيون */
    [data-testid="stFileUploader"] { border: 2px solid #2ea043 !important; border-radius: 15px !important; background: #0d0d0d !important; }
    
    /* الأزرار نيون */
    .stButton > button { border: 2px solid #2ea043 !important; color: #ffffff !important; background: transparent !important; border-radius: 50px !important; }
    .stButton > button:hover { background: #2ea043 !important; box-shadow: 0 0 20px #2ea043 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. اختيار اللغة ---
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0)
lang = translations[selected_lang]

# تطبيق الاتجاه والمحاذاة ديناميكياً
st.markdown(f"""<style>.stApp {{ direction: {lang['dir']} !important; text-align: {lang['align']} !important; }}</style>""", unsafe_allow_html=True)

# --- 5. الواجهة ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    files = st.file_uploader(lang["up"], type=["pdf"], accept_multiple_files=True)
    if files and st.button(lang["btn"]):
        st.success("Processing...")

with tab2:
    img = st.file_uploader(lang["up"], type=["jpg", "png"])
    if img and st.button(lang["btn"]):
        st.info("Scanning...")
