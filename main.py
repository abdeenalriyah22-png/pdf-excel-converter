import streamlit as st
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import shutil

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي - عبادين", layout="wide")

# التحقق من وجود محرك OCR في النظام
tesseract_path = shutil.which("tesseract")

# 2. وظائف التنسيق والبصريات (CSS)
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_styled_interface(png_file):
    try:
        bin_str = get_base64(png_file)
        style_code = f'''
        <style>
        /* خلفية التطبيق الكاملة */
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* شريط الأدوات العلوي */
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0.3) !important;
        }}

        /* صندوق العمل الرئيسي */
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.4) !important;
            padding: 50px !important;
            border-radius: 30px !important;
            margin-top: 30px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
            max-width: 1200px !important;
        }}

        /* تنسيق النصوص (أبيض، كبير، بظلال سوداء) */
        h1 {{ 
            font-size: 70px !important; 
            color: #FFFFFF !important; 
            font-weight: 900 !important;
            text-shadow: 4px 4px 10px #000000 !important;
            text-align: right !important;
        }}
        
        p, label, .stMarkdown {{ 
            font-size: 35px !important; 
            color: #FFFFFF !important; 
            font-weight: 700 !important;
            text-shadow: 2px 2px 5px #000000 !important;
            text-align: right !important;
        }}

        /* تحسين صندوق النص المستخرج (خلفية بيضاء واضحة) */
        .stTextArea textarea {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            color: #000000 !important;
            font-size: 22px !important;
            font-weight: 600 !important;
            border-radius: 15px !important;
            direction: rtl !important;
        }}

        /* مستطيل الرفع البرتقالي الشفاف */
        [data-testid="stFileUploader"] {{
            background-color: rgba(255, 165, 0, 0.25) !important;
            border: 3px dashed #FFA500 !important;
            border-radius: 20px !important;
            padding: 20px !important;
        }}

        /* تنسيق التبويبات (Tabs) */
        .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            color: white !important;
            padding: 10px 30px;
            font-size: 24px !important;
        }}
        .stTabs [aria-selected="true"] {{ 
            background-color: #FFA500 !important; 
        }}

        /* محاذاة عامة لليمين */
        .stApp {{ direction: rtl !important; text-align: right !important; }}
        </style>
        '''
        st.markdown(style_code, unsafe_allow_html=True)
    except:
        pass

# تطبيق التنسيق باستخدام صورة الخلفية
set_styled_interface('background.jpg')

# 3. واجهة التطبيق
st.markdown("<h1>📄 المحاسب الذكي</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 جداول Excel", "🔍 استخراج نصوص"])

# --- التبويب الأول: محول الجداول مع الحدود ومعالجة الأخطاء ---
with tab1:
    st.markdown("<p>تحويل PDF إلى Excel (مع الحدود وحذف الصفوف الزائدة)</p>", unsafe_allow_html=True)
    pdf_file = st.file_uploader("ارفع ملف PDF للجداول", type=["pdf"], key="pdf_up")
    
    if pdf_file:
        try:
            with st.spinner('جاري معالجة الجداول وتنسيقها...'):
                dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
                if dfs:
                    st.success(f"تم العثور على {len(dfs)} جدول")
                    output = io.BytesIO()
                    
                    # إعداد خيار معالجة قيم NaN/Inf لتجنب توقف البرنامج
                    with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                        for i, df in enumerate(dfs):
                            # 1. تنظيف البيانات من القيم غير المدعومة والصفوف الفارغة
                            df = df.replace([float('inf'), float('-inf')], 0)
                            df = df.fillna('')
                            df = df.dropna(how='all', axis=0).reset_index(drop=True)
                            
                            sheet_name = f'Table_{i+1}'
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                            # 2. تنسيق الحدود (Borders) والرأس
                            workbook  = writer.book
                            worksheet = writer.sheets[sheet_name]
                            
                            border_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFA500', 'color': 'white', 'border': 1, 'align': 'center'})
                            
                            # كتابة البيانات مع الحدود
                            for row_num, row_data in enumerate(df.values):
                                for col_num, col_data in enumerate(row_data):
                                    worksheet.write(row_num + 1, col_num, col_data, border_fmt)
                            
                            # كتابة العناوين
                            for col_num, value in enumerate(df.columns.values):
                                worksheet.write(0, col_num, value, header_fmt)
                            
                            st.dataframe(df)
                    
                    st.download_button("📥 تحميل ملف Excel المنسق بالحدود", data=output.getvalue(), file_name="Smart_Accountant_Data.xlsx")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")

# --- التبويب الثاني: مستخرج النصوص المطور (عربي + إنجليزي) ---
with tab2:
    st.markdown("<p>استخراج النصوص من الصور (عربي + إنجليزي + أرقام)</p>", unsafe_allow_html=True)
    if not tesseract_path:
        st.error("⚠️ محرك OCR غير مثبت في السيرفر. يرجى التأكد من ملف packages.txt")
    
    img_file = st.file_uploader("ارفع صورة الفاتورة أو المستند", type=["jpg", "png", "jpeg"], key="img_up")
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="المعاينة", width=500)
        
        if st.button("ابدأ استخراج النص الآن"):
            try:
                with st.spinner('جاري قراءة البيانات...'):
                    # دعم اللغتين معاً
                    extracted_text = pytesseract.image_to_string(image, lang='ara+eng')
                    
                    if extracted_text.strip():
                        st.markdown("<p>النص المستخرج بوضوح:</p>", unsafe_allow_html=True)
                        st.text_area("", value=extracted_text, height=400)
                        st.download_button("📥 حفظ النص كملف", data=extracted_text, file_name="Extracted_Text.txt")
                    else:
                        st.warning("لم يتم العثور على نصوص واضحة في الصورة.")
            except Exception as e:
                st.error(f"خطأ في المعالجة: {e}")

# التذييل
st.markdown("<br><br><br><p style='text-align: center; font-size: 45px; color: white; text-shadow: 3px 3px 8px #000;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
