import streamlit as st
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات
translations = {
    "العربية": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب ملف PDF هنا", "btn": "بدء المعالجة"},
    "English": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system", "tab1": "📊 PDF to Excel", "tab2": "🔍 OCR Text", "up": "Upload PDF", "btn": "Start"},
    "Français": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé", "tab1": "📊 PDF vers Excel", "tab2": "🔍 OCR Texte", "up": "Charger PDF", "btn": "Démarrer"},
    "اردو": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "جدید کلاؤڈ سسٹم", "tab1": "📊 ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالیں", "up": "فائل اپ لوڈ کریں", "btn": "شروع"}
}

# شريط اختيار اللغة
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# التصميم الديناميكي الكامل
st.markdown(f"""
<style>
    /* إخفاء الأزرار المزعجة */
    #MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{ display: none !important; }}
    
    /* تثبيت شريط اللغة */
    [data-testid="stSelectbox"] {{
        position: fixed !important; top: 15px !important; {lang['pos']}: 20px !important; z-index: 9999 !important; width: 150px !important;
    }}
    
    /* توسيط المحتوى مع جعل العنوان يميل لليمين عند العربية */
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']} !important; }}
    .main-container {{ max-width: 900px; margin: 0 auto; padding-top: 100px !important; text-align: {lang['align']} !important; }}
    
    /* المستطيل المتوهج أخضر نيون */
    [data-testid="stFileUploader"] {{ 
        border: 2px solid #2ea043 !important; 
        border-radius: 15px !important; 
        box-shadow: 0 0 15px rgba(46, 160, 67, 0.4) !important;
        background: #FFFFFF !important;
    }}
    
    /* تذييل الحقوق ثابت في الأسفل خالص */
    .footer {{ 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        text-align: center; padding: 15px; background: #F8F9FA; 
        color: #555; font-weight: bold; border-top: 1px solid #ddd;
    }}
</style>
""", unsafe_allow_html=True)

# محتوى الصفحة
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

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
    
    st.markdown('</div>', unsafe_allow_html=True)

# الحقوق في الأسفل خالص
st.markdown('<div class="footer">المحاسب الذكي Pro | جميع الحقوق محفوظة © 2026</div>', unsafe_allow_html=True)
