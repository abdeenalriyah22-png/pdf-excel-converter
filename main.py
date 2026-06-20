import streamlit as st
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz
import streamlit.components.v1 as components

# إعدادات الصفحة
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# قاموس اللغات
translations = {
    "العربية": {"dir": "rtl", "align": "right", "pos": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF/CSV إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب ملف PDF أو CSV أو صورة", "btn": "بدء المعالجة", "copy": "📋 نسخ النص بالكامل"},
}

selected_lang = st.selectbox("🌐", ["العربية"], index=0, key="lang_selector")
lang = translations[selected_lang]

# --- التصميم الشامل ---
st.markdown(f"""
<style>
    #MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stSelectbox"] {{ position: fixed !important; top: 15px !important; {lang['pos']}: 20px !important; z-index: 9999 !important; width: 150px !important; }}
    
    .stApp {{ background-color: #F8F9FA !important; direction: {lang['dir']} !important; }}
    .main-container {{ max-width: 900px; margin: 0 auto; padding-top: 100px !important; }}
    
    h1 {{ 
        text-align: {lang['align']} !important; 
        color: #202124 !important; 
        text-shadow: 0 0 10px #28a745, 0 0 20px #28a745 !important; 
    }}
    p {{ text-align: {lang['align']} !important; color: #202124 !important; }}
    
    [data-testid="stFileUploader"] {{ border: 2px solid #28a745 !important; border-radius: 12px !important; box-shadow: 0 0 15px rgba(40, 167, 69, 0.3) !important; background: #ffffff !important; }}
    div.stButton > button {{ border: 2px solid #28a745 !important; transition: 0.3s; }}
    div.stButton > button:active {{ box-shadow: 0 0 20px #28a745 !important; }}
    
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #888; font-size: 12px; border-top: 1px solid #ddd; background: #F8F9FA; }}
</style>
""", unsafe_allow_html=True)

# محتوى الصفحة
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

    with tab1:
        files = st.file_uploader(lang["up"], type=["pdf", "csv"], accept_multiple_files=True)
        if files:
            for f in files:
                if st.button(f"{lang['btn']}", key=f"btn1_{f.name}"):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        if f.name.endswith('.pdf'):
                            dfs = tabula.read_pdf(f, pages='all', multiple_tables=True, lattice=True)
                            for i, df in enumerate(dfs): df.to_excel(writer, index=False, sheet_name=f'Sheet{i+1}')
                        else:
                            pd.read_csv(f).to_excel(writer, index=False, sheet_name='Sheet1')
                    st.download_button("📥 تحميل", output.getvalue(), f"{f.name.split('.')[0]}.xlsx")

    with tab2:
        file = st.file_uploader(lang["up"], type=["jpg", "png", "pdf"])
        if file and st.button(f"{lang['btn']}", key="btn2"):
            with st.spinner("جاري المعالجة..."):
                try:
                    full_text = ""
                    if file.type == "application/pdf":
                        doc = fitz.open(stream=file.read(), filetype="pdf")
                        for page in doc:
                            pix = page.get_pixmap()
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            full_text += pytesseract.image_to_string(img, lang='ara+eng')
                    else:
                        full_text = pytesseract.image_to_string(Image.open(file), lang='ara+eng')
                    
                    st.text_area("النص:", value=full_text, height=300)
                    if full_text.strip():
                        copy_btn_code = f'<button style="padding:10px; background:#28a745; color:white; border:none; border-radius:5px;" onclick="navigator.clipboard.writeText(`{full_text.replace("`", "")}`)">📋 {lang["copy"]}</button>'
                        components.html(copy_btn_code, height=50)
                except Exception:
                    st.error("خطأ: يرجى التأكد من أن الملف سليم.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">المحاسب الذكي Pro | جميع الحقوق محفوظة © 2026</div>', unsafe_allow_html=True)
