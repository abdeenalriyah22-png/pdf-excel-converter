import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import tabula
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# كود جوجل أدسنس
components.html("""<meta name="google-adsense-account" content="ca-pub-1091631464795781">""", height=0)

# وظيفة تصحيح الحروف العربية (الجزء الأهم لإنهاء مشكلة النصوص المقلوبة)
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# قاموس اللغات
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "btn": "بدء المعالجة", "download": "تحميل الإكسل"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "btn": "Start Processing", "download": "Download Excel"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "btn": "شروع کریں", "download": "ایکسل ڈاؤن لوڈ کریں"}
}

selected_lang = st.selectbox("🌐", ["العربية", "English", "اردو"])
lang = translations[selected_lang]

# التصميم (خلفية Off-white مع أزرار نابضة)
st.markdown(f"""
<style>
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']}; }}
    h1 {{ color: #202124 !important; text-align: {lang['align']}; }}
    div.stButton > button {{ 
        border: 2px solid #28a745 !important; 
        background: white !important;
        color: #28a745 !important;
        animation: pulse 2s infinite; 
    }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }} }}
</style>
""", unsafe_allow_html=True)

st.title(lang["title"])

# المعالجة الذكية
files = st.file_uploader("ارفع ملف PDF", type=["pdf"], accept_multiple_files=True)
if files:
    for f in files:
        if st.button(f"{lang['btn']} {f.name}"):
            with st.spinner("جاري المعالجة وتصحيح النصوص..."):
                try:
                    # قراءة الجداول
                    dfs = tabula.read_pdf(f, pages='all', multiple_tables=True)
                    output = io.BytesIO()
                    
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for i, df in enumerate(dfs):
                            # تصحيح أعمدة وخلايا الجدول (السر هنا)
                            df.columns = [fix_arabic(str(col)) for col in df.columns]
                            df = df.applymap(fix_arabic)
                            
                            df.to_excel(writer, index=False, sheet_name=f'Sheet{i+1}')
                            writer.sheets[f'Sheet{i+1}'].right_to_left()
                    
                    st.success("تم!")
                    st.download_button(lang["download"], output.getvalue(), f"Excel_{f.name}.xlsx")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")

# الإعلانات
components.html("""<div style="text-align:center;"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-1091631464795781" data-ad-slot="8159670732"></ins></div>""", height=100)
