import streamlit as st
import tabula
import pandas as pd
import io
import base64

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. وظائف الخلفية والتنسيق المحسن
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_styled_interface(png_file):
    bin_str = get_base64(png_file)
    style_code = f'''
    <style>
    /* تعيين خلفية الموقع */
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* إظهار أزرار التحكم العليا بوضوح */
    [data-testid="stHeader"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px);
    }}

    /* صندوق العمل - تكبير وتحسين الرؤية بخلفية بيضاء مريحة */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.95) !important; /* خلفية بيضاء شبه كاملة لراحة العين */
        padding: 4rem !important;
        border-radius: 25px !important;
        margin-top: 30px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4) !important;
        max-width: 1000px !important;
    }}

    /* تكبير وتوضيح الخطوط العربية */
    h1 {{
        font-size: 42px !important;
        color: #1E1E1E !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }}
    
    p, span, label {{
        font-size: 20px !important; /* تكبير الخط الفرعي */
        color: #333333 !important;
        font-weight: 500 !important;
    }}

    /* محاذاة كل شيء لليمين */
    .stMarkdown, .stTitle, div {{
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

# 3. واجهة التطبيق المحسنة
st.title("📄 محول PDF إلى Excel المحترف")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا وسنقوم باستخراج الجداول فوراً وبوضوح تام.")

# منطقة الرفع
uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري التحليل واستخراج البيانات...'):
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            if len(dfs) > 0:
                st.success(f"✅ اكتملت المهمة! تم العثور على {len(dfs)} جدول.")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        st.subheader(f"📊 معاينة الجدول رقم {i+1}")
                        st.dataframe(df, use_container_width=True)
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                
                st.download_button(
                    label="📥 تحميل ملف Excel الجاهز",
                    data=output.getvalue(),
                    file_name="Converted_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ الملف لا يحتوي على جداول واضحة.")
    except Exception as e:
        st.error(f"خطأ تقني: {e}")

# التذييل
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>الفصل في الذمة.. الوصل في الأمانة</h3>", unsafe_allow_html=True)
