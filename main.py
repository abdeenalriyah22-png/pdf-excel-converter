import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="المحاسب الذكي Pro", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة المحدث (العربية، الإنجليزية، الفرنسية، الأردية) ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#58a6ff;'>Pro</span>", "subtitle": "النظام السحابي لمعالجة البيانات", "tab1": "📊 تحويل PDF", "tab2": "🔍 استخراج النصوص (OCR)", "btn_convert": "بدء التحويل", "btn_ocr": "استخراج النص", "motto": "الفصل في الذمة.. الوصل في الأمانة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff;'>Pro</span>", "subtitle": "Advanced cloud data processing", "tab1": "📊 PDF to Excel", "tab2": "🔍 Smart OCR", "btn_convert": "Start Converting", "btn_ocr": "Extract Text", "motto": "Separation of liability... connection in trust"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff;'>Pro</span>", "subtitle": "Système cloud de traitement de données", "tab1": "📊 Convertir PDF", "tab2": "🔍 Extraction OCR", "btn_convert": "Démarrer", "btn_ocr": "Extraire", "motto": "Séparation de la responsabilité... lien de confiance"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:#58a6ff;'>Pro</span>", "subtitle": "جدید کلاؤڈ سسٹم", "tab1": "📊 پی ڈی ایف کنورٹ", "tab2": "🔍 ٹیکسٹ نکالنا", "btn_convert": "تبدیلی شروع کریں", "btn_ocr": "ٹیکسٹ نکالیں", "motto": "الفصل في الذمة.. الوصل في الأمانة"}
}

selected_lang = st.selectbox("🌐 Language / Langue / اللغة", ["العربية", "English", "Français", "اردو"])
lang = translations[selected_lang]

# --- 3. نظام التنسيق النيون (مصحح ومنظف) ---
st.markdown(f"""
<style>
    html, body, [class*="st-emotion-cache"] {{ font-family: 'Cairo', sans-serif !important; direction: {lang['dir']} !important; text-align: {lang['align']} !important; }}
    .stApp {{ background: radial-gradient(circle, #111723, #07090e) !important; color: #e6edf3 !important; }}
    h1 {{ color: #ffffff !important; text-align: center; }}
    .custom-card {{ background: #0b1526 !important; border: 2px solid #00f2fe !important; border-radius: 20px !important; padding: 25px !important; margin-bottom: 20px; }}
    .stButton>button {{ background: #00f2fe !important; color: #000 !important; font-weight: bold !important; width: 100%; border-radius: 10px !important; }}
    .footer {{ text-align: center; padding: 20px; color: #00f2fe; }}
</style>
""", unsafe_allow_html=True)

# --- 4. العرض ---
st.markdown(f"<h1>{lang['title']}</h1><p style='text-align:center;'>{lang['subtitle']}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    pdf_file = st.file_uploader(lang["tab1"], type=["pdf"])
    if pdf_file and st.button(lang["btn_convert"]):
        dfs = tabula.read_pdf(pdf_file, pages='all', lattice=True)
        if dfs:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dfs[0].to_excel(writer, index=False)
            st.success("تم التحويل بنجاح!")
            st.download_button("📥 تحميل الإكسيل", data=output.getvalue(), file_name="output.xlsx")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    ocr_file = st.file_uploader(lang["tab2"], type=["jpg", "png", "pdf"])
    if ocr_file and st.button(lang["btn_ocr"]):
        # تم تفعيل دعم الفرنسية هنا (ara+eng+fra)
        text = pytesseract.image_to_string(Image.open(ocr_file), lang='ara+eng+fra')
        st.text_area("النص:", value=text, height=200)
        st_copy_to_clipboard(text)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='footer'>{lang['motto']}</div>", unsafe_allow_html=True)
