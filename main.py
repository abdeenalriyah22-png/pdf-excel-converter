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

# --- 2. قاموس الترجمة المحدث ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً",
        "tab1_title": "📊 تحويل PDF إلى جداول Excel", "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات", "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي", "card2_desc": "استخراج النصوص العربية والإنجليزية والأوردو بدقة كاملة من المستندات المصورة والـ PDF",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF الخاصة بالجداول هنا", "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدأ تحويل وجدولة: ", "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي لقراءة النص",
        "status_loading": "جاري تفكيك الجداول وهيكلتها...", "success_convert": "🚀 اكتمل التحويل بنجاح!",
        "download_excel": "📥 تحميل ملف Excel", "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr", "align": "left",
        "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Advanced cloud system for smart data and table processing",
        "tab1_title": "📊 Convert PDF to Excel", "tab2_title": "🔍 Smart Text Extraction (OCR)",
        "card1_title": "Data Table Extractor", "card1_desc": "Convert any table inside PDF into a formatted Excel file",
        "card2_title": "Text Reader & Scanner", "card2_desc": "Extract text with full accuracy from scanned documents",
        "uploader_pdf": "Drag and drop your PDF files here", "uploader_ocr": "Upload document image or PDF",
        "btn_convert": "Start Converting: ", "btn_ocr": "🚀 Launch AI to Read Text",
        "status_loading": "Deconstructing tables...", "success_convert": "🚀 Conversion completed!",
        "download_excel": "📥 Download Excel file", "motto": "Separation of liability... connection in trust"
    },
    "Français": {
        "direction": "ltr", "align": "left",
        "title": "📊 Comptable Intelligent <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Système cloud avancé pour le traitement intelligent des données",
        "tab1_title": "📊 Convertir PDF en Excel", "tab2_title": "🔍 Extraction intelligente (OCR)",
        "card1_title": "Extracteur de tableaux", "card1_desc": "Convertissez automatiquement tout tableau PDF en fichier Excel",
        "card2_title": "Lecteur et scanner de texte", "card2_desc": "Extrayez du texte avec précision à partir de documents numérisés",
        "uploader_pdf": "Glissez et déposez vos fichiers PDF ici", "uploader_ocr": "Téléchargez une image ou un PDF numérisé",
        "btn_convert": "Commencer la conversion: ", "btn_ocr": "🚀 Lancer l'IA pour lire le texte",
        "status_loading": "Structure des tableaux en cours...", "success_convert": "🚀 Conversion réussie!",
        "download_excel": "📥 Télécharger le fichier Excel", "motto": "Séparation de la responsabilité... Connexion dans la confiance"
    }
}

# --- 3. اختيار اللغة وتنسيق النيون ---
selected_lang = st.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English", "Français"], index=0)
lang = translations[selected_lang]

st.markdown(f"""
<style>
    :root {{ --neon-blue: #58a6ff; --neon-green: #2ea043; }}
    html, body {{ direction: {lang['direction']} !important; text-align: {lang['align']} !important; font-family: 'Cairo', sans-serif !important; background: #07090e !important; }}
    
    /* القائمة المنسدلة بيضاء */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{ background-color: #ffffff !important; border: 2px solid var(--neon-blue) !important; color: black !important; }}
    
    /* توهج الأزرار */
    .stButton > button {{ background: transparent !important; color: white !important; border: 2px solid var(--neon-green) !important; box-shadow: 0 0 10px var(--neon-green), inset 0 0 10px var(--neon-green) !important; transition: 0.3s !important; }}
    .stButton > button:hover {{ background: var(--neon-green) !important; box-shadow: 0 0 25px var(--neon-green), 0 0 50px var(--neon-green) !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. الواجهة ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

with tab1:
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        for uploaded_pdf in pdf_files:
            if st.button(f"{lang['btn_convert']}{uploaded_pdf.name}"):
                with st.spinner(lang["status_loading"]):
                    # هنا كود التحويل الخاص بك
                    st.success(lang["success_convert"])

with tab2:
    ocr_file = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "pdf"])
    if ocr_file and st.button(lang["btn_ocr"]):
        # هنا كود الـ OCR الخاص بك
        st.write("✅ Ready")
