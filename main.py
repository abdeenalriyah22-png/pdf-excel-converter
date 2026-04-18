import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة (يجب أن يكون أول أمر برمي)
st.set_page_config(page_title="محول PDF إلى Excel المحترف", layout="wide")

# 2. كود الخلفية - استخدمنا رابطاً عالمياً مباشراً لضمان العمل 100%
# الصورة المختارة هي صورة مكتب محاسبة أنيق واحترافي
img_url = "https://images.unsplash.com/photo-1454165833767-0220eb99c3e4?q=80&w=2070&auto=format&fit=crop"

page_bg_img = f"""
<style>
/* تعيين الخلفية للموقع بالكامل */
[data-testid="stAppViewContainer"] {{
    background-image: url("{img_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* إخفاء خلفية رأس الصفحة لتظهر الصورة */
[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

/* تنسيق حاوية العمل (المربع الذي ترفع فيه الملفات) */
.main .block-container {{
    background-color: rgba(255, 255, 255, 0.85); /* أبيض شفاف */
    padding: 3rem;
    border-radius: 20px;
    margin-top: 50px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}}

/* توحيد تنسيق الخطوط والمحاذاة لليمين */
h1, h2, h3, p, span, .stMarkdown {{
    direction: rtl !important;
    text-align: right !important;
    color: #1E1E1E !important;
}}

/* تحسين شكل زر الرفع */
.stFileUploader {{
    direction: ltr; /* للحفاظ على شكل أيقونة الرفع */
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. واجهة البرنامج
st.title("📄 محول PDF إلى Excel المحترف")
st.write("أهلاً بك يا أستاذ عبدين. ارفع ملف الـ PDF هنا لاستخراج الجداول فوراً وبدقة.")

# 4. منطقة رفع ومعالجة الملفات
uploaded_file = st.file_uploader("اختر ملف PDF من جهازك", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري قراءة الجداول من الملف...'):
            # قراءة الجداول باستخدام مكتبة tabula
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            
            if len(dfs) > 0:
                st.success(f"✅ تم العثور على {len(dfs)} جدول بنجاح.")
                
                # إعداد ملف الإكسل في الذاكرة
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        st.subheader(f"📊 معاينة الجدول رقم {i+1}")
                        st.dataframe(df)
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                
                # زر تحميل ملف الإكسل الناتج
                st.download_button(
                    label="📥 تحميل ملف Excel الجاهز",
                    data=output.getvalue(),
                    file_name="Converted_Data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ لم يتم العثور على جداول واضحة. تأكد أن الملف يحتوي على جداول نصية قابلة للقراءة.")
                
    except Exception as e:
        st.error(f"❌ حدث خطأ تقني: {e}")
        st.info("نصيحة: تأكد من وجود ملف packages.txt وبه كلمة default-jre في حسابك على GitHub.")

# 5. التذييل (مبدأ العمل الخاص بك)
st.markdown("---")
st.markdown("<p style='text-align: center; font-weight: bold;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
