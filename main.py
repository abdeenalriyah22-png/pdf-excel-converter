import streamlit as st
import tabula
import pandas as pd
import io
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. وظائف الخلفية والتنسيق الفائق الوضوح
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
    
    /* شريط الأدوات العلوي - جعله شفافاً ليعيد الأزرار */
    [data-testid="stHeader"] {{
        background: rgba(255, 255, 255, 0.1) !important;
    }}

    /* صندوق العمل الرئيسي - جعله ناصع البياض وبدون شفافية لضمان الوضوح */
    .main .block-container {{
        background-color: #ffffff !important;
        padding: 50px !important;
        border-radius: 15px !important;
        margin-top: 40px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5) !important;
        max-width: 950px !important;
    }}

    /* تكبير العناوين والخطوط وجعلها سوداء تماماً */
    h1 {{
        font-size: 45px !important;
        color: #000000 !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
    }}
    
    p, span, label, .stMarkdown {{
        font-size: 22px !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
        line-height: 1.6 !important;
    }}

    /* ضبط اتجاه النص للعربية */
    .stApp, .stMarkdown, .stTitle, div {{
        direction: rtl !important;
        text-align: right !important;
    }}

    /* تحسين شكل زر الرفع ليكون واضحاً */
    .stFileUploader section {{
        background-color: #f8f9fa !important;
        border: 2px dashed #000000 !important;
        border-radius: 10px !important;
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
st.title("📄 محول ملفات PDF إلى Excel")
st.write("مرحباً بك يا أستاذ عبدين. ارفع ملفك الآن وستظهر لك البيانات بوضوح تام.")

uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري المعالجة...'):
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            if len(dfs) > 0:
                st.success(f"✅ تم استخراج {len(dfs)} جدول بنجاح.")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        st.subheader(f"📊 معاينة الجدول {i+1}")
                        st.dataframe(df, use_container_width=True)
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                
                st.download_button(
                    label="📥 تحميل ملف Excel الجاهز",
                    data=output.getvalue(),
                    file_name="Converted_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"حدث خطأ أثناء القراءة: {e}")

st.markdown("---")
st.markdown("<h2 style='text-align: center; color: #000;'>الفصل في الذمة.. الوصل في الأمانة</h2>", unsafe_allow_html=True)
