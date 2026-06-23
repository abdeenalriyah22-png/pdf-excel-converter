import streamlit as st
import pandas as pd
import pdfplumber
import io

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات (كما هو)
translations = {
    "العربية": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF/CSV إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up1": "اسحب ملف PDF أو CSV هنا", "up2": "اسحب ملف PDF أو صورة هنا", "btn": "بدء المعالجة", "loading": "جاري المعالجة... يرجى الانتظار", "copy": "📋 نسخ النص بالكامل"},
    "English": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system", "tab1": "📊 PDF/CSV to Excel", "tab2": "🔍 OCR Text", "up1": "Upload PDF or CSV", "up2": "Upload PDF or Image", "btn": "Start", "loading": "Processing... please wait", "copy": "📋 Copy All Text"},
    "Français": {"dir": "ltr", "align": "left", "pos": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé", "tab1": "📊 PDF/CSV vers Excel", "tab2": "🔍 OCR Texte", "up1": "Charger PDF ou CSV", "up2": "Charger PDF ou Image", "btn": "Démarrer", "copy": "📋 Copier tout"},
    "اردو": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "جدید کلاؤڈ سسٹم", "tab1": "📊 PDF/CSV ایکسل میں", "tab2": "🔍 ٹیکسٹ نکالیں", "up1": "فائل اپ لوڈ کریں", "up2": "پی ڈی ایف یا تصویر اپ لوڈ کریں", "btn": "شروع", "copy": "📋 کاپی کریں"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# التصميم الأصلي
st.markdown(f"""
<style>
    #MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stSelectbox"] {{ position: fixed !important; top: 15px !important; {lang['pos']}: 20px !important; z-index: 9999 !important; width: 150px !important; }}
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']} !important; }}
    .main-container {{ max-width: 900px; margin: 0 auto; padding-top: 100px !important; }}
    h1 {{ text-align: {lang['align']} !important; color: #202124 !important; text-shadow: 0 0 10px #28a745, 0 0 20px #28a745 !important; }}
    [data-testid="stFileUploader"] {{ border: 2px solid #28a745 !important; border-radius: 12px !important; background: #ffffff !important; }}
    div.stButton > button {{ border: 2px solid #28a745 !important; transition: 0.3s; }}
</style>
""", unsafe_allow_html=True)

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
                    with st.spinner(lang["loading"]):
                        try:
                            # استخدام pdfplumber للاستخراج الخام
                            with pdfplumber.open(f) as pdf:
                                all_data = []
                                for page in pdf.pages:
                                    table = page.extract_table()
                                    if table: all_data.extend(table)
                                
                                df = pd.DataFrame(all_data[1:], columns=all_data[0])
                                
                                # استخدام محرك التنسيق الذكي
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    df.to_excel(writer, index=False, sheet_name='Data')
                                    worksheet = writer.sheets['Data']
                                    # أمر حيوي لضبط اتجاه ورقة العمل ككل
                                    worksheet.right_to_left() 
                                    
                            st.download_button("📥 تحميل الإكسل", output.getvalue(), "Converted_Data.xlsx")
                        except Exception as e:
                            st.error(f"خطأ: {e}")

    with tab2:
        st.info("ميزة الـ OCR لا تزال تحت التطوير")
    st.markdown('</div>', unsafe_allow_html=True)
