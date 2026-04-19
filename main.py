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

# التحقق من وجود محرك OCR
tesseract_path = shutil.which("tesseract")

# 2. وظائف التنسيق والبصريات
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
            background-color: rgba(0, 0, 0, 0.4) !important;
            padding: 40px !important;
            border-radius: 30px !important;
        }}
        h1 {{ font-size: 60px !important; color: white !important; text-shadow: 3px 3px 6px black !important; text-align: right; }}
        p, label {{ font-size: 28px !important; color: white !important; text-shadow: 2px 2px 4px black !important; text-align: right; }}
        
        /* تحسين صندوق النص المستخرج - خلفية بيضاء شفافة وخط واضح */
        .stTextArea textarea {{
            background-color: rgba(255, 255, 255, 0.9) !important; /* خلفية بيضاء واضحة */
            color: #000000 !important; /* نص أسود للقراءة */
            font-size: 22px !important;
            font-weight: 600 !important;
            border-radius: 15px !important;
            direction: rtl !important;
        }}
        
        [data-testid="stFileUploader"] {{
            background-color: rgba(255, 165, 0, 0.2) !important;
            border: 2px dashed #FFA500 !important;
        }}
        .stTabs [data-baseweb="tab"] {{ color: white !important; font-size: 22px !important; }}
        .stTabs [aria-selected="true"] {{ background-color: #FFA500 !important; border-radius: 10px; }}
        </style>
        '''
        st.markdown(style_code, unsafe_allow_html=True)
    except:
        pass

set_styled_interface('background.jpg')

# 3. واجهة التطبيق
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 استخراج الجداول (Excel)", "🔍 استخراج النصوص (عربي/إنجليزي)"])

with tab1:
    st.markdown("<p>حول ملفات الـ PDF إلى جداول إكسيل منظمة</p>", unsafe_allow_html=True)
    pdf_file = st.file_uploader("ارفع ملف PDF", type=["pdf"], key="pdf_key")
    if pdf_file:
        try:
            with st.spinner('جاري تحليل الجداول...'):
                dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
                if dfs:
                    st.success(f"تم استخراج {len(dfs)} جدول")
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, df in enumerate(dfs):
                            st.dataframe(df)
                            df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                    st.download_button("📥 تحميل ملف Excel", data=output.getvalue(), file_name="Converted_Data.xlsx")
        except Exception as e:
            st.error(f"خطأ: {e}")

with tab2:
    st.markdown("<p>استخراج النصوص من الصور (يدعم العربية والإنجليزية والأرقام)</p>", unsafe_allow_html=True)
    if not tesseract_path:
        st.error("⚠️ محرك OCR غير مثبت. تأكد من ملف packages.txt")
    
    img_file = st.file_uploader("ارفع صورة المستند (PNG, JPG)", type=["jpg", "png", "jpeg"], key="img_key")
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="المعاينة", width=500)
        
        if st.button("استخراج النص الآن"):
            try:
                with st.spinner('جاري قراءة النص والبيانات...'):
                    # الإعداد السحري: ara+eng لدعم اللغتين معاً
                    extracted_text = pytesseract.image_to_string(image, lang='ara+eng')
                    
                    if extracted_text.strip():
                        st.markdown("<p>النص المستخرج بوضوح:</p>", unsafe_allow_html=True)
                        st.text_area(label="", value=extracted_text, height=400)
                        st.download_button("📥 حفظ النص كملف", data=extracted_text, file_name="Extracted.txt")
                    else:
                        st.warning("لم يتم التعثور على نصوص واضحة.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")

st.markdown("<br><br><p style='text-align: center; color: white; font-size: 35px;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
