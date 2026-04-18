import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel المحترف", layout="wide")

# 2. كود الخلفية - قمت بتعديل الرابط ليكون "مباشراً" تماماً وتجاوز حماية المتصفح
img_url = "https://raw.githubusercontent.com/abdeenalriyadh22-png/pdf-excel-converter/main/background.jpg"

st.markdown(
    f"""
    <style>
    /* إجبار الخلفية على الظهور وتجاوز أي إعدادات سابقة */
    .stApp {{
        background: url("{img_url}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}

    /* جعل الطبقات المتوسطة شفافة 100% */
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stAppViewBlockContainer"] {{
        background-color: transparent !important;
    }}

    /* صندوق العمل - أبيض شفاف ليكون الكلام واضحاً */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 3rem !important;
        border-radius: 20px !important;
        margin-top: 50px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
        max-width: 900px !important;
    }}

    /* تنسيق الخطوط العربية واللون الأسود */
    h1, h2, p, span, div, .stMarkdown {{
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        font-weight: 500;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 3. واجهة البرنامج
st.title("📄 محول PDF إلى Excel")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً.")

uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري التحويل...'):
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
