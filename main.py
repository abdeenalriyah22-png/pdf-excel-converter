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
            direction: rtl;
        }}

        /* الشريط العلوي */
        header[data-testid="stHeader"] {{
            background-color: #FFD700 !important;
            color: #000000 !important;
        }}

        /* --- الحل النهائي لمشكلة القائمة بدون خلفية --- */
        /* استهداف حاوية القائمة المنسدلة لضمان وجود خلفية صفراء صريحة */
        div[data-baseweb="popover"], 
        div[class*="st-emotion-cache-"] ul {{
            background-color: #FFD700 !important; /* أصفر كامل بدون شفافية لضمان الوضوح */
            background: #FFD700 !important;
            border: 2px solid #000000 !important;
            box-shadow: 0px 10px 20px rgba(0,0,0,0.8) !important;
        }}

        /* تنسيق النصوص داخل القائمة لتكون واضحة جداً */
        div[data-testid="stMainMenu"] li, 
        div[class*="st-emotion-cache-"] li span {{
            color: #000000 !important; /* نص أسود */
            font-weight: 800 !important; /* خط عريض */
            font-size: 18px !important;
        }}

        /* تعديل مكان شريط الأدوات لليمين */
        [data-testid="stToolbar"] {{
            right: 1rem !important;
            left: auto !important;
            display: flex !important;
            flex-direction: row-reverse !important;
        }}
        /* ------------------------------------------- */

        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.5) !important;
            padding: 50px !important;
            border-radius: 30px !important;
        }}
        h1 {{ font-size: 60px !important; color: #FFFFFF !important; font-weight: 900 !important; text-align: right !important; }}
        p, label {{ font-size: 28px !important; color: #FFFFFF !important; font-weight: 700 !important; text-align: right !important; }}
        .stTabs [aria-selected="true"] {{ background-color: #FFD700 !important; color: #000000 !important; }}
        </style>
        '''
        st.markdown(style_code, unsafe_allow_html=True)
    except:
        pass

set_styled_interface('background.jpg')

# 3. واجهة التطبيق
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📊 جداول Excel", "🔍 استخراج نصوص"])

# الكود المتبقي لمعالجة الملفات (كما هو في النسخ السابقة)
with tab1:
    st.markdown("<p>تحويل PDF إلى جداول مرتبة</p>", unsafe_allow_html=True)
    pdf_files = st.file_uploader("ارفع ملفات PDF", type=["pdf"], key="pdf_multi", accept_multiple_files=True)
    if pdf_files:
        for uploaded_pdf in pdf_files:
            try:
                with st.spinner(f'جاري معالجة: {uploaded_pdf.name} ...'):
                    dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                    if dfs:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            sheet_name = 'Data_Sheet'
                            workbook = writer.book
                            worksheet = workbook.add_worksheet(sheet_name)
                            writer.sheets[sheet_name] = worksheet
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD700', 'color': 'black', 'border': 1, 'align': 'center'})
                            current_row = 0
                            for df in dfs:
                                df = df.replace([float('inf'), float('-inf')], 0).fillna('').loc[:, ~df.columns.str.contains('^Unnamed')]
                                df = df.replace('', pd.NA).dropna(axis=1, how='all').fillna('')
                                if df.empty: continue
                                for col_num, value in enumerate(df.columns.values):
                                    worksheet.write(current_row, col_num, value, header_fmt)
                                    worksheet.set_column(col_num, col_num, 20)
                                for row_idx, row_data in enumerate(df.values):
                                    for col_num, col_data in enumerate(row_data):
                                        worksheet.write(current_row + row_idx + 1, col_num, col_data)
                                current_row += len(df) + 3
                        st.download_button(label=f"📥 تحميل إكسيل: {uploaded_pdf.name}", data=output.getvalue(), file_name=f"Excel_{uploaded_pdf.name.split('.')[0]}.xlsx")
            except Exception as e:
                st.error(f"خطأ: {e}")

st.markdown("<br><br><p style='text-align: center; font-size: 45px; color: white; text-shadow: 3px 3px 8px #
