import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. إعدادات الخلفية (تأكد أن اسم الصورة في GitHub هو background.jpg)
image_filename = "background.jpg" 
github_user = "abdeenalriyadh22-png"
repo = "pdf-excel-converter"

# الرابط المباشر للصورة من سيرفرات GitHub
img_url = f"https://raw.githubusercontent.com/{github_user}/{repo}/main/{image_filename}"

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("{img_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* تجعل واجهة العمل شفافة قليلاً لتظهر الخلفية من خلفها */
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.85); 
    padding: 3rem;
    border-radius: 20px;
    margin-top: 50px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}}

/* محاذاة النصوص لليمين */
h1, h2, p, span {{
    direction: rtl;
    text-align: right;
    color: #1E1E1E !important;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. محتوى التطبيق
st.title("📄 محول PDF إلى Excel")
st.write(f"أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً.")

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
st.markdown("<p style='text-align: center;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
