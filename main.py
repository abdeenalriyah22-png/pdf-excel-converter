import streamlit as st
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import shutil

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي - عابدين", layout="wide")

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
        
        .stTextArea textarea {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #000000 !important;
            font-size: 22px !important;
            font-weight: 600 !important;
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
    st.markdown("<p>تحويل PDF إلى Excel مع معالجة الصفوف الزائدة والحدود</p>", unsafe_allow_html=True)
    pdf_file = st.file_uploader("ارفع ملف PDF", type=["pdf"], key="pdf_key")
    if pdf_file:
        try:
            with st.spinner('جاري تحليل الجداول وتنسيقها...'):
                dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
                if dfs:
                    st.success(f"تم استخراج {len(dfs)} جدول بنجاح")
                    output = io.BytesIO()
                    
                    # استخدام XlsxWriter لتنسيق الحدود
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, df in enumerate(dfs):
                            # الحل للمشكلة 1: حذف الصفوف الأولى إذا كانت كلها فارغة (NaN)
                            df = df.dropna(how='all', axis=0).reset_index(drop=True)
                            
                            sheet_name = f'Table_{i+1}'
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                            # الحل للمشكلة 2: إضافة الحدود (Borders) وتنسيق الرأس
                            workbook  = writer.book
                            worksheet = writer.sheets[sheet_name]
                            
                            # تعريف تنسيق الحدود
                            border_format = workbook.add_format({
                                'border': 1,
                                'align': 'center',
                                'valign': 'vcenter'
                            })
                            
                            # تطبيق التنسيق على كامل نطاق الجدول
                            for row_num, row_data in enumerate(df.values):
                                for col_num, col_data in enumerate(row_data):
                                    worksheet.write(row_num + 1, col_num, col_data, border_format)
                            
                            # تنسيق عناوين الأعمدة
                            header_format = workbook.add_format({
                                'bold': True,
                                'bg_color': '#FFA500',
                                'color': 'white',
                                'border': 1,
                                'align': 'center'
                            })
                            for col_num, value in enumerate(df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                            
                            st.dataframe(df)
                    
                    st.download_button("📥 تحميل ملف Excel المنسق", data=output.getvalue(), file_name="Formatted_Data.xlsx")
        except Exception as e:
            st.error(f"خطأ: {e}")

with tab2:
    # (يبقى كود التبويب الثاني كما هو في الإصدار السابق)
    st.markdown("<p>استخراج النصوص من الصور</p>", unsafe_allow_html=True)
    img_file = st.file_uploader("ارفع صورة المستند", type=["jpg", "png", "jpeg"], key="img_key")
    if img_file:
        image = Image.open(img_file)
        if st.button("استخراج النص"):
            text = pytesseract.image_to_string(image, lang='ara+eng')
            st.text_area("", value=text, height=300)

st.markdown("<br><p style='text-align: center; color: white; font-size: 35px;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
