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

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="المحاسب الذكي Pro / Smart Accountant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. دمج كود جوجل أدسنس والتحقق في الخلفية ---
components.html("""
<meta name="google-adsense-account" content="ca-pub-1091631464795781">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781"
     crossorigin="anonymous"></script>
""", height=0, width=0)

# --- 3. اختيار اللغة في أعلى الموقع ---
selected_lang = st.selectbox(
    "🌐 Choose Language / اختر اللغة / زبان کا انتخاب کریں / Choisir la langue",
    ["العربية", "English", "Français", "اردو"],
    index=0,
    key="language_selector"
)

# --- 4. قاموس الترجمة ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right", "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً", "tab1_title": "📊 تحويل PDF إلى جداول Excel",
        "tab2_title": "🔍 استخراج النصوص الذكي (OCR)", "card1_title": "مستخرج جداول البيانات",
        "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي", "card2_desc": "استخراج النصوص العربية والإنجليزية والفرنسية والأوردو بدقة كاملة",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF الخاصة بالجداول هنا", "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدأ تحويل وجدولة: ", "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي لقراءة النص",
        "status_preparing": "📁 ملف قيد التحضير: ", "status_loading": "جاري تفكيك الجداول وهيكلتها...",
        "status_ocr_loading": "جاري المسح الضوئي للمستند وتفسير الحروف...", "success_convert": "🚀 اكتمل التحويل بنجاح وبأعلى دقة!",
        "warning_no_tables": "⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.", "warning_no_text": "نعتذر، لم نكتشف حروفاً أو نصوصاً مقروءة في هذا المستند.",
        "download_excel": "📥 اضغط هنا لتحميل ملف Excel المستخرج", "download_txt": "📥 تحميل النص كملف TXT",
        "ocr_result_header": "#### ✅ النصوص التي تم العثور عليها ومسحها:", "opt1": "📋 الخيار الأول:", "opt2": "📥 الخيار الثاني:",
        "btn_copy": "📋 نسخ النص بالكامل", "copied": "✅ تم النسخ بنجاح!", "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr", "align": "left", "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Advanced cloud system for smart data and table processing", "tab1_title": "📊 Convert PDF to Excel",
        "tab2_title": "🔍 Smart Text Extraction (OCR)", "card1_title": "Data Table Extractor",
        "card1_desc": "Upload your files to automatically convert any silent table inside PDF into a formatted Excel file",
        "card2_title": "Text Reader & Scanner", "card2_desc": "Extract Arabic, English, French, and Urdu text with full accuracy",
        "uploader_pdf": "Drag and drop your PDF table files here", "uploader_ocr": "Upload invoice/document image (JPG, PNG) or scanned PDF file",
        "btn_convert": "Start Converting & Scheduling: ", "btn_ocr": "🚀 Launch AI to Read Text",
        "status_preparing": "📁 File preparing: ", "status_loading": "Deconstructing and structuring tables...",
        "status_ocr_loading": "Scanning document and interpreting characters...", "success_convert": "🚀 Conversion completed successfully!",
        "warning_no_tables": "⚠️ No clear numerical tables detected.", "warning_no_text": "Sorry, no readable text detected.",
        "download_excel": "📥 Click here to download the extracted Excel file", "download_txt": "📥 Download text as TXT file",
        "ocr_result_header": "#### ✅ Extracted Text:", "opt1": "📋 Option 1:", "opt2": "📥 Option 2:",
        "btn_copy": "📋 Copy Full Text", "copied": "✅ Copied Successfully!", "motto": "Separation of liability... connection in trust"
    },
    "Français": {
        "direction": "ltr", "align": "left", "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Système cloud avancé pour le traitement intelligent des données", "tab1_title": "📊 Convertir PDF en Excel",
        "tab2_title": "🔍 Extraction de texte intelligente (OCR)", "card1_title": "Extracteur de données",
        "card1_desc": "Téléchargez vos fichiers pour convertir automatiquement tout tableau PDF en fichier Excel",
        "card2_title": "Lecteur et scanner de texte", "card2_desc": "Extrayez du texte arabe, anglais, français et ourdou avec une précision totale",
        "uploader_pdf": "Glissez et déposez vos fichiers PDF ici", "uploader_ocr": "Téléchargez l'image de la facture ou le fichier PDF scanné",
        "btn_convert": "Démarrer la conversion: ", "btn_ocr": "🚀 Lancer l'IA pour lire le texte",
        "status_preparing": "📁 Préparation du fichier: ", "status_loading": "Déconstruction des tableaux en cours...",
        "status_ocr_loading": "Numérisation et interprétation des caractères...", "success_convert": "🚀 Conversion terminée avec succès !",
        "warning_no_tables": "⚠️ Aucun tableau numérique clair détecté.", "warning_no_text": "Désolé, aucun texte lisible détecté.",
        "download_excel": "📥 Cliquez ici pour télécharger le fichier Excel", "download_txt": "📥 Télécharger le texte au format TXT",
        "ocr_result_header": "#### ✅ Texte extrait :", "opt1": "📋 Option 1 :", "opt2": "📥 Option 2 :",
        "btn_copy": "📋 Copier le texte", "copied": "✅ Copié avec succès !", "motto": "Séparation de la responsabilité... lien de confiance"
    },
    "اردو": {
        "direction": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم", "tab1_title": "📊 پی ڈی ایف کو ایکسل میں تبدیل کریں",
        "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)", "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "card1_desc": "پی ڈی ایف کے اندر موجود ٹیبل کو خودکار طور پر ایکسل فائل میں تبدیل کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسکینر", "card2_desc": "عربی، انگریزی، فرانسیسی اور اردو متن درستگی کے ساتھ نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں", "uploader_ocr": "انوائس یا اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی شروع کریں: ", "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "📁 فائل کی تیاری: ", "status_loading": "ٹیبلز کو سٹرکچر کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین کیا جا رہا ہے...", "success_convert": "🚀 تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح عددی ٹیبل نہیں ملا۔", "warning_no_text": "معذرت، کوئی متن نہیں ملا۔",
        "download_excel": "📥 ایکسل فائل ڈاؤن لوڈ کرنے کے لیے کلک کریں", "download_txt": "📥 متن TXT فائل کے طور پر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:", "opt1": "📋 پہلا آپشن:", "opt2": "📥 دوسرا آپشن:",
        "btn_copy": "📋 پورا متن کاپی کریں", "copied": "✅ کامیابی سے کاپی ہو گیا!", "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

lang = translations[selected_lang]

# --- 5. استرجاع التنسيق الأصلي المستقر ---
def apply_neon_style(direction, align):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    html, body, [class*="st-emotion-cache"], p, div, h1, h2, h3, span, label, textarea {{
        font-family: 'Cairo', sans-serif !important;
        direction: {direction} !important;
        text-align: {align} !important;
    }}
    .stApp {{ background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; color: #e6edf3; }}
    h1 {{ color: #ffffff !important; font-weight: 900 !important; background: linear-gradient(to right, #ffffff, #58a6ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .custom-card {{ background: linear-gradient(145deg, #161b22 0%, #0f1319 100%); border: 1px solid #30363d; border-radius: 16px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important; color: white !important; border-radius: 12px !important; width: 100%; }}
    .footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: rgba(22, 27, 34, 0.9); text-align: center; padding: 12px; border-top: 1px solid #30363d; color: #8b949e; z-index: 999; }}
    </style>
    """, unsafe_allow_html=True)

apply_neon_style(lang["direction"], lang["align"])

# عرض المحتوى بنفس الهيكلية السابقة...
st.markdown(f"<div style='text-align: {lang['align']};'><h1>{lang['title']}</h1><p>{lang['subtitle']}</p></div>", unsafe_allow_html=True)
tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

with tab1:
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        for f in pdf_files:
            if st.button(f"{lang['btn_convert']}{f.name}"):
                dfs = tabula.read_pdf(f, pages='all', lattice=True)
                if dfs:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        dfs[0].to_excel(writer, index=False)
                    st.success(lang["success_convert"])
                    st.download_button(lang["download_excel"], output.getvalue(), f"Excel_{f.name}.xlsx")

with tab2:
    ocr_file = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "pdf"])
    if ocr_file and st.button(lang["btn_ocr"]):
        text = pytesseract.image_to_string(Image.open(ocr_file), lang='ara+eng+fra')
        st.text_area("Result", value=text)
        st_copy_to_clipboard(text)

st.markdown(f"<div class='footer'>المحاسب الذكي Pro | {lang['motto']} | 2026 ©</div>", unsafe_allow_html=True)
