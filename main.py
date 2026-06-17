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

# --- 2. قاموس الترجمة ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right",
        "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات",
        "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)",
        "uploader_pdf": "اسحب ملفات الـ PDF هنا", "uploader_ocr": "ارفع صورة أو ملف PDF",
        "btn_convert": "بدأ التحويل: ", "btn_ocr": "🚀 تشغيل الذكاء الاصطناعي",
        "success": "🚀 اكتمل التحويل!", "download": "📥 تحميل الملف"
    },
    "English": {
        "direction": "ltr", "align": "left",
        "title": "📊 Smart Accountant Pro", "subtitle": "Advanced system for data processing",
        "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)",
        "uploader_pdf": "Drag and drop PDF files here", "uploader_ocr": "Upload image or PDF file",
        "btn_convert": "Start Converting: ", "btn_ocr": "🚀 Launch AI",
        "success": "🚀 Conversion complete!", "download": "📥 Download file"
    },
    "Français": {
        "direction": "ltr", "align": "left",
        "title": "📊 Comptable Intelligent Pro", "subtitle": "Système avancé pour le traitement des données",
        "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)",
        "uploader_pdf": "Glissez et déposez vos fichiers PDF", "uploader_ocr": "Téléchargez une image ou un PDF",
        "btn_convert": "Commencer la conversion: ", "btn_ocr": "🚀 Lancer l'IA",
        "success": "🚀 Conversion réussie!", "download": "📥 Télécharger le fichier"
    }
}

# --- 3. اختيار اللغة ---
selected_lang = st.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English", "Français"], index=0)
lang = translations[selected_lang]

# --- 4. التنسيق (النيون الواضح) ---
st.markdown(f"""
<style>
    html, body, [class*="st-emotion-cache"] {{ 
        direction: {lang['direction']} !important; 
        text-align: {lang['align']} !important; 
        background-color: #07090e !important; 
        color: #e6edf3 !important; 
    }}
    
    /* قائمة اللغات بيضاء */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{ 
        background-color: #ffffff !important; 
        color: #000000 !important; 
    }}

    /* أزرار النيون */
    .stButton > button {{ 
        background: #000 !important; 
        color: #fff !important; 
        border: 2px solid #2ea043 !important; 
        box-shadow: 0 0 10px #2ea043 !important; 
        border-radius: 8px !important; 
    }}
    .stButton > button:hover {{ 
        background: #2ea043 !important; 
        box-shadow: 0 0 20px #2ea043 !important; 
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. الواجهة ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], accept_multiple_files=True)
    if files and st.button(lang["btn_convert"]):
        st.success(lang["success"])

with tab2:
    img = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "pdf"])
    if img and st.button(lang["btn_ocr"]):
        st.info("Processing...")
