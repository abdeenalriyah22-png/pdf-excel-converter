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
        /* خلفية التطبيق */
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            direction: rtl; /* توجيه الصفحة لليمين */
        }}

        /* --- الشريط العلوي الأصفر --- */
        header[data-testid="stHeader"] {{
            background-color: #FFD700 !important;
            color: #000000 !important;
        }}
        header[data-testid="stHeader"] svg {{ fill: #000000 !important; }}
        header[data-testid="stHeader"] button {{ color: #000000 !important; }}

        /* --- تعديل القائمة المنسدلة (جهة اليمين + نصوص واضحة) --- */
        div[data-testid="stTooltipHoverTarget"] {{ direction: rtl !important; }}
        
        /* استهداف حاوية القائمة المنسدلة */
        div[data-baseweb="popover"] {{
            direction: rtl !important;
            text-align: right !important;
        }}

        /* تنسيق الأزرار داخل القائمة */
        div[data-testid="stMainMenu"] ul {{
            background-color: rgba(255, 215, 0, 0.9) !important; /* زيادة كثافة اللون للوضوح */
            border: 2px solid #000000 !important;
            border-radius: 12px !important;
            padding: 10px !important;
        }}

        div[data-testid="stMainMenu"] li {{
            color: #000000 !important; /* نص أسود فاحم */
            font-weight: 900 !important; /* خط عريض جداً */
            font-size: 18px !important;
            text-align: right !important;
            padding: 10px !important;
        }}

        div[data-testid="stMainMenu"] li:hover {{
            background-color: rgba(0, 0, 0, 0.15) !important;
        }}

        /* تصحيح مكان الأيقونة (الثلاث نقاط) لتكون جهة اليمين */
        [data-testid="stToolbar"] {{
            right: auto !important;
            left: 2rem !important;
            flex-direction: row-reverse !important;
        }}
        /* --------------------------------------------------- */
        
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.5) !important;
            padding: 50px !important;
            border-radius: 30px !important;
        }}

        h1 {{ font-size: 60px !important; color: #FFFFFF !important; font-weight: 900 !important; text-shadow: 4px 4px 10px #000000 !important; text-align: right !important; }}
        p, label {{ font-size: 28px !important; color: #FFFFFF !important; font-weight: 700 !important; text-align: right !important; }}

        /* التبويبات السفلية */
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent !important; gap: 10px !important; direction: rtl !important; }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #FFFFFF !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
        }}
        .stTabs [aria-selected="true"] {{ background-color: #FFD700 !important; color: #000000 !important; }}

        .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.95) !important; color: #000000 !important; font-size: 20px !important; direction: rtl !important; }}
        [data-testid="stFileUploader"] {{ background-color: rgba(255, 215, 0, 0.1) !important; border: 2px dashed #FFD700 !important; }}
        </style>
        '''
        st.markdown(style_code, unsafe_allow_html=True)
    except:
        pass

set_styled_interface('background.jpg')

# 3. واجهة التطبيق
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📊 جداول Excel", "🔍 استخراج نصوص"])

with tab1:
    st.markdown("<p>تحويل PDF إلى جداول مرتبة (تطهير تلقائي للأعمدة)</p>", unsafe_allow_html=True)
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
                            border_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD700', 'color': 'black', 'border': 1, 'align': 'center'})
                            
                            current_row = 0
                            for df in dfs:
                                df = df.replace([float('inf'), float('-inf')], 0).fillna('')
                                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                                df = df.replace('', pd.NA).dropna(axis=1, how='all').fillna('')
                                if df.empty or len(df.columns) == 0: continue
                                
                                for col_num, value in enumerate(df.columns.values):
                                    worksheet.write(current_row, col_num, value, header_fmt)
                                    worksheet.set_column(col_num, col_num, 20)
                                for row_idx, row_data in enumerate(df.values):
                                    for col_num, col_data in enumerate(row_data):
                                        worksheet.write(current_row + row_idx + 1, col_num, col_data, border_fmt)
                                current_row += len(df) + 3
                        st.download_button(label=f"📥 تحميل إكسيل: {uploaded_pdf.name}", data=output.getvalue(), file_name=f"Excel_{uploaded_pdf.name.split('.')[0]}.xlsx", key=f"btn_{uploaded_pdf.name}")
            except Exception as e:
                st.error(f"خطأ: {e}")

with tab2:
    st.markdown("<p>استخراج النصوص من الصور</p>", unsafe_allow_html=True)
    img_file = st.file_uploader("ارفع صورة المستند", type=["jpg", "png", "jpeg"], key="img_up")
    if img_file:
        image = Image.open(img_file)
        st.image(image, width=500)
        if st.button("ابدأ استخراج النص"):
            try:
                with st.spinner('جاري القراءة...'):
                    text = pytesseract.image_to_string(image, lang='ara+eng')
                    if text.strip():
                        st.text_area("", value=text, height=400)
            except Exception as e:
                st.error(f"خطأ: {e}")

st.markdown("<br><br><p style='text-align: center; font-size: 45px; color: white; text-shadow: 3px 3px 8px #000;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
