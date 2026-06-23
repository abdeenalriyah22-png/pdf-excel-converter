import streamlit as st
import pandas as pd
import io
import pdfplumber
from PIL import Image
import pytesseract
import fitz
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات
translations = {
    "العربية": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF/CSV إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up1": "اسحب ملف PDF أو CSV هنا", "up2": "اسحب ملف PDF أو صورة هنا", "btn": "بدء المعالجة", "copy": "📋 نسخ النص بالكامل"},
    "English": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system", "tab1": "📊 PDF/CSV to Excel", "tab2": "🔍 OCR Text", "up1": "Upload PDF or CSV", "up2": "Upload PDF or Image", "btn": "Start", "copy": "📋 Copy All Text"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English"], index=0, key="lang_selector")
lang = translations[selected_lang]

# --- التصميم الشامل ---
st.markdown(f"""
<style>
    #MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stSelectbox"] {{ position: fixed !important; top: 15px !important; {lang['pos']}: 20px !important; z-index: 9999 !important; width: 150px !important; }}
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']} !important; }}
    .main-container {{ max-width: 900px; margin: 0 auto; padding-top: 100px !important; }}
    h1 {{ text-align: {lang['align']} !important; color: #202124 !important; text-shadow: 0 0 10px #28a745, 0 0 20px #28a745 !important; }}
    [data-testid="stFileUploader"] {{ border: 2px solid #28a745 !important; border-radius: 12px !important; }}
</style>
""", unsafe_allow_html=True)

# محتوى الصفحة
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

    with tab1:
        files = st.file_uploader(lang["up1"], type=["pdf", "csv"], accept_multiple_files=True)
        if files:
            for f in files:
                if st.button(f"{lang['btn']}", key=f"btn1_{f.name}"):
                    output = io.BytesIO()
                    if f.name.endswith('.pdf'):
                        with pdfplumber.open(f) as pdf:
                            all_rows = []
                            for page in pdf.pages:
                                table = page.extract_table()
                                if table: all_rows.extend(table)
                            df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
                            df.to_excel(output, index=False)
                    else:
                        pd.read_csv(f).to_excel(output, index=False)
                    st.download_button("📥 تحميل الإكسل", output.getvalue(), f"{f.name.split('.')[0]}.xlsx")

    with tab2:
        file = st.file_uploader(lang["up2"], type=["jpg", "png", "pdf"])
        if file and st.button(f"{lang['btn']}", key="btn2"):
            # منطق الـ OCR كما هو سابقاً
            pass
