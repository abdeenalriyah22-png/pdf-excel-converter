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

# قاموس الترجمة المكتمل (مع الفرنسية)
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "ارفع ملف الـ PDF هنا", "btn_convert": "بدء التحويل: ", "btn_ocr": "🚀 تشغيل الذكاء الاصطناعي", "loading": "جاري المعالجة...", "success": "🚀 اكتمل التحويل!", "download": "📥 تحميل الملف", "no_tables": "⚠️ لم يتم العثور على جداول."},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system for data processing", "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)", "up": "Upload your PDF file here", "btn_convert": "Start conversion: ", "btn_ocr": "🚀 Run AI", "loading": "Processing...", "success": "🚀 Done!", "download": "📥 Download", "no_tables": "⚠️ No tables found."},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé pour données", "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)", "up": "Téléchargez votre fichier PDF ici", "btn_convert": "Démarrer la conversion: ", "btn_ocr": "🚀 Lancer l'IA", "loading": "Traitement en cours...", "success": "🚀 Conversion réussie!", "download": "📥 Télécharger le fichier", "no_tables": "⚠️ Aucun tableau trouvé."},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "ڈیٹا پروسیسنگ کا جدید نظام", "tab1": "📊 PDF کو ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)", "up": "فائل یہاں اپ لوڈ کریں", "btn_convert": "تبدیلی شروع کریں: ", "btn_ocr": "🚀 AI چلائیں", "loading": "پروسیسنگ...", "success": "🚀 مکمل ہوا!", "download": "📥 فائل ڈاؤن لوڈ کریں", "no_tables": "⚠️ کوئی ٹیبل نہیں ملا۔"}
}

# اختيار اللغة
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# تصميم جوجل الجديد (خلفية فاتحة + تباين عالي)
st.markdown(f"""
<style>
    html, body, .stApp {{ 
        direction: {lang['dir']} !important; 
        text-align: {lang['align']} !important; 
        background-color: #F8F9FA !important; 
        color: #202124 !important; 
    }}
    h1 {{ color: #1A73E8 !important; font-size: 3rem !important; }}
    [data-testid="stFileUploader"] {{ border: 2px solid #DADCE0 !important; background-color: #FFFFFF !important; border-radius: 12px !important; }}
    .stButton > button {{ background-color: #1A73E8 !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: bold !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

# --- منطق معالجة الملفات (بدون تعديل) ---
with tab1:
    pdf_files = st.file_uploader(lang["up"], type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        for f in pdf_files:
            if st.button(f"{lang['btn_convert']}{f.name}"):
                with st.spinner(lang["loading"]):
                    dfs = tabula.read_pdf(f, pages='all', multiple_tables=True, lattice=True)
                    if dfs:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            for i, df in enumerate(dfs):
                                df.to_excel(writer, index=False, sheet_name=f'Sheet{i+1}')
                        st.success(lang["success"])
                        st.download_button(lang["download"], output.getvalue(), f"{f.name}.xlsx", "application/vnd.ms-excel")
                    else:
                        st.warning(lang["no_tables"])

with tab2:
    img = st.file_uploader(lang["up"], type=["jpg", "png", "pdf"])
    if img and st.button(lang["btn_ocr"]):
        try:
            full_text = pytesseract.image_to_string(Image.open(img), lang='ara+eng')
            st.text_area("النص:", value=full_text, height=300)
        except Exception as e:
            st.error(f"Error: {e}")
