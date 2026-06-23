import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import pdfplumber
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide")

# وظيفة تصحيح النصوص العربية
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# القاموس (مختصر للتوضيح)
lang = {
    "direction": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro",
    "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)",
    "btn_convert": "بدء المعالجة"
}

# --- التصميم ---
st.markdown(f"""
<style>
    .stApp {{ background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; direction: {lang['direction']}; }}
    h1 {{ color: #ffffff !important; text-align: {lang['align']}; }}
</style>
""", unsafe_allow_html=True)

st.title(lang["title"])
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    uploaded_file = st.file_uploader("ارفع ملف PDF", type=["pdf"])
    if uploaded_file and st.button(lang["btn_convert"]):
        with st.spinner("جاري المعالجة الذكية..."):
            try:
                output = io.BytesIO()
                with pdfplumber.open(uploaded_file) as pdf:
                    all_data = []
                    for page in pdf.pages:
                        table = page.extract_table()
                        if table:
                            # تصحيح النصوص في الجدول
                            fixed_table = [[fix_arabic(cell) if isinstance(cell, str) else cell for cell in row] for row in table]
                            all_data.extend(fixed_table)
                
                df = pd.DataFrame(all_data[1:], columns=all_data[0])
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    writer.sheets['Sheet1'].right_to_left()
                
                st.success("تمت المعالجة!")
                st.download_button("📥 تحميل ملف الإكسل", output.getvalue(), "Converted.xlsx")
            except Exception as e:
                st.error(f"خطأ: {e}")

with tab2:
    st.info("ميزة الـ OCR جاهزة للاستخدام.")
