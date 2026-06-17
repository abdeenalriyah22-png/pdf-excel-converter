import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# --- 2. إعدادات الترجمة ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً",
        "tab1_title": "📊 تحويل PDF إلى جداول Excel", "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات", "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي", "card2_desc": "استخراج النصوص العربية والإنجليزية والأوردو بدقة كاملة من المستندات المصورة والـ PDF",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF الخاصة بالجداول هنا",
        "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدأ تحويل وجدولة: ", "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي لقراءة النص",
        "status_preparing": "📁 ملف قيد التحضير: ", "status_loading": "جاري تفكيك الجداول وهيكلتها...",
        "status_ocr_loading": "جاري المسح الضوئي للمستند وتفسير الحروف...",
        "success_convert": "🚀 اكتمل التحويل بنجاح وبأعلى دقة!",
        "warning_no_tables": "⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.",
        "warning_no_text": "نعتذر، لم نكتشف حروفاً أو نصوصاً مقروءة في هذا المستند.",
        "download_excel": "📥 اضغط هنا لتحميل ملف Excel المستخرج", "download_txt": "📥 تحميل النص كملف TXT",
        "ocr_result_header": "#### ✅ النصوص التي تم العثور عليها ومسحها:",
        "opt1": "📋 الخيار الأول:", "opt2": "📥 الخيار الثاني:",
        "btn_copy": "📋 نسخ النص بالكامل", "copied": "✅ تم النسخ بنجاح!",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr", "align": "left",
        "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Advanced cloud system for smart data and table processing",
        "tab1_title": "📊 Convert PDF to Excel", "tab2_title": "🔍 Smart Text Extraction (OCR)",
        "card1_title": "Data Table Extractor", "card1_desc": "Upload your files to automatically convert any silent table inside PDF into a formatted Excel file",
        "card2_title": "Text Reader & Scanner", "card2_desc": "Extract Arabic, English, and Urdu text with full accuracy from scanned documents and images",
        "uploader_pdf": "Drag and drop your PDF table files here",
        "uploader_ocr": "Upload invoice/document image (JPG, PNG) or scanned PDF file",
        "btn_convert": "Start Converting & Scheduling: ", "btn_ocr": "🚀 Launch AI to Read Text",
        "status_preparing": "📁 File preparing: ", "status_loading": "Deconstructing and structuring tables...",
        "status_ocr_loading": "Scanning document and interpreting characters...",
        "success_convert": "🚀 Conversion completed successfully with highest accuracy!",
        "warning_no_tables": "⚠️ No clear numerical tables detected in this file.",
        "warning_no_text": "Sorry, no readable characters or text detected in this document.",
        "download_excel": "📥 Click here to download the extracted Excel file", "download_txt": "📥 Download text as TXT file",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "opt1": "📋 Option 1:", "opt2": "📥 Option 2:",
        "btn_copy": "📋 Copy Full Text", "copied": "✅ Copied Successfully!",
        "motto": "Separation of liability... connection in trust"
    },
    "Français": {
        "direction": "ltr", "align": "left",
        "title": "📊 Comptable Intelligent <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Système cloud avancé pour le traitement intelligent des données",
        "tab1_title": "📊 Convertir PDF en Excel", "tab2_title": "🔍 Extraction intelligente de texte (OCR)",
        "card1_title": "Extracteur de tableaux", "card1_desc": "Téléchargez vos fichiers pour convertir automatiquement tout tableau PDF en fichier Excel formaté",
        "card2_title": "Lecteur et scanner de texte", "card2_desc": "Extrayez du texte avec une précision totale à partir de documents numérisés et d'images",
        "uploader_pdf": "Glissez et déposez vos fichiers PDF ici",
        "uploader_ocr": "Téléchargez une image de facture/document (JPG, PNG) ou un PDF numérisé",
        "btn_convert": "Commencer la conversion: ", "btn_ocr": "🚀 Lancer l'IA pour lire le texte",
        "status_preparing": "📁 Préparation du fichier: ", "status_loading": "Structure des tableaux en cours...",
        "status_ocr_loading": "Numérisation et interprétation des caractères...",
        "success_convert": "🚀 Conversion terminée avec succès!",
        "warning_no_tables": "⚠️ Aucun tableau numérique détecté dans ce fichier.",
        "warning_no_text": "Désolé, aucun texte lisible détecté dans ce document.",
        "download_excel": "📥 Cliquez ici pour télécharger le fichier Excel", "download_txt": "📥 Télécharger le texte en format TXT",
        "ocr_result_header": "#### ✅ Texte extrait :",
        "opt1": "📋 Option 1:", "opt2": "📥 Option 2:",
        "btn_copy": "📋 Copier le texte", "copied": "✅ Copié avec succès!",
        "motto": "Séparation de la responsabilité... Connexion dans la confiance"
    },
    "اردو": {
        "direction": "rtl", "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "tab1_title": "📊 پی ڈی ایف کو ایکسل میں تبدیل کریں", "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر", "card1_desc": "پی ڈی ایف کے اندر موجود کسی بھی پوشیدہ ٹیبل کو خودکار طور پر فارمیٹ شدہ ایکسل فائل میں تبدیل کرنے کے لیے اپنی فائلیں اپ لوڈ کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسكينر", "card2_desc": "اسکین شدہ दस्तावेजات اور تصاویر سے مکمل درستگی کے ساتھ عربی، انگریزی اور اردو متن نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر (JPG, PNG) أو اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی اور شیڈولنگ شروع کریں: ", "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "📁 فائل کی تیاری: ", "status_loading": "ٹیبلز کو ڈی کنسٹریکٹ اور سٹرکچر کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین اور حروف کی تشریح کی جا رہی ہے...",
        "success_convert": "🚀 اعلیٰ ترین درستگی کے ساتھ تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح عددی ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل حروف یا متن نہیں ملا۔",
        "download_excel": "📥 نکالی گئی ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں", "download_txt": "📥 متن کو TXT فائل کے طور بر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "opt1": "📋 پہلا آپشن:", "opt2": "📥 دوسرا آپشن:",
        "btn_copy": "📋 پورا متن کاپی کریں", "copied": "✅ کامیابی سے کاپی ہو گیا!",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

# --- 3. اختيار اللغة ---
selected_lang = st.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English", "Français", "اردو"], index=0)
lang = translations[selected_lang]

# --- 4. تطبيق التصميم ---
st.markdown(f"""
<style>
    html, body, [class*="st-emotion-cache"] {{ font-family: 'Cairo', sans-serif !important; direction: {lang['direction']} !important; text-align: {lang['align']} !important; }}
    .stApp {{ background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; color: #e6edf3; }}
</style>
""", unsafe_allow_html=True)

# --- 5. الواجهة الرئيسية ---
st.markdown(f"<h1>{lang['title']}</h1><p>{lang['subtitle']}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

with tab1:
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        for uploaded_pdf in pdf_files:
            if st.button(f"{lang['btn_convert']}{uploaded_pdf.name}"):
                with st.spinner(lang["status_loading"]):
                    dfs = tabula.read_pdf(uploaded_pdf, pages='all', lattice=True)
                    if dfs:
                        st.success(lang["success_convert"])
                        # كود التحميل (تم اختصاره هنا، استخدم كودك الأصلي للتحميل)
                    else: st.warning(lang["warning_no_tables"])

with tab2:
    ocr_file = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "pdf"])
    if ocr_file and st.button(lang["btn_ocr"]):
        # كود الـ OCR (استخدم كودك الأصلي هنا للـ OCR)
        st.write(lang["ocr_result_header"])
