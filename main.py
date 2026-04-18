import streamlit as st
import tabula
import pandas as pd
import io
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. وظائف التنسيق البصري المتقدم
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_styled_interface(png_file):
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
    
    /* صندوق العمل الرئيسي */
    .main .block-container {{
        background-color: rgba(0, 0, 0, 0.4) !important;
        padding: 60px !important;
        border-radius: 30px !important;
        margin-top: 50px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
        max-width: 1100px !important;
    }}

    /* النصوص باللون الأبيض وحجم مضاعف */
    h1 {{
        font-size: 80px !important;
        color: #FFFFFF !important;
        font-weight: 900 !important;
        text-shadow: 4px 4px 10px #000000 !important;
        margin-bottom: 30px !important;
    }}
    
    p, span, label, .stMarkdown {{
        font-size: 40px !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 5px #000000 !important;
        line-height: 1.8 !important;
    }}

    /* التعديل الجديد: جعل مستطيل الرفع برتقالي شفاف */
    [data-testid="stFileUploader"] {{
        background-color: rgba(255, 165, 0, 0.3) !important; /* لون برتقالي شفاف */
        border: 3px dashed #FFA500 !important; /* إطار برتقالي منقط */
        border-radius: 20px !important;
        padding: 20px !important;
    }}

    /* تغيير لون أيقونة الرفع والنص داخل المستطيل للأبيض */
    [data-testid="stFileUploader"] section button {{
        background-color: #FFA500 !important;
        color: white !important;
    }}

    /* ضبط اتجاه النص للعربية */
    .stApp, .stMarkdown, .stTitle, div {{
        direction: rtl !important;
        text-align: right !important;
    }}
    </style>
    '''
    st.markdown(style_code, unsafe_allow_html=True)

# تطبيق التنسيق
try:
    set_styled_interface('background.jpg')
except:
    pass

# 3. واجهة التطبيق
st.markdown("<h1>📄 محول ملفات PDF</h1>", unsafe_allow_html=True)
st.markdown("<p>أهلاً بك يا أستاذ عبدين. ارفع ملفك الآن في المستطيل البرتقالي أدناه.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري المعالجة...'):
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            if len(dfs) > 0:
                st.success("✅ تم الاستخراج بنجاح.")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        st.subheader(f"📊 الجدول {i+1}")
                        st.dataframe(df, use_container_width=True)
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                
                st.download_button(
                    label="📥 تحميل ملف Excel",
                    data=output.getvalue(),
                    file_name="Converted_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

st.markdown("<br><br><br><p style='text-align: center; font-size: 50px; color: white; text-shadow: 3px 3px 8px #000;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
