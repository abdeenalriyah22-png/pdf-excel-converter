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

# 2. وظائف التنسيق والبصريات (التعديل المطلوب للشريط العلوي)
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
        }}

        /* --- تعديل الشريط العلوي (Share, Edit, etc.) باللون الأصفر --- */
        header[data-testid="stHeader"] {{
            background-color: #FFD700 !important;
            color: #000000 !important;
        }}
        header[data-testid="stHeader"] svg {{
            fill: #000000 !important; /* تلوين الأيقونات بالأسود لتظهر فوق الأصفر */
        }}
        header[data-testid="stHeader"] button {{
            color: #000000 !important;
        }}
        /* --------------------------------------------------------- */
        
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.4) !important;
            padding: 50px !important;
            border-radius: 30px !important;
        }}

        h1 {{ font-size: 70px !important; color: #FFFFFF !important; font-weight: 900 !important; text-shadow: 4px 4px 10px #000000 !important; text-align: right !important; }}
        p, label {{ font-size: 30px !important; color: #FFFFFF !important; font-weight: 700 !important; text-align: right !important; }}

        /* إعادة التبويبات لشكلها السابق (شفافة مع خط أبيض) */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent !important;
            padding: 0 !important;
            gap: 10px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #FFFFFF !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #FFD700 !important;
            color: #000000 !important;
        }}

        .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.95) !important; color: #000000 !important; font-size: 20px !important; direction: rtl !important; }}
        [data-testid="stFileUploader"] {{ background-color: rgba(255, 215, 0, 0.1) !important; border: 2px dashed #FFD700 !important; }}
        .stApp {{ direction: rtl !important; text-align: right !important; }}
        </style>
        '''
        st.markdown(style_code, unsafe_allow_html=True)
    except:
        pass

set_styled_interface('background.jpg')

# 3. واجهة التطبيق
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 جداول Excel", "🔍 استخراج نصوص"])

# --- التبويب الأول: محول الجداول ---
with tab1:
    st.markdown("<p>تحويل PDF إلى جداول مرتبة في ورقة إكسيل واحدة</p>", unsafe_allow_html=True)
    pdf_files = st.file_uploader("ارفع ملفات PDF", type=["pdf"], key="pdf_multi", accept_multiple_files=True)
    
    if pdf_files:
        for uploaded_pdf in pdf_files:
            try:
                with st.spinner(f'جاري معالجة: {uploaded_pdf.name} ...'):
                    dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True)
                    if dfs:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                            sheet_name = 'Data_Sheet'
                            workbook = writer.book
                            worksheet = workbook.add_worksheet(sheet_name)
                            writer.sheets[sheet_name] = worksheet
                            
                            border_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD700', 'color': 'black', 'border': 1, 'align': 'center'})
                            
                            current_row = 0
                            for df in dfs:
                                df = df.replace([float('inf'), float('-inf')], 0).fillna('')
                                if df.empty: continue
                                for col_num, value in enumerate(df.columns.values):
                                    worksheet.write(current_row, col_num, value, header_fmt)
                                    worksheet.set_column(col_num, col_num, 22)
                                for row_idx, row_data in enumerate(df.values):
                                    for col_num, col_data in enumerate(row_data):
                                        worksheet.write(current_row + row_idx + 1, col_num, col_data, border_fmt)
                                current_row += len(df) + 3
                            
                        st.download_button(label=f"📥 تحميل إكسيل: {uploaded_pdf.name}", data=output.getvalue(), file_name=f"Excel_{uploaded_pdf.name.split('.')[0]}.xlsx", key=f"btn_{uploaded_pdf.name}")
                        st.divider()
            except Exception as e:
                st.error(f"خطأ: {e}")

# --- التبويب الثاني: استخراج النصوص ---
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
