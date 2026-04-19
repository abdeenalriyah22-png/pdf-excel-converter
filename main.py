import streamlit as st
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import shutil
import fitz  # استيراد PyMuPDF

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي - عابدين", layout="wide")

# 2. وظائف التنسيق
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def set_styled_interface(png_file):
    try:
        bin_str = get_base64(png_file)
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            direction: rtl;
        }}
        header[data-testid="stHeader"] {{ background-color: #FFD700 !important; }}
        [data-testid="stFileUploader"] {{
            background-color: rgba(255, 165, 0, 0.25) !important;
            border: 2px dashed #FFA500 !important;
            border-radius: 15px !important;
            padding: 20px !important;
        }}
        div[data-baseweb="popover"], div[class*="st-emotion-cache-"] ul {{
            background-color: #FFD700 !important;
            border: 2px solid #000000 !important;
        }}
        div[data-testid="stMainMenu"] li {{ color: #000000 !important; font-weight: 800 !important; }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.6) !important;
            padding: 40px !important;
            border-radius: 30px !important;
        }}
        h1 {{ font-size: 60px !important; color: #FFFFFF !important; font-weight: 900 !important; text-align: right !important; }}
        p, label {{ font-size: 28px !important; color: #FFFFFF !important; font-weight: 700 !important; text-align: right !important; }}
        .stTabs [aria-selected="true"] {{ background-color: #FFD700 !important; color: #000000 !important; }}
        .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.9) !important; color: #000000 !important; font-size: 20px !important; }}
        </style>
        ''', unsafe_allow_html=True)
    except: pass

set_styled_interface('background.jpg')

# 3. واجهة التطبيق
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📊 جداول Excel", "🔍 استخراج نصوص"])

with tab1:
    st.markdown("<p>تحويل PDF إلى جداول مرتبة</p>", unsafe_allow_html=True)
    pdf_files = st.file_uploader("ارفع ملفات PDF للجداول", type=["pdf"], key="pdf_excel", accept_multiple_files=True)
    if pdf_files:
        for uploaded_pdf in pdf_files:
            try:
                with st.spinner(f'جاري المعالجة...'):
                    dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                    if dfs:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            sheet_name = 'Data_Sheet'
                            workbook = writer.book
                            worksheet = workbook.add_worksheet(sheet_name)
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD700', 'color': 'black', 'border': 1, 'align': 'center'})
                            current_row = 0
                            for df in dfs:
                                df = df.replace([float('inf'), float('-inf')], 0).fillna('').loc[:, ~df.columns.str.contains('^Unnamed')]
                                df = df.replace('', pd.NA).dropna(axis=1, how='all').fillna('')
                                if df.empty: continue
                                for col_num, value in enumerate(df.columns.values):
                                    worksheet.write(current_row, col_num, value, header_fmt)
                                for row_idx, row_data in enumerate(df.values):
                                    for col_num, col_data in enumerate(row_data):
                                        worksheet.write(current_row + row_idx + 1, col_num, col_data)
                                current_row += len(df) + 3
                        st.download_button(label=f"📥 تحميل إكسيل: {uploaded_pdf.name}", data=output.getvalue(), file_name=f"Excel_{uploaded_pdf.name.split('.')[0]}.xlsx")
            except Exception as e: st.error(f"خطأ: {e}")

with tab2:
    st.markdown("<p>استخراج النصوص من الصور وملفات PDF</p>", unsafe_allow_html=True)
    ocr_file = st.file_uploader("ارفع صورة أو ملف PDF للنصوص", type=["jpg", "png", "jpeg", "pdf"], key="ocr_up")
    if ocr_file:
        full_text = ""
        if st.button("🚀 ابدأ الاستخراج"):
            try:
                with st.spinner('جاري التحليل...'):
                    if ocr_file.type == "application/pdf":
                        doc = fitz.open(stream=ocr_file.read(), filetype="pdf")
                        for page in doc:
                            text = page.get_text()
                            if text.strip(): full_text += text + "\n"
                            else:
                                pix = page.get_pixmap()
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                full_text += pytesseract.image_to_string(img, lang='ara+eng') + "\n"
                    else:
                        full_text = pytesseract.image_to_string(Image.open(ocr_file), lang='ara+eng')

                    if full_text.strip():
                        st.text_area("النص:", value=full_text, height=350)
                        st.download_button(label="📥 تحميل النص TXT", data=full_text, file_name="extracted.txt")
                    else: st.warning("لا يوجد نص واضح.")
            except Exception as e: st.error(f"خطأ: {e}")

st.markdown("<br><p style='text-align: center; font-size: 45px; color: white;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
