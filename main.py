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
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide")

# --- 2. قاموس الترجمة ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "معالجة ذكية للجداول والبيانات", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب أو اختر ملف PDF", "btn": "ابدأ العملية"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Smart data processing system", "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)", "up": "Drag or choose PDF file", "btn": "Start Process"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système de traitement de données", "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)", "up": "Glissez ou choisissez un PDF", "btn": "Démarrer"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "ڈیٹا پروسیسنگ کا جدید نظام", "tab1": "📊 پی ڈی ایف کو ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)", "up": "فائل یہاں ڈریگ کریں", "btn": "شروع کریں"}
}

# --- 3. التنسيق (رفع القائمة للأعلى + نيون أخضر) ---
st.markdown("""
<style>
    /* رفع المحتوى للأعلى مباشرة */
    .block-container { padding-top: 0rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }

    /* تنسيق القائمة المنسدلة (الأخضر النيوني) */
    [data-testid="stSelectbox"] { margin-top: -20px !important; }
    [data-testid="stSelectbox"] div[data-baseweb="select"] { 
        background-color: #000 !important; 
        border: 2px solid #2ea043 !important; 
        color: #2ea043 !important; 
    }
    
    /* توحيد النصوص باللون الأبيض */
    html, body, div, p, h1, h2, h3, span, label { 
        color: #ffffff !important; 
    }
    
    .stApp { background-color: #07090e !important; }

    /* مستطيل الرفع */
    [data-testid="stFileUploader"] {
        border: 2px solid #2ea043 !important;
        border-radius: 15px !important;
    }
    
    /* الأزرار */
    .stButton > button {
        border: 2px solid #2ea043 !important;
        color: #2ea043 !important;
        border-radius: 50px !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. القائمة المنسدلة (أول عنصر في الكود) ---
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0)
lang = translations[selected_lang]

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
