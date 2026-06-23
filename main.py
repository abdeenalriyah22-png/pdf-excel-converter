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

# وظيفة تصحيح النصوص العربية (لضمان ظهورها بشكل سليم في الإكسل)
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# قاموس اللغات
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "btn": "بدء المعالجة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "btn": "Start Processing"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "btn": "شروع کریں"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English", "اردو"])
lang = translations[selected_lang]

# التصميم: خلفية Off-white مع أزرار نابضة (Pulse Effect)
st.markdown(f"""
<style>
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']}; }}
    h1 {{ color: #202124 !important; text-align: {lang['align']}; }}
    
    div.stButton > button {{ 
        border: 2px solid #28a745 !important; 
        background: white !important;
        color: #28a745 !important;
        transition: 0.3s; 
        animation: pulse 2s infinite; 
    }}
    @keyframes pulse {{ 
        0% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }} 
        70% {{ box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }} 
        100% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }} 
    }}
</style>
""", unsafe_allow_html=True)

st.title(lang["title"])

# المعالجة الذكية للجداول
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
                                # تصحيح النصوص العربية قبل الإضافة
                                fixed_table = [[fix_arabic(cell) if isinstance(cell, str) else cell for cell in row] for row in table]
                                all_data.extend(fixed_table)
                    
                    df = pd.DataFrame(all_data[1:], columns=all_data[0])
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Data')
                        writer.sheets['Data'].right_to_left()
                    
                    st.success("تم التحويل!")
                    st.download_button("📥 تحميل الإكسل", output.getvalue(), f"Excel_{f.name}.xlsx")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
