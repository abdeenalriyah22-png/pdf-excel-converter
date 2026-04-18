import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة - وضعناها في البداية لضمان استجابة السيرفر
st.set_page_config(page_title="محول PDF إلى Excel المحترف", layout="wide")

# 2. كود إجبار الخلفية على الظهور وتجاوز إعدادات الثيم (Force Background)
img_url = "https://images.unsplash.com/photo-1454165833767-0220eb99c3e4?q=80&w=2070&auto=format&fit=crop"

page_bg_img = f"""
<style>
/* استهداف الحاوية الكبرى للموقع وإجبارها على عرض الصورة */
div[data-testid="stAppViewContainer"] {{
    background-image: url("{img_url}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}

/* جعل جميع الطبقات المتوسطة شفافة تماماً لرؤية الخلفية */
div[data-testid="stAppViewBlockContainer"], 
div[data-testid="stVerticalBlock"],
[data-testid="stHeader"],
[data-testid="stToolbar"] {{
    background-color: transparent !important;
    background: transparent !important;
}}

/* إنشاء مربع العمل الأبيض الشفاف ليكون الكلام واضحاً */
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.85) !important;
    padding: 3rem !important;
    border-radius: 20px !important;
    margin-top: 60px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    max-width: 900px !important;
}}

/* تنسيق النصوص والمحاذاة */
h1, h2, h3, p, span, .stMarkdown {{
    direction: rtl !important;
    text-align: right !important;
    color: #000000 !important;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. واجهة البرنامج
st.title("📄 محول PDF إلى Excel المحترف")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً وبدقة.")

# 4. منطقة معالجة الملفات
uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري قراءة الجداول من الملف...'):
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            
            if len(dfs) > 0:
                st.success(f"✅ تم العثور على {len(dfs)} جدول بنجاح.")
                
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
                st.warning("⚠️ لم يتم العثور على جداول نصية واضحة.")
                
    except Exception as e:
        st.error(f"❌ حدث خطأ تقني: {e}")

# 5. التذييل
st.markdown("---")
st.markdown("<p style='text-align: center; font-weight: bold;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
