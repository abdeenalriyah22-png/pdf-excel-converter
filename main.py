import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. قاموس الترجمة ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "subtitle": "النظام السحابي المطور لمعالجة الجداول", "tab1": "📊 تحويل PDF إلى Excel", "tab2": "🔍 استخراج النصوص (OCR)", "up": "اسحب أو اختر ملف PDF", "btn": "ابدأ العملية", "loading": "جاري التحويل...", "success": "🚀 اكتمل التحويل!", "download": "📥 تحميل الملف"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "subtitle": "Advanced cloud system for data", "tab1": "📊 Convert PDF to Excel", "tab2": "🔍 Smart Text Extraction (OCR)", "up": "Drag or choose PDF file", "btn": "Start Process", "loading": "Converting...", "success": "🚀 Conversion complete!", "download": "📥 Download file"},
    "Français": {"dir": "ltr", "align": "left", "title": "📊 Comptable Intelligent Pro", "subtitle": "Système cloud avancé pour données", "tab1": "📊 Convertir PDF en Excel", "tab2": "🔍 Extraction de texte (OCR)", "up": "Glissez ou choisissez un PDF", "btn": "Démarrer", "loading": "Conversion en cours...", "success": "🚀 Conversion réussie!", "download": "📥 Télécharger le fichier"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "subtitle": "ڈیٹا پروسیسنگ کا جدید نظام", "tab1": "📊 PDF کو ایکسل میں بدلیں", "tab2": "🔍 ٹیکسٹ نکالنا (OCR)", "up": "فائل یہاں ڈریگ کریں", "btn": "شروع کریں", "loading": "تبدیل کیا جا رہا ہے...", "success": "🚀 تبدیلی مکمل ہوئی!", "download": "📥 فائل ڈاؤن لوڈ کریں"}
}

# --- 3. اختيار اللغة (في الأعلى) ---
selected_lang = st.selectbox("🌐", ["العربية", "English", "Français", "اردو"], index=0, key="lang_selector")
lang = translations[selected_lang]

# --- 4. التنسيق الجذري ---
st.markdown(f"""
<style>
    /* اتجاه ومحاذاة الصفحة */
    html, body, .stApp {{ direction: {lang['dir']} !important; text-align: {lang['align']} !important; background-color: #07090e !important; color: #ffffff !important; }}
    
    /* تصغير قائمة اللغة ووضعها في الأعلى */
    div[data-testid="stSelectbox"] {{ width: 250px !important; margin-bottom: 20px !important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {{ background-color: #000 !important; border: 2px solid #2ea043 !important; color: #2ea043 !important; }}
    
    /* توحيد الألوان للنصوص */
    h1, h2, h3, p, div, span, label {{ color: #ffffff !important; }}
    
    /* مستطيل الرفع نيون */
    [data-testid="stFileUploader"] {{ border: 2px solid #2ea043 !important; border-radius: 15px !important; background: #0d0d0d !important; }}
    
    /* الأزرار نيون */
    .stButton > button {{ border: 2px solid #2ea043 !important; color: #ffffff !important; background: transparent !important; border-radius: 50px !important; }}
    .stButton > button:hover {{ background: #2ea043 !important; box-shadow: 0 0 20px #2ea043 !important; }}
</style>
""", unsafe_allow_html=True)

# --- 5. الواجهة ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1"], lang["tab2"]])

# --- 6. منطق التحويل ---
with tab1:
    files = st.file_uploader(lang["up"], type=["pdf"], accept_multiple_files=True)
    if files:
        for f in files:
            if st.button(f"{lang['btn']} {f.name}"):
                with st.spinner(lang["loading"]):
                    # حفظ الملف مؤقتاً لقراءته بواسطة Tabula
                    with open(f.name, "wb") as temp_file:
                        temp_file.write(f.getvalue())
                    
                    try:
                        dfs = tabula.read_pdf(f.name, pages='all', multiple_tables=True, stream=True)
                        if dfs:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                for i, df in enumerate(dfs):
                                    df.to_excel(writer, index=False, sheet_name=f'Sheet{i+1}')
                            st.success(lang["success"])
                            st.download_button(lang["download"], output.getvalue(), f"{f.name}.xlsx", "application/vnd.ms-excel")
                        else:
                            st.error("لم يتم العثور على جداول!")
                    except Exception as e:
                        st.error(f"خطأ: {e}")

with tab2:
    img = st.file_uploader(lang["up"], type=["jpg", "png", "pdf"])
    if img and st.button(lang["btn"]):
        st.info("Scanning...")
