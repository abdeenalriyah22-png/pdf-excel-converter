import streamlit as st
import pandas as pd
import pdfplumber
import io

st.set_page_config(page_title="المحاسب الذكي Pro", layout="wide")

# CSS - النيون والنبض
st.markdown("""
<style>
    div.stButton > button { border: 2px solid #28a745 !important; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); } 100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); } }
</style>
""", unsafe_allow_html=True)

st.title("📊 المحاسب الذكي Pro")

uploaded_file = st.file_uploader("اسحب ملف الـ PDF هنا", type=["pdf"])

if uploaded_file and st.button("بدء المعالجة"):
    with st.spinner("جاري معالجة البيانات باستخدام محرك pdfplumber..."):
        try:
            all_rows = []
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        all_rows.extend(table)
            
            if all_rows:
                df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
                output = io.BytesIO()
                df.to_excel(output, index=False)
                st.download_button("📥 تحميل الإكسل", output.getvalue(), "Jard_Report.xlsx")
                st.success("تم استخراج الجدول بنجاح!")
            else:
                st.error("لم يتم العثور على جداول.")
        except Exception as e:
            st.error(f"خطأ: {e}")
