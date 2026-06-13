import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="المحاسب الذكي Pro / Smart Accountant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. دمج كود جوجل أدسنس ---
components.html("""
<meta name="google-adsense-account" content="ca-pub-1091631464795781">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781"
     crossorigin="anonymous"></script>
""", height=0, width=0)

# --- 3. قاموس الترجمة ---
translations = {
    "العربية": {
        "direction": "rtl", "align": "right",
        "title": "📊 المحاسب الذكي <span style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe;'>Pro</span>",
        "subtitle": "المنصة السحابية المتكاملة لإدارة ومعالجة ملفات وجداول PDF ذكياً",
        "menu_title": "🛠️ تفعيل الأدوات الذكية:",
        "tool_excel": "📊 تحويل PDF إلى جداول Excel",
        "tool_ocr": "🔍 استخراج النصوص الذكي (OCR)",
        "tool_merge": "📂 دمج ملفات PDF متعددة",
        "tool_delete": "✂️ حذف صفحات من ملف PDF",
        "tool_reorder": "🔀 إعادة ترتيب صفحات PDF",
        "tool_sign": "✍️ التوقيع الإلكتروني على المستند",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF الخاصة بالجداول هنا",
        "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدأ تحويل وجدولة: ",
        "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي لقراءة النص",
        "status_loading": "جاري تفكيك البيانات وهيكلتها برمجياً...",
        "success_convert": "🚀 اكتملت العملية بنجاح وبأعلى دقة!",
        "warning_no_tables": "⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.",
        "warning_no_text": "نعتذر، لم نكتشف حروفاً أو نصوصاً مقروءة في هذا المستند.",
        "download_excel": "📥 اضغط هنا لتحميل ملف Excel المستخرج",
        "download_txt": "📥 تحميل النص كملف TXT",
        "ocr_result_header": "#### ✅ النصوص التي تم العثور عليها ومسحها:",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr", "align": "left",
        "title": "📊 Smart Accountant <span style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe;'>Pro</span>",
        "subtitle": "Integrated cloud platform for smart PDF management",
        "menu_title": "🛠️ Activate Smart Tools:",
        "tool_excel": "📊 Convert PDF to Excel",
        "tool_ocr": "🔍 Smart Text Extraction (OCR)",
        "tool_merge": "📂 Merge PDF Files",
        "tool_delete": "✂️ Delete Pages",
        "tool_reorder": "🔀 Reorder PDF Pages",
        "tool_sign": "✍️ Digital Signature",
        "uploader_pdf": "Drag and drop your PDF files here",
        "uploader_ocr": "Upload invoice/document image or PDF",
        "btn_convert": "Start Converting: ",
        "btn_ocr": "🚀 Launch AI to Read Text",
        "status_loading": "Processing data...",
        "success_convert": "🚀 Success!",
        "warning_no_tables": "⚠️ No tables detected.",
        "warning_no_text": "No readable text detected.",
        "download_excel": "📥 Download Excel file",
        "download_txt": "📥 Download TXT",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "motto": "Separation of liability... connection in trust"
    },
    "اردو": {
        "direction": "rtl", "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe;'>Pro</span>",
        "subtitle": "جدید کلاؤڈ سسٹم برائے پی ڈی ایف مینجمنٹ",
        "menu_title": "🛠️ ٹول منتخب کریں:",
        "tool_excel": "📊 پی ڈی ایف کو ایکسل میں بدلیں",
        "tool_ocr": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "tool_merge": "📂 متعدد پی ڈی ایف ضم کریں",
        "tool_delete": "✂️ صفحات حذف کریں",
        "tool_reorder": "🔀 صفحات دوبارہ ترتیب دیں",
        "tool_sign": "✍️ دستاویز پر دستخط",
        "uploader_pdf": "پی ڈی ایف فائلیں یہاں ڈریگ کریں",
        "uploader_ocr": "انوائس یا دستاویز اپ لوڈ کریں",
        "btn_convert": "تبدیلی شروع کریں: ",
        "btn_ocr": "🚀 AI لانچ کریں",
        "status_loading": "ڈیٹا پر کارروائی جاری ہے...",
        "success_convert": "🚀 کامیابی سے مکمل ہو گیا!",
        "warning_no_tables": "⚠️ کوئی ٹیبل نہیں ملا۔",
        "warning_no_text": "کوئی ٹیکسٹ نہیں ملا۔",
        "download_excel": "📥 ایکسل ڈاؤن لوڈ کریں",
        "download_txt": "📥 ٹیکسٹ ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

# --- 4. لوحة التحكم الجانبية ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00f2fe;'>⚙️ CONTROL PANEL</h2>", unsafe_allow_html=True)
    
    selected_lang = st.selectbox("🌐 Language / اللغة", ["العربية", "English", "اردو"], index=0)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    theme_choice = st.radio("🌓 Theme Mode", ["Dark Mode 🌑", "Light Mode ☀️"])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    lang = translations[selected_lang]
    tool_options = [lang["tool_excel"], lang["tool_ocr"], lang["tool_merge"], lang["tool_delete"], lang["tool_reorder"], lang["tool_sign"]]
    current_tool = st.radio(lang["menu_title"], tool_options)

# --- 5. نظام الـ CSS (استخدام {{ }} لتجنب أخطاء f-string) ---
st.markdown(f"""
<style>
.stApp {{ background: radial-gradient(circle, #0b0f19, #04060a) !important; color: #f8fafc !important; }}
[data-testid="stSidebar"] {{ background-color: rgba(10, 15, 26, 0.95) !important; }}
h1 {{ background: linear-gradient(to right, #ffffff, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.custom-card {{ background: #0f172a; border-radius: 20px; padding: 30px; text-align: center; border: 1px solid rgba(0, 242, 254, 0.2); }}
.stButton>button {{ background: linear-gradient(90deg, #00f2fe, #4facfe); color: #000; font-weight: 900; border-radius: 14px; width: 100%; }}
</style>
""", unsafe_allow_html=True)

# --- 6. عرض الواجهة ---
st.markdown(f"<div style='text-align: {lang['align']};'><h1>{lang['title']}</h1><p>{lang['subtitle']}</p></div>", unsafe_allow_html=True)

# --- 7. منطق الأدوات (اختصار للأداة الأولى كمثال) ---
if current_tool == lang["tool_excel"]:
    st.markdown(f"<div class='custom-card'><h3>{lang['tool_excel']}</h3></div>", unsafe_allow_html=True)
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], accept_multiple_files=True)
    # ... باقي منطق التحويل ...

# التذييل
st.markdown(f"<div style='text-align:center; padding:20px; color:#94a3b8;'>{lang['motto']} | 2026 ©</div>", unsafe_allow_html=True)
