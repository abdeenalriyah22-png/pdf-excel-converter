import streamlit as st
import tabula
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="محول الجداول الاحترافي", layout="wide")

st.title("📄 محول PDF إلى Excel")
st.write("قم برفع ملف الـ PDF وسيقوم النظام باستخراج الجداول فوراً.")

# 2. أداة رفع الملف
uploaded_file = st.file_uploader("اختر ملف PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # شريط انتظار أثناء المعالجة
        with st.spinner('انتظر قليلاً.. جاري استخراج الجداول'):
            # استخدام tabula لقراءة كل الصفحات
            tables = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)
            
            if len(tables) > 0:
                st.success(f"ممتاز! تم العثور على {len(tables)} جدول.")
                
                # تحضير ملف الإكسل في الذاكرة
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(tables):
                        st.write(f"📊 معاينة الجدول رقم {i+1}:")
                        st.dataframe(df) # عرض الجدول للمستخدم
                        df.to_excel(writer, sheet_name=f'Sheet_{i+1}', index=False)
                
                # 3. زر التحميل النهائي
                st.download_button(
                    label="✅ تحميل ملف Excel الجاهز",
                    data=output.getvalue(),
                    file_name="Converted_Expenses.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("لم يتم العثور على جداول واضحة في هذا الملف.")
                
    except Exception as e:
        st.error(f"حدث خطأ تقني: {e}")
        st.info("ملاحظة: تأكد من تثبيت Java على جهازك ليعمل المحرك بنجاح.")