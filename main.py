import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import fitz
from PIL import Image
import pytesseract
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة (شامل الفرنسية) ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي لمعالجة البيانات", "tab1": "📊 تحويل PDF", "tab2": "🔍 استخراج النصوص", "btn_convert": "بدء التحويل", "btn_ocr": "استخراج النص", "motto": "الفصل في الذمة.. الوصل في الأمانة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud data processing", "tab1": "📊 PDF to Excel", "tab2": "🔍 Smart OCR", "btn_convert": "Start Converting", "btn_ocr": "Launch AI Read", "motto": "Separation of liability... connection in trust"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Système cloud avancé de traitement des données", "tab1": "📊 Convertir PDF", "tab2": "🔍 Extraction de texte (OCR)", "btn_convert": "Démarrer la conversion", "btn_ocr": "Extraire le texte", "motto": "Séparation de la responsabilité... lien de confiance"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "جدید کلاؤڈ سسٹم برائے ڈیٹا پروسیسنگ", "tab1": "📊 پی ڈی ایف کنورٹ", "tab2": "🔍 ٹیکسٹ نکالنا", "btn_convert": "تبدیلی شروع کریں", "btn_ocr": "ٹیکسٹ نکالیں", "motto": "الفصل في الذمة.. الوصل في الأمانة"}
}

selected_lang = st.selectbox("🌐 Language / Langue / اللغة", ["العربية", "English", "Français", "اردو"])
lang = translations[selected_lang]

# --- 3. التنسيق (CSS) ---
st.markdown(f"""
<style>
    html, body, [class*="st-emotion-cache"] {{ font-family: 'Cairo', sans-serif !important; direction: {lang['dir']} !important; text-align: {lang['align']} !important; }}
    .stApp {{ background: radial-gradient(circle, #111723, #07090e); color: #e6edf3; }}
    h1 {{ color: #58a6ff; }}
    .custom-card {{ background: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px; }}
</style>
""", unsafe_allow_html=True)

# --- 4. المحتوى ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    pdf_file = st.file_uploader(lang["tab1"], type=["pdf"])
    if pdf_file and st.button(lang["btn_convert"]):
        dfs = tabula.read_pdf(pdf_file, pages='all', lattice=True)
        if dfs:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dfs[0].to_excel(writer, index=False)
            st.success("تم التحويل بنجاح!")
            st.download_button("📥 تحميل الإكسيل", data=output.getvalue(), file_name="output.xlsx")

with tab2:
    ocr_file = st.file_uploader(lang["tab2"], type=["jpg", "png", "pdf"])
    if ocr_file and st.button(lang["btn_ocr"]):
        # كود مبسط للـ OCR
        text = pytesseract.image_to_string(Image.open(ocr_file), lang='ara+eng+fra')
        st.text_area("النص:", value=text, height=200)
        st_copy_to_clipboard(text)

# --- التذييل ---
st.markdown(f"<div style='text-align:center; padding:20px; color:#58a6ff;'>{lang['motto']}</div>", unsafe_allow_html=True)
