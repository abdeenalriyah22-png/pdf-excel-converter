import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="محول PDF إلى Excel المحترف", layout="wide")

# 2. كود الخلفية المخصص بصورتك الخاصة
# ملاحظة: استبدل 'background.jpg' باسم صورتك التي رفعتها على GitHub
image_name = "background.jpg" 
user_github = "abdeenalriyadh22-png"
repo_name = "pdf-excel-converter"

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url("https://raw.githubusercontent.com/{user_github}/{repo_name}/main/{image_name}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

/* حاوية المحتوى لجعل النصوص واضحة فوق الصورة */
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.9);
    padding: 3rem;
    border-radius: 20px;
    margin-top: 50px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}}

/* تنسيق النصوص */
h1, h2, h3, p {{
    color: #1E1E1E !important;
    direction: rtl;
    text-align: right;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. واجهة البرنامج
st.title("📄 محول PDF إلى Excel")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً.")

# 4. منطق معالجة الملفات
uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري قراءة الجداول...'):
            # استخدام tabula لقراءة الجداول
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            
            if len(dfs) > 0:
                st.success(f"✅ تم العثور على {len(dfs)} جدول بنجاح.")
                
                # إعداد ملف الإكسل
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        st.subheader(f"📊 معاينة الجدول رقم {i+1}")
                        st.dataframe(df)
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                
                processed_data = output.getvalue()
                
                # زر التحميل
                st.download_button(
                    label="📥 تحميل ملف Excel الجاهز",
                    data=processed_data,
                    file_name="Converted_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ لم يتم العثور على جداول. تأكد من أن الملف يحتوي على جداول نصية.")
                
    except Exception as e:
        st.error(f"❌ حدث خطأ: {e}")
        st.info("تأكد من وجود ملف packages.txt وبه كلمة default-jre في حسابك على GitHub.")

# 5. التذييل (مبدأ العمل)
st.markdown("---")
st.markdown("<p style='text-align: center;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
