import streamlit as st
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي - عابدين", layout="wide")

# 2. وظائف التنسيق والبصريات
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_styled_interface(png_file):
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
        margin-top: 30px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
        max-width: 1200px !important;
    }}
    h1 {{ font-size: 70px !important; color: #FFFFFF !important; text-shadow: 4px 4px 10px #000000 !important; }}
    p, span, label, .stMarkdown {{ font-size: 35px !important; color: #FFFFFF !important; text-shadow: 2px 2px 5px #000000 !important; }}
    
    /* مستطيل الرفع البرتقالي الشفاف */
    [data-testid="stFileUploader"] {{
        background-color: rgba(255, 165, 0, 0.25) !important;
        border: 3px dashed #FFA500 !important;
        border-radius: 20px !important;
    }}
    
    /* تنسيق التبويبات (Tabs) لتبدو واضحة */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: white !important;
        padding: 10px 30px;
        font-size: 25px !important;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #FFA500 !important; }}

    .stApp {{ direction: rtl !important; text-align: right !important; }}
    </style>
    '''
    st.markdown(style_code, unsafe_allow_html=True)

try:
    set_styled_interface('background.jpg')
except:
    pass

# 3. واجهة التطبيق مع التبويبات
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 استخراج جداول (Excel)", "🔍 استخراج نصوص عربية (OCR)"])

# --- التبويب الأول: محول الجداول القديم ---
with tab1:
    st.markdown("<p>رفع ملف PDF لتحويله إلى جداول Excel</p>", unsafe_allow_html=True)
    file_pdf = st.file_uploader("ارفع ملف PDF للجداول", type=["pdf"], key="pdf_tab1")
    
    if file_pdf:
        try:
            with st.spinner('جاري التحليل...'):
                dfs = tabula.read_pdf(file_pdf, pages='all', multiple_tables=True)
                if dfs:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, df in enumerate(dfs):
                            st.dataframe(df)
                            df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                    st.download_button("📥 تحميل ملف Excel", data=output.getvalue(), file_name="Data.xlsx")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

# --- التبويب الثاني: مستخرج النصوص الجديد ---
with tab2:
    st.markdown("<p>استخراج النصوص العربية من الصور (JPG, PNG)</p>", unsafe_allow_html=True)
    file_img = st.file_uploader("ارفع صورة أو ملف PDF للنص", type=["jpg", "png", "jpeg"], key="img_tab2")
    
    if file_img:
        try:
            with st.spinner('جاري قراءة النص العربي...'):
                image = Image.open(file_img)
                st.image(image, caption="المعاينة", width=400)
                
                # استخراج النص باستخدام محرك تيسراكت للغة العربية
                text = pytesseract.image_to_string(image, lang='ara')
                
                if text.strip():
                    st.markdown("<p>النص المستخرج:</p>", unsafe_allow_html=True)
                    st.text_area("", value=text, height=300)
                    st.download_button("📥 حفظ النص كمحرر", data=text, file_name="Extracted_Text.txt")
                else:
                    st.warning("لم يتم العثور على نص واضح، تأكد من جودة الصورة.")
        except Exception as e:
            st.error("تأكد من تنصيب محرك Tesseract في السيرفر أولاً.")

st.markdown("<br><p style='text-align: center; font-size: 40px;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
