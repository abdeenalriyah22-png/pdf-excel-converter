import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. كود إجبار الخلفية وتدمير اللون الأبيض الافتراضي
img_url = "https://images.unsplash.com/photo-1454165833767-0220eb99c3e4?q=80&w=2070&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
    /* استهداف الطبقة الأم لتكون هي الصورة */
    .stApp {{
        background: url("{img_url}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    /* جعل كل الحاويات والطبقات شفافة تماماً بنسبة 100% */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stAppViewBlockContainer"],
    .main,
    .stDeployButton {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* صندوق العمل - أبيض بوضوح عالي للقراءة */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 40px !important;
        border-radius: 15px !important;
        margin-top: 50px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        max-width: 850px !important;
    }}

    /* تنسيق الخطوط */
    h1, h2, p, span, div {{
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 3. واجهة البرنامج
st.title("📄 محول PDF إلى Excel المحترف")
st.write(f"مرحباً بك يا أستاذ عبدين. ارفع الملف الآن وستجده تحول في ثوانٍ.")

uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري استخراج البيانات...'):
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
st.markdown("<p style='text-align: center; font-weight: bold;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
