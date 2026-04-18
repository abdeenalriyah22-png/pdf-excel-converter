import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة (يجب أن يكون أول سطر)
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. رابط الصورة المباشر من حسابك في GitHub
# قمت بضبط الرابط ليكون "خام" (Raw) لضمان القراءة
img_url = "https://raw.githubusercontent.com/abdeenalriyadh22-png/pdf-excel-converter/main/background.jpg"

st.markdown(
    f"""
    <style>
    /* إجبار التطبيق بالكامل على استخدام الصورة كخلفية */
    .stApp {{
        background-image: url("{img_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* جعل رأس الصفحة والقوائم شفافة تماماً */
    header, [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0) !important;
    }}

    /* جعل الحاوية الرئيسية شفافة */
    [data-testid="stAppViewContainer"] {{
        background-color: transparent !important;
    }}

    /* صندوق العمل - أبيض شفاف ليكون الكلام واضحاً جداً */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 3rem !important;
        border-radius: 20px !important;
        margin-top: 50px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3) !important;
        max-width: 900px !important;
    }}

    /* توحيد الخطوط والمحاذاة لليمين باللون الأسود */
    h1, h2, h3, p, span, div {{
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 3. واجهة التطبيق
st.title("📄 محول PDF إلى Excel المحترف")
st.write(f"مرحباً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا وستجده تحول في ثوانٍ.")

# 4. رفع ومعالجة الملفات
uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري قراءة الجداول...'):
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
