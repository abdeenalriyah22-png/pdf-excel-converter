import streamlit as st
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي", layout="wide")

# --- الأدوات الأساسية ---
st.title("📊 المحاسب الذكي")
st.sidebar.title("🛠️ الأدوات")

menu = st.sidebar.radio("اختر العملية:", ["📊 تحويل PDF إلى إكسيل", "🔍 استخراج النصوص (OCR)"])

# --- منطق التحويل (النسخة المستقرة) ---
if menu == "📊 تحويل PDF إلى إكسيل":
    st.subheader("تحويل جداول PDF إلى Excel")
    pdf_file = st.file_uploader("ارفع ملف الـ PDF", type=["pdf"])
    if pdf_file and st.button("بدء التحويل"):
        with st.spinner("جاري المعالجة..."):
            dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
            if dfs:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for i, df in enumerate(dfs):
                        df.to_excel(writer, sheet_name=f'Table_{i+1}', index=False)
                st.success("تم التحويل بنجاح!")
                st.download_button("📥 تحميل ملف Excel", data=output.getvalue(), file_name="converted.xlsx")
            else:
                st.warning("لم يتم العثور على جداول.")

# --- منطق استخراج النص (النسخة المستقرة) ---
elif menu == "🔍 استخراج النصوص (OCR)":
    st.subheader("استخراج النصوص من الصور/المستندات")
    img_file = st.file_uploader("ارفع صورة أو ملف PDF", type=["jpg", "png", "pdf"])
    if img_file and st.button("استخراج النص"):
        with st.spinner("جاري القراءة..."):
            try:
                # معالجة بسيطة لاستخراج النص
                if img_file.type == "application/pdf":
                    doc = fitz.open(stream=img_file.read(), filetype="pdf")
                    text = "".join([page.get_text() for page in doc])
                else:
                    text = pytesseract.image_to_string(Image.open(img_file), lang='ara+eng')
                
                st.text_area("النص المستخرج:", value=text, height=300)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
