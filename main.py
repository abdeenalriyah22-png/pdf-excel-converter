import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import arabic_reshaper
from bidi.algorithm import get_display
from st_copy_to_clipboard import st_copy_to_clipboard

# --- وظيفة تصحيح النصوص العربية (لحل مشكلة قلب الحروف) ---
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- قاموس اللغات ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro",
        "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)",
        "uploader_pdf": "اسحب ملفات الـ PDF هنا", "btn_convert": "بدء المعالجة",
        "loading": "جاري التحويل...", "success": "تم التحويل بنجاح!", "download": "تحميل Excel"
    },
    "English": {
        "direction": "ltr", "align": "left", "title": "📊 Smart Accountant Pro",
        "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)",
        "uploader_pdf": "Drag your PDF files here", "btn_convert": "Start Processing",
        "loading": "Processing...", "success": "Conversion successful!", "download": "Download Excel"
    },
    "اردو": {
        "direction": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro",
        "tab1": "📊 پی ڈی ایف کو ایکسل میں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)",
        "uploader_pdf": "اپنی پی ڈی ایف فائلیں یہاں ڈریگ کریں", "btn_convert": "شروع کریں",
        "loading": "پروسیسنگ ہو رہی ہے...", "success": "کامیابی سے مکمل ہوا!", "download": "ایکسل ڈاؤن لوڈ کریں"
    }
}

selected_lang = st.selectbox("🌐 Choose Language", ["العربية", "English", "اردو"])
lang = translations[selected_lang]

# --- التصميم (CSS المحدث) ---
st.markdown(f"""
<style>
    .stApp {{ background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; direction: {lang['direction']}; }}
    h1 {{ color: #ffffff !important; text-align: {lang['align']}; }}
    [data-testid="stFileUploader"] {{ border: 2px dashed #21262d !important; border-radius: 20px !important; }}
    .stButton>button {{ background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important; color: white !important; border-radius: 12px !important; width: 100%; }}
</style>
""", unsafe_allow_html=True)

st.title(lang["title"])
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        for f in pdf_files:
            if st.button(f"{lang['btn_convert']} {f.name}", key=f.name):
                output = io.BytesIO()
                with st.spinner(lang["loading"]):
                    try:
                        # استخراج الجداول (بدون مكتبة tabula التي تتطلب Java إذا أمكن، أو استخدامها مع ملفاتك)
                        dfs = tabula.read_pdf(f, pages='all', multiple_tables=True, lattice=True)
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            for i, df in enumerate(dfs):
                                # تطبيق تصحيح النصوص العربية على كل خلية
                                df = df.applymap(fix_arabic)
                                df.to_excel(writer, index=False, sheet_name=f'Sheet{i+1}')
                                writer.sheets[f'Sheet{i+1}'].right_to_left()
                        
                        st.success(lang["success"])
                        st.download_button(lang["download"], output.getvalue(), f"Converted_{f.name}.xlsx")
                    except Exception as e:
                        st.error(f"Error: {e}")

with tab2:
    st.info("ميزة الـ OCR متاحة للاستخدام...")
