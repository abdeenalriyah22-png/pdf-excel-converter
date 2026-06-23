import streamlit as st
import pandas as pd
import tabula
import io

st.set_page_config(page_title="المحاسب الذكي Pro", layout="wide")

# التصميم (النيون + النبض) - وضعناه في أعلى الكود لضمان عمله
st.markdown("""
<style>
    div.stButton > button { 
        border: 2px solid #28a745 !important; 
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); } 100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); } }
    [data-testid="stFileUploader"] { border: 2px solid #28a745 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 المحاسب الذكي Pro")

uploaded_file = st.file_uploader("اسحب ملف PDF هنا", type=["pdf"])

if uploaded_file and st.button("بدء المعالجة"):
    with st.spinner("جاري دمج البيانات العربية..."):
        try:
            # استخدام tabula مع خيار lattice للتعامل مع الجداول
            tables = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True, lattice=True, encoding='utf-8')
            
            if tables:
                # دمج كل الصفحات في جدول واحد
                combined_df = pd.concat(tables, ignore_index=True)
                
                output = io.BytesIO()
                combined_df.to_excel(output, index=False)
                st.download_button("📥 تحميل الإكسل", output.getvalue(), "Converted_Data.xlsx")
                st.success("تمت المعالجة بنجاح!")
            else:
                st.error("لم يتم العثور على جداول واضحة.")
        except Exception as e:
            st.error(f"خطأ: {e}")
