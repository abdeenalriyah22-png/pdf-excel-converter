import streamlit as st
import tabula
import pandas as pd
import io
import fitz
from PIL import Image
import pytesseract
from st_copy_to_clipboard import st_copy_to_clipboard

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", layout="wide", initial_sidebar_state="collapsed")

# قاموس الترجمة
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي لمعالجة البيانات", "tab1": "📊 تحويل PDF", "tab2": "🔍 استخراج النصوص", "btn_convert": "بدء التحويل", "btn_ocr": "استخراج النص", "motto": "الفصل في الذمة.. الوصل في الأمانة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud data processing", "tab1": "📊 PDF to Excel", "tab2": "🔍 Smart OCR", "btn_convert": "Start Converting", "btn_ocr": "Launch AI Read", "motto": "Separation of liability... connection in trust"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Système cloud avancé de traitement", "tab1": "📊 Convertir PDF", "tab2": "🔍 Extraction OCR", "btn_convert": "Démarrer", "btn_ocr": "Extraire", "motto": "Séparation de la responsabilité... lien de confiance"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "جدید کلاؤڈ سسٹم برائے ڈیٹا پروسیسنگ", "tab1": "📊 پی ڈی ایف کنورٹ", "tab2": "🔍 ٹیکسٹ نکالنا", "btn_convert": "تبدیلی شروع کریں", "btn_ocr": "ٹیکسٹ نکالیں", "motto": "الفصل في الذمة.. الوصل في الأمانة"}
}

# اختيار اللغة
selected_lang = st.selectbox("🌐 Language / Langue / اللغة", ["العربية", "English", "Français", "اردو"])
lang = translations[selected_lang]

# التنسيق النيون (مصحح برمجياً)
st.markdown(f"""
<style>
    html, body, [class*="st-emotion-cache"] {{ 
        font-family: 'Cairo', sans-serif !important; 
        direction: {lang['dir']} !important; 
        text-align: {lang['align']} !important; 
    }}
    .stApp {{ background: radial-gradient(circle, #0b0f19, #050a14) !important; color: #00f2fe !important; }}
    h1 {{ color: #00f2fe !important; text-shadow: 0 0 10px #00f2fe; text-align: center; }}
    .custom-card {{ background: #0b1526 !important; border: 2px solid #00f2fe !important; border-radius: 20px !important; padding: 20px !important; margin-bottom: 20px; }}
    [data-testid="stFileUploader"] {{ border: 2px dashed #00f2fe !important; border-radius: 15px !important; background: rgba(0, 242, 254, 0.05) !important; }}
    .stButton>button {{ background: #00f2fe !important; color: #000 !important; font-weight: bold !important; width: 100%; border-radius: 10px !important; }}
    .footer {{ text-align: center; padding: 20px; color: #00f2fe; position: fixed; bottom: 0; width: 100%; }}
</style>
""", unsafe_allow_html=True)

# العرض
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
        text = pytesseract.image_to_string(Image.open(ocr_file), lang='ara+eng+fra')
        st.text_area("النص:", value=text, height=200)
        st_copy_to_clipboard(text)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div class='footer'>{lang['motto']}</div>", unsafe_allow_html=True)
