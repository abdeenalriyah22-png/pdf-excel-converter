import streamlit as st
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات (تم تحديث الألوان للتماشي مع التصميم)
translations = {
    "العربية": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب ملف PDF هنا", "btn": "بدء المعالجة"},
    "English": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system", "tab1": "📊 PDF to Excel", "tab2": "🔍 OCR Text", "up": "Upload PDF", "btn": "Start"}
}
# (يمكنك إضافة باقي اللغات بنفس الطريقة)
lang = translations["العربية"]

# --- التصميم الاحترافي (مستوحى من Jazerat) ---
st.markdown(f"""
<style>
    /* الألوان الأساسية */
    :root {{ --main-purple: #4b0082; --light-bg: #f4f4f4; }}
    
    #MainMenu, header, footer {{ display: none !important; }}
    
    .stApp {{ background-color: #FFFFFF !important; }}
    
    /* شريط العنوان (Header) */
    .header-style {{ 
        background-color: var(--main-purple); 
        color: white; 
        padding: 20px; 
        text-align: center; 
        margin-bottom: 30px;
        border-bottom: 5px solid #ffcc00; /* لمسة ذهبية */
    }}
    
    /* تنسيق الحاوية */
    .main-container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
    
    /* المستطيل: إطار بنفسجي أنيق */
    [data-testid="stFileUploader"] {{ 
        border: 2px solid var(--main-purple) !important; 
        border-radius: 10px !important; 
        background-color: #f9f9f9 !important;
    }}
    
    /* تنسيق الأزرار (البنفسجي) */
    div.stButton > button {{ 
        background-color: var(--main-purple) !important; 
        color: white !important; 
        border-radius: 5px !important; 
        border: none !important;
        padding: 10px 25px !important;
    }}
    div.stButton > button:hover {{ background-color: #3d0066 !important; }}
    
    /* الفوتر */
    .footer {{ 
        text-align: center; 
        padding: 40px; 
        color: var(--main-purple); 
        font-weight: bold; 
    }}
</style>
""", unsafe_allow_html=True)

# تطبيق الهيدر البنفسجي
st.markdown('<div class="header-style"><h1>المحاسب الذكي Pro</h1><p>النظام السحابي المطور لمعالجة الجداول</p></div>', unsafe_allow_html=True)

# المحتوى
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

    with tab1:
        files = st.file_uploader(lang["up"], type=["pdf"], accept_multiple_files=True)
        if files and st.button(lang["btn"]):
             st.success("جاري المعالجة...")
             
    with tab2:
        file = st.file_uploader(lang["up"], type=["jpg", "png", "pdf"])
        if file and st.button(lang["btn"]):
             st.info("تم استخراج النص.")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">جميع الحقوق محفوظة © 2026</div>', unsafe_allow_html=True)
