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

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# 2. وظيفة تصحيح النصوص العربية (الجزء الذكي)
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# 3. القاموس الموحد للغات
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "btn": "بدء المعالجة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "tab1": "📊 PDF to Excel", "tab2": "🔍 Smart OCR", "btn": "Start Processing"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "tab1": "📊 پی ڈی ایف سے ایکسل", "tab2": "🔍 OCR ٹیکسٹ", "btn": "شروع کریں"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English", "اردو"])
lang = translations[selected_lang]

# 4. التصميم النيوني الاحترافي
st.markdown(f"""
<style>
    .stApp {{ background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; direction: {lang['dir']}; }}
    h1 {{ color: #ffffff !important; text-align: {lang['align']}; text-shadow: 0 0 10px #58a6ff; }}
    .stButton>button {{ background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important; color: white !important; width: 100%; border-radius: 12px; }}
</style>
""", unsafe_allow_html=True)

st.title(lang["title"])
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

# 5. التبويب الأول: معالجة الجداول (PDF -> Excel)
with tab1:
    files = st.file_uploader("ارفع ملف PDF", type=["pdf"], accept_multiple_files=True)
    if files:
        for f in files:
            if st.button(f"{lang['btn']} {f.name}"):
                with st.spinner("جاري المعالجة الذكية..."):
                    try:
                        output = io.BytesIO()
                        with pdfplumber.open(f) as pdf:
                            all_data = []
                            for page in pdf.pages:
                                table = page.extract_table()
                                if table:
                                    # تصحيح ذكي للنص ليعرض بشكل سليم في إكسل
                                    fixed_table = [[fix_arabic(cell) if isinstance(cell, str) else cell for cell in row] for row in table]
                                    all_data.extend(fixed_table)
                        
                        df = pd.DataFrame(all_data[1:], columns=all_data[0])
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Data')
                            writer.sheets['Data'].right_to_left()
                        
                        st.success("تمت المعالجة!")
                        st.download_button("📥 تحميل الإكسل", output.getvalue(), f"Excel_{f.name.replace('.pdf', '')}.xlsx")
                    except Exception as e:
                        st.error(f"حدث خطأ: {e}")

# 6. التبويب الثاني: استخراج النصوص (OCR)
with tab2:
    uploaded_ocr = st.file_uploader("ارفع صورة أو ملف PDF للاستخراج", type=["jpg", "png", "pdf"])
    if uploaded_ocr and st.button("استخراج النص"):
        full_text = "تجربة استخراج النص..." # هنا يوضع منطق OCR الخاص بك
        st.text_area("النص المستخرج:", value=full_text)
        st_copy_to_clipboard(text=full_text)
