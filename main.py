import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات (شامل الفرنسية)
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب ملف PDF هنا", "btn": "بدء المعالجة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system", "tab1": "📊 PDF to Excel", "tab2": "🔍 OCR Text", "up": "Upload PDF", "btn": "Start"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé", "tab1": "📊 PDF vers Excel", "tab2": "🔍 OCR Texte", "up": "Charger PDF", "btn": "Démarrer"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "جدید کلاؤڈ سسٹم", "tab1": "📊 ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالیں", "up": "فائل اپ لوڈ کریں", "btn": "شروع"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# التصميم النهائي (إخفاء كل أزرار النظام + خلفية فاتحة + نيون)
st.markdown(f"""
<style>
    /* إخفاء القلم، القائمة، والمشاركة من ستريمليت */
    #MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{
        display: none !important;
        visibility: hidden !important;
    }}
    
    /* الخلفية الفاتحة والنصوص */
    html, body, .stApp {{ 
        direction: {lang['dir']} !important; 
        text-align: {lang['align']} !important; 
        background-color: #F8F9FA !important; 
        color: #202124 !important; 
    }}
    
    /* المستطيل النيون */
    [data-testid="stFileUploader"] {{ 
        border: 2px solid #1A73E8 !important; 
        border-radius: 15px !important; 
        background: #FFFFFF !important;
        box-shadow: 0 0 10px rgba(26, 115, 232, 0.2) !important;
    }}
    
    /* تذييل الحقوق */
    .footer {{ 
        position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; 
        padding: 10px; background: #F8F9FA; color: #1A73E8; font-weight: bold; 
        border-top: 1px solid #1A73E8; z-index: 999;
    }}
</style>
""", unsafe_allow_html=True)

# واجهة البرنامج
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

# منطق المعالجة (كما هو تماماً)
with tab1:
    files = st.file_uploader(lang["up"], type=["pdf"], accept_multiple_files=True)
    if files:
        for f in files:
            if st.button(f"{lang['btn']} {f.name}"):
                dfs = tabula.read_pdf(f, pages='all', multiple_tables=True, lattice=True)
                if dfs:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, df in enumerate(dfs): df.to_excel(writer, index=False, sheet_name=f'Sheet{i+1}')
                    st.success("تم!")
                    st.download_button("📥 تحميل", output.getvalue(), f"{f.name}.xlsx")

with tab2:
    img = st.file_uploader(lang["up"], type=["jpg", "png", "pdf"])
    if img and st.button(lang["btn"]):
        full_text = pytesseract.image_to_string(Image.open(img), lang='ara+eng')
        st.text_area("النص:", value=full_text, height=300)

st.markdown('<div class="footer">المحاسب الذكي Pro | جميع الحقوق محفوظة © 2026</div>', unsafe_allow_html=True)
