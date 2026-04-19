import streamlit as st
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import shutil

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي - عبدين", layout="wide")

# 2. التحقق من وجود محرك OCR
tesseract_path = shutil.which("tesseract")

# وظيفة التنسيق
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_styled_interface(png_file):
    try:
        bin_str = get_base64(png_file)
        style_code = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.5) !important;
            padding: 50px !important;
            border-radius: 30px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
        }}
        h1 {{ font-size: 60px !important; color: white !important; text-shadow: 3px 3px 5px black !important; }}
        p, label {{ font-size: 30px !important; color: white !important; text-shadow: 2px 2px 4px black !important; }}
        [data-testid="stFileUploader"] {{
            background-color: rgba(255, 165, 0, 0.2) !important;
            border: 2px dashed orange !important;
        }}
        .stTabs [data-baseweb="tab"] {{ color: white !important; font-size: 20px !important; }}
        </style>
        '''
        st.markdown(style_code, unsafe_allow_html=True)
    except:
        pass

set_styled_interface('background.jpg')

# 3. واجهة التبويبات
st.markdown("<h1 style='text-align: right;'>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 جداول Excel", "🔍 نصوص عربية"])

with tab1:
    st.markdown("<p style='text-align: right;'>محول الجداول من PDF</p>", unsafe_allow_html=True)
    pdf_file = st.file_uploader("ارفع ملف الجداول", type=["pdf"], key="pdf_up")
    if pdf_file:
        try:
            dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
            if dfs:
                st.success(f"تم العثور على {len(dfs)} جدول")
                # ... كود التحميل المعتاد ...
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

with tab2:
    st.markdown("<p style='text-align: right;'>استخراج النص من الصور</p>", unsafe_allow_html=True)
    if not tesseract_path:
        st.error("⚠️ محرك النصوص غير جاهز بعد. يرجى التأكد من ملف packages.txt")
    
    img_file = st.file_uploader("ارفع صورة الفاتورة أو المستند", type=["jpg", "png", "jpeg"], key="img_up")
    if img_file:
        image = Image.open(img_file)
        st.image(image, width=500)
        if st.button("ابدأ استخراج النص"):
            try:
                # استخدام اللغة العربية ara
                text = pytesseract.image_to_string(image, lang='ara')
                st.text_area("النص المستخرج:", value=text, height=300)
            except Exception as e:
                st.error(f"خطأ في المعالجة: {e}")

st.markdown("<br><p style='text-align: center; color: white;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
