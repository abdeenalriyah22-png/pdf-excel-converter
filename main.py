import streamlit as st
import pandas as pd
import tabula
import io
from PIL import Image
import pytesseract
import fitz
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات الأربعة
translations = {
    "العربية": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF/CSV إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up1": "اسحب ملف PDF أو CSV هنا", "up2": "اسحب ملف PDF أو صورة هنا", "btn": "بدء المعالجة", "loading": "جاري المعالجة...", "copy": "📋 نسخ النص"},
    "English": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system", "tab1": "📊 PDF/CSV to Excel", "tab2": "🔍 OCR Text", "up1": "Upload PDF or CSV", "up2": "Upload PDF or Image", "btn": "Start", "loading": "Processing...", "copy": "📋 Copy"},
    "Français": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé", "tab1": "📊 PDF/CSV vers Excel", "tab2": "🔍 OCR Texte", "up1": "Charger PDF ou CSV", "up2": "Charger PDF ou Image", "btn": "Démarrer", "loading": "Traitement...", "copy": "📋 Copier"},
    "اردو": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "جدید کلاؤڈ سسٹم", "tab1": "📊 PDF/CSV ایکسل میں", "tab2": "🔍 ٹیکسٹ نکالیں", "up1": "فائل اپ لوڈ کریں", "up2": "پی ڈی ایف یا تصویر اپ لوڈ کریں", "btn": "شروع", "loading": "عمل جاری ہے...", "copy": "📋 کاپی کریں"}
}

# قائمة اللغات في الأعلى
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# التصميم (النيون + النبض + التنسيق)
st.markdown(f"""
<style>
    #MainMenu, header, footer {{ display: none !important; }}
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']} !important; }}
    
    /* تصميم زر اللغة في الأعلى */
    [data-testid="stSelectbox"] {{ position: fixed !important; top: 15px !important; {lang['pos']}: 20px !important; z-index: 9999 !important; width: 150px !important; }}
    
    /* تأثير النبض للأزرار */
    div.stButton > button {{ border: 2px solid #28a745 !important; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }} }}
    
    h1 {{ color: #202124 !important; text-align: {lang['align']} !important; }}
    .main-container {{ max-width: 900px; margin: 0 auto; padding-top: 60px; }}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    files = st.file_uploader(lang["up1"], type=["pdf", "csv"], accept_multiple_files=True)
    if files:
        for f in files:
            if st.button(f"{lang['btn']}", key=f"btn1_{f.name}"):
                with st.spinner(lang["loading"]):
                    try:
                        output = io.BytesIO()
                        if f.name.endswith('.pdf'):
                            # استخدام tabula مع encoding='utf-8' للعربية
                            dfs = tabula.read_pdf(f, pages='all', multiple_tables=True, lattice=True, encoding='utf-8')
                            if dfs:
                                combined_df = pd.concat(dfs, ignore_index=True)
                                combined_df.to_excel(output, index=False)
                        else:
                            pd.read_csv(f).to_excel(output, index=False)
                        st.download_button("📥 تحميل الإكسل", output.getvalue(), f"{f.name.split('.')[0]}.xlsx")
                    except Exception as e:
                        st.error(f"خطأ: {e}")

with tab2:
    file = st.file_uploader(lang["up2"], type=["jpg", "png", "pdf"])
    if file and st.button(f"{lang['btn']}", key="btn2"):
        st.info("جاري استخراج النص...")
st.markdown('</div>', unsafe_allow_html=True)
