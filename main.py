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
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0.3) !important; }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.4) !important;
            padding: 50px !important;
            border-radius: 30px !important;
            margin-top: 30px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
            max-width: 1200px !important;
        }}
        h1 {{ font-size: 70px !important; color: #FFFFFF !important; font-weight: 900 !important; text-shadow: 4px 4px 10px #000000 !important; text-align: right !important; }}
        p, label, .stMarkdown {{ font-size: 35px !important; color: #FFFFFF !important; font-weight: 700 !important; text-shadow: 2px 2px 5px #000000 !important; text-align: right !important; }}
        .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.95) !important; color: #000000 !important; font-size: 22px !important; font-weight: 600 !important; border-radius: 15px !important; direction: rtl !important; }}
        [data-testid="stFileUploader"] {{ background-color: rgba(255, 165, 0, 0.25) !important; border: 3px dashed #FFA500 !important; border-radius: 20px !important; padding: 20px !important; }}
        .stTabs [data-baseweb="tab"] {{ background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; color: white !important; padding: 10px 30px; font-size: 24px !important; }}
        .stTabs [aria-selected="true"] {{ background-color: #FFA500 !important; }}
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

# --- التبويب الأول: محول الجداول المطور (ملف PDF واحد = ورقة Excel واحدة) ---
with tab1:
    st.markdown("<p>رفع ملفات PDF لتحويل كل ملف إلى شيت واحد مستقل</p>", unsafe_allow_html=True)
    # تفعيل خاصية رفع أكثر من ملف في نفس الوقت
    pdf_files = st.file_uploader("ارفع ملفات PDF (يمكنك رفع عدة ملفات معاً)", type=["pdf"], key="pdf_multi", accept_multiple_files=True)
    
    if pdf_files:
        for uploaded_pdf in pdf_files:
            try:
                with st.spinner(f'جاري معالجة: {uploaded_pdf.name} ...'):
                    # قراءة جميع الجداول من كافة صفحات الملف الواحد
                    dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True)
                    
                    if dfs:
                        # دمج جداول الملف الواحد في جدول واحد
                        final_df = pd.concat([df.replace([float('inf'), float('-inf')], 0).fillna('') for df in dfs], ignore_index=True)
                        final_df = final_df.dropna(how='all', axis=0).reset_index(drop=True)
                        
                        st.write(f"✅ تم دمج محتويات {uploaded_pdf.name} في جدول واحد.")
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                            sheet_name = 'Data_Sheet'
                            final_df.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                            workbook  = writer.book
                            worksheet = writer.sheets[sheet_name]
                            
                            # التنسيقات والحدود
                            border_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFA500', 'color': 'white', 'border': 1, 'align': 'center'})
                            
                            # تطبيق الحدود
                            for row_num, row_data in enumerate(final_df.values):
                                for col_num, col_data in enumerate(row_data):
                                    worksheet.write(row_num + 1, col_num, col_data, border_fmt)
                            
                            # تطبيق رأس الجدول وضبط العرض
                            for col_num, value in enumerate(final_df.columns.values):
                                worksheet.write(0, col_num, value, header_fmt)
                                worksheet.set_column(col_num, col_num, 20)
                        
                        # زر تحميل مخصص لكل ملف يتم رفعه
                        st.download_button(
                            label=f"📥 تحميل إكسيل ملف: {uploaded_pdf.name}",
                            data=output.getvalue(),
                            file_name=f"Excel_{uploaded_pdf.name.split('.')[0]}.xlsx",
                            key=f"btn_{uploaded_pdf.name}"
                        )
                        st.divider() # فاصل بين الملفات المرفوعة
            except Exception as e:
                st.error(f"خطأ في معالجة {uploaded_pdf.name}: {e}")

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
