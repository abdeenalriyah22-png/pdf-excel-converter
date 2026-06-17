import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة المحدث ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول",
        "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب ملفات الـ PDF هنا",
        "btn_convert": "بدأ تحويل: ", "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي", "loading": "جاري المعالجة...",
        "success": "🚀 اكتمل بنجاح!", "download_excel": "📥 تحميل ملف Excel", "download_txt": "📥 تحميل النص",
        "no_tables": "⚠️ لم نكتشف جداول رقمية. جرب الـ OCR.", "no_text": "لم نكتشف نصوصاً.", "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    # ... (يمكنك إضافة باقي اللغات بنفس النمط)
}

# --- 3. اختيار اللغة (في الأعلى كما طلبت) ---
selected_lang = st.selectbox("🌐", ["العربية"], index=0, key="lang_selector")
lang = translations[selected_lang]

# --- 4. التنسيق (النيون + التصحيح) ---
st.markdown(f"""
<style>
    .stApp {{ direction: {lang['direction']} !important; text-align: {lang['align']} !important; background-color: #07090e !important; color: #ffffff !important; }}
    div[data-testid="stSelectbox"] {{ width: 250px !important; margin-{lang['align']}: 0 !important; }}
    [data-testid="stFileUploader"] {{ border: 2px solid #2ea043 !important; border-radius: 15px !important; }}
    .stButton > button {{ border: 2px solid #2ea043 !important; color: #ffffff !important; background: transparent !important; border-radius: 50px !important; }}
</style>
""", unsafe_allow_html=True)

# --- 5. منطق معالجة الملفات المدمج ---
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

with tab1:
    pdf_files = st.file_uploader(lang["up"], type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        for uploaded_pdf in pdf_files:
            if st.button(f"{lang['btn_convert']}{uploaded_pdf.name}"):
                with st.spinner(lang["loading"]):
                    try:
                        # استخدام منطق المعالجة القوي (Lattice=True)
                        dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                        if dfs:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                current_row = 0
                                for df in dfs:
                                    df = df.fillna('').replace([float('inf'), float('-inf')], 0)
                                    df.to_excel(writer, index=False, startrow=current_row, sheet_name='Data')
                                    current_row += len(df) + 2
                            st.success(lang["success"])
                            st.download_button(lang["download_excel"], output.getvalue(), f"Excel_{uploaded_pdf.name}.xlsx", "application/vnd.ms-excel")
                        else:
                            st.warning(lang["no_tables"])
                    except Exception as e:
                        st.error(f"Error: {e}")

with tab2:
    ocr_file = st.file_uploader("ارفع صورة أو ملف PDF للمسح الضوئي", type=["jpg", "png", "pdf"])
    if ocr_file and st.button(lang["btn_ocr"]):
        try:
            full_text = ""
            if ocr_file.type == "application/pdf":
                doc = fitz.open(stream=ocr_file.read(), filetype="pdf")
                for page in doc:
                    text = page.get_text()
                    full_text += text if text.strip() else pytesseract.image_to_string(Image.frombytes("RGB", [page.get_pixmap().width, page.get_pixmap().height], page.get_pixmap().samples), lang='ara+eng')
            else:
                full_text = pytesseract.image_to_string(Image.open(ocr_file), lang='ara+eng')
            st.text_area("النص المستخرج:", value=full_text, height=300)
        except Exception as e:
            st.error(f"OCR Error: {e}")
