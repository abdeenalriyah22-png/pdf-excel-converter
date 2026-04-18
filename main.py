import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. كود الخلفية (مباشر ومبسط)
# ملاحظة: تأكد من رفع صورة باسم background.jpg في حسابك
img_url = "https://raw.githubusercontent.com/abdeenalriyadh22-png/pdf-excel-converter/main/background.jpg"

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{img_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

/* حاوية العمل - جعلتها أكثر شفافية (0.7) لتظهر الخلفية بوضوح */
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.7); 
    padding: 3rem;
    border-radius: 20px;
    margin-top: 50px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}}

/* تنسيق النصوص لليمين */
h1, h2, h3, p, span, .stMarkdown {{
    direction: rtl;
    text-align: right;
    color: #000000 !important;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. محتوى التطبيق
st.title("📄 محول PDF إلى Excel المحترف")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً.")

uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

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
            else:
                st.warning("⚠️ لم يتم العثور على جداول نصية.")
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: black;'><b>الفصل في الذمة.. الوصل في الأمانة</b></p>", unsafe_allow_html=True)
