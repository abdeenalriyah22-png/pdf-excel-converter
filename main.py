import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. رابط الصورة المباشر (استخدمنا رابط خارجي مضمون)
img_url = "https://images.unsplash.com/photo-1454165833767-0220eb99c3e4?q=80&w=2070&auto=format&fit=crop"

page_bg_img = f"""
<style>
/* إجبار الخلفية على الظهور في أعمق طبقة */
.stApp {{
    background-image: url("{img_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* جعل الطبقات التي فوقها شفافة */
[data-testid="stAppViewContainer"] {{
    background-color: rgba(0,0,0,0);
}}

/* تنسيق حاوية العمل لتكون بيضاء شفافة وواضحة */
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.9) !important;
    padding: 3rem !important;
    border-radius: 20px !important;
    margin-top: 50px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2) !important;
}}

/* تنسيق النصوص باللون الأسود والمحاذاة لليمين */
h1, h2, p, span {{
    direction: rtl !important;
    text-align: right !important;
    color: #000000 !important;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. واجهة التطبيق
st.title("📄 محول PDF إلى Excel المحترف")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً.")

uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري معالجة الجداول...'):
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
                st.warning("⚠️ لم يتم العثور على جداول.")
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

st.markdown("---")
st.markdown("<p style='text-align: center;'><b>الفصل في الذمة.. الوصل في الأمانة</b></p>", unsafe_allow_html=True)
