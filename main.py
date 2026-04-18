import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة (يجب أن تكون أول سطر بعد الـ import)
st.set_page_config(page_title="محول PDF إلى Excel", layout="wide")

# 2. كود إضافة خلفية الصورة وتنسيق الواجهة (CSS)
page_bg_img = """
<style>
/* تعيين خلفية الموقع كاملة */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1454165833767-0220eb99c3e4?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* شفافية رأس الصفحة */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* حاوية المحتوى الرئيسي لتكون واضحة */
.main .block-container {
    background-color: rgba(255, 255, 255, 0.9); /* خلفية بيضاء شفافة للكلام */
    padding: 3rem;
    border-radius: 20px;
    margin-top: 50px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

/* تنسيق العناوين لتظهر باللون الأسود الواضح */
h1, h2, h3, p {
    color: #1E1E1E !important;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# 3. عنوان التطبيق
st.title("📄 محول PDF إلى Excel المحترف")
st.write("قم برفع ملف الـ PDF الخاص بك، وسيقوم النظام باستخراج الجداول وتحويلها إلى إكسل فوراً.")

# 4. رفع الملف
uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        with st.spinner('جاري معالجة الملف واستخراج البيانات...'):
            # قراءة الجداول من الـ PDF
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            
            if len(dfs) > 0:
                st.success(f"✅ ممتاز! تم العثور على {len(dfs)} جدول.")
                
                # إنشاء ملف إكسل في الذاكرة
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        # عرض معاينة للجدول
                        st.subheader(f"📊 معاينة الجدول رقم {i+1}")
                        st.dataframe(df)
                        
                        # حفظ كل جدول في صفحة (Sheet) مستقلة
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
                st.warning("⚠️ لم يتم العثور على جداول واضحة في هذا الملف. تأكد أن الـ PDF يحتوي على جداول نصية وليس صوراً.")
                
    except Exception as e:
        st.error(f"❌ حدث خطأ تقني: {e}")
        st.info("ملاحظة: تأكد من إضافة ملف packages.txt في GitHub ليتمكن المحرك من العمل بنجاح.")

# تذييل الصفحة
st.markdown("---")
st.markdown("<p style='text-align: center;'>الفصل في الذمة.. الوصل في الأمانة</p>", unsafe_allow_html=True)
