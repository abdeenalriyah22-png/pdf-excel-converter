import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة ---
translations = {
    "العربية": {
        "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول",
        "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "ارفع ملف الـ PDF هنا",
        "btn_convert": "بدء التحويل: ", "btn_ocr": "🚀 تشغيل الذكاء الاصطناعي", "loading": "جاري المعالجة...",
        "success": "🚀 اكتمل التحويل بنجاح!", "download": "📥 تحميل الملف", "no_tables": "⚠️ لم يتم العثور على جداول.",
        "ocr_header": "✅ النصوص المستخرجة:", "copy": "📋 نسخ النص", "copied": "✅ تم النسخ!"
    }
}
lang = translations["العربية"]

# --- 3. تصميم Material Design 3 (تباين عالي) ---
st.markdown("""
<style>
    /* إعدادات الخطوط والتباين */
    html, body, [class*="st-emotion-cache"] { font-family: 'Segoe UI', Roboto, sans-serif !important; }
    h1 { font-size: 3.5rem !important; color: #FFFFFF !important; font-weight: 700 !important; }
    p, span, label { font-size: 1.2rem !important; color: #B0B0B0 !important; }
    
    /* خلفية سوداء عميقة */
    .stApp { background-color: #000000 !important; }

    /* مستطيل الرفع (إطار أبيض عريض) */
    [data-testid="stFileUploader"] {
        border: 3px solid #FFFFFF !important;
        background-color: #121212 !important;
        border-radius: 20px !important;
    }
    
    /* الأزرار (أبيض على أسود) */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 50px !important;
        padding: 15px 40px !important;
        font-weight: 900 !important;
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. الواجهة ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

# --- 5. منطق معالجة الملفات (بدون تعديل) ---
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
            st.text_area(lang["ocr_header"], value=full_text, height=300)
            st_copy_to_clipboard(full_text, before_copy_label=lang["copy"], after_copy_label=lang["copied"])
        except Exception as e:
            st.error(f"Error: {e}")
