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

# --- 3. القائمة المنسدلة (في أعلى قمة الصفحة) ---
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# --- 4. التنسيق (النيون الأخضر + القائمة العلوية) ---
st.markdown(f"""
<style>
    /* جعل القائمة في أعلى القمة */
    div[data-testid="stVerticalBlock"] {{ gap: 0rem; }}
    
    /* تنسيق القائمة المنسدلة باللون الأخضر */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{ 
        background-color: #000 !important; 
        border: 2px solid #2ea043 !important; 
        color: #2ea043 !important; 
    }}
    
    /* توحيد الألوان والنصوص */
    html, body, div, p, h1, h2, h3, span, label {{ 
        direction: {lang['dir']} !important; 
        text-align: {lang['align']} !important; 
        color: #ffffff !important; 
    }}
    
    .stApp {{ background-color: #07090e !important; }}

    /* مستطيل الرفع (توهج أخضر) */
    [data-testid="stFileUploader"] {{
        background-color: #0d0d0d !important;
        border: 2px solid #2ea043 !important;
        border-radius: 15px !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        box-shadow: 0 0 15px #2ea043 !important;
    }}

    /* أزرار النيون الأخضر */
    .stButton > button {{
        background: transparent !important;
        border: 2px solid #2ea043 !important;
        color: #2ea043 !important;
        border-radius: 50px !important;
    }}
    .stButton > button:hover {{
        background: #2ea043 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px #2ea043 !important;
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
