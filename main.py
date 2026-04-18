import streamlit as st
import tabula
import pandas as pd
import io
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. وظيفة لتحويل صورة محليا أو من رابط إلى كود Base64 لضمان الظهور
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 3rem;
        border-radius: 20px;
        margin-top: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}

    h1, h2, p, span {{
        direction: rtl;
        text-align: right;
        color: #000000 !important;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# استدعاء الخلفية (تأكد أن الملف background.jpg موجود في نفس المجلد بجانب main.py)
try:
    set_background('background.jpg')
except:
    st.warning("جاري تحميل التنسيقات الفنية...")

# 3. محتوى التطبيق
st.title("📄 محول PDF إلى Excel المحترف")
st.write(f"أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً.")

uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري معالجة البيانات...'):
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            if len(dfs) > 0:
                st.success(f"✅ تم العثور على {len(dfs)} جدول.")
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        st.subheader(f"📊 معاينة الجدول رقم {i+1}")
                        st.dataframe(df)
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                
                st.download_button(
                    label="📥 تحميل ملف Excel الجاهز",
                    data=output.getvalue(),
                    file_name="Converted_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

st.markdown("---")
st.markdown("<p style='text-align: center;'><b>الفصل في الذمة.. الوصل في الأمانة</b></p>", unsafe_allow_html=True)
