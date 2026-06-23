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

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="المحاسب الذكي Pro / Smart Accountant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. دمج كود جوجل أدسنس ---
components.html("""
<meta name="google-adsense-account" content="ca-pub-1091631464795781">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781" crossorigin="anonymous"></script>
""", height=0, width=0)

# --- 3. اختيار اللغة ---
selected_lang = st.selectbox(
    "🌐 Choose Language / اختر اللغة / زبان کا انتخاب کریں",
    ["العربية", "English", "اردو"],
    index=0,
    key="language_selector"
)

# --- 4. وظيفة تصحيح النصوص العربية (بدون قلب الحروف) ---
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# --- 5. التصميم النيوني ---
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; }
    h1 { color: #ffffff !important; text-align: center; text-shadow: 0 0 10px #58a6ff; }
    .stButton>button { background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important; color: white !important; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("📊 المحاسب الذكي Pro")

tab1, tab2 = st.tabs(["📊 تحويل PDF إلى Excel", "🔍 استخراج النصوص (OCR)"])

# --- 6. تبويب المعالجة (PDF إلى Excel) ---
with tab1:
    files = st.file_uploader("ارفع ملفات الـ PDF هنا", type=["pdf"], accept_multiple_files=True)
    if files:
        for f in files:
            if st.button(f"بدء المعالجة: {f.name}"):
                with st.spinner("جاري المعالجة الذكية..."):
                    try:
                        output = io.BytesIO()
                        # استخدام pdfplumber بدلاً من tabula لتجنب خطأ الجافا
                        with pdfplumber.open(f) as pdf:
                            all_data = []
                            for page in pdf.pages:
                                table = page.extract_table()
                                if table:
                                    # تصحيح الحروف العربية لكل خلية
                                    fixed_table = [[fix_arabic(cell) if isinstance(cell, str) else cell for cell in row] for row in table]
                                    all_data.extend(fixed_table)
                        
                        df = pd.DataFrame(all_data[1:], columns=all_data[0])
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Sheet1')
                            writer.sheets['Sheet1'].right_to_left()
                        
                        st.success("تم التحويل بنجاح!")
                        st.download_button("📥 تحميل الإكسل", output.getvalue(), f"Excel_{f.name}.xlsx")
                    except Exception as e:
                        st.error(f"خطأ في المعالجة: {e}")

# --- 7. تبويب OCR والإعلانات ---
with tab2:
    st.info("ميزة استخراج النصوص جاهزة.")
    
# مساحة الإعلان
components.html("""<div style="text-align:center;"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-1091631464795781" data-ad-slot="8159670732"></ins></div>""", height=100)
