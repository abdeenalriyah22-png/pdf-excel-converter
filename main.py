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

# --- 2. التحكم في اختيار الثيم واللغة من الأعلى ---
col_top1, col_top2, col_top3 = st.columns([3, 3, 2])

with col_top1:
    selected_lang = st.selectbox(
        "🌐 Choose Language / اختر اللغة",
        ["العربية", "English", "اردو"],
        index=0,
        key="language_selector"
    )

with col_top2:
    selected_theme_name = st.selectbox(
        "🎨 Select Theme / اختر الثيم الفني",
        ["🌌 نيون سايبربانك (Cyberpunk Neon)", "👑 رويال جولد (Royal Gold)", "🌲 الطبيعة المريحة (Emerald Forest)", "🌙 الكلاسيكي الداكن (Dark Mode)"],
        index=0,
        key="theme_selector"
    )

with col_top3:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    theme_mapping = {
        "🌌 نيون سايبربانك (Cyberpunk Neon)": "cyberpunk",
        "👑 رويال جولد (Royal Gold)": "gold",
        "🌲 الطبيعة المريحة (Emerald Forest)": "forest",
        "🌙 الكلاسيكي الداكن (Dark Mode)": "dark"
    }
    current_theme = theme_mapping.get(selected_theme_name, "cyberpunk")

# --- 3. دمج الخلفية المتحركة المخصصة لكل ثيم عبر iframe ---
def render_permanent_background(theme):
    if theme == "cyberpunk":
        bg_code = """
        body, html { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #05050a; }
        .bg-fx { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; pointer-events: none; }
        .grid-line { position: absolute; width: 200%; height: 200%; background-image: linear-gradient(rgba(236, 72, 153, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(6, 182, 212, 0.05) 1px, transparent 1px); background-size: 40px 40px; animation: moveGrid 20s linear infinite; }
        @keyframes moveGrid { 0% { transform: translateY(0); } 100% { transform: translateY(40px); } }
        """
    elif theme == "gold":
        bg_code = """
        body, html { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #0c0a09; }
        .bg-fx { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; pointer-events: none; background: radial-gradient(circle at 50% 20%, rgba(217, 119, 6, 0.12) 0%, transparent 60%); }
        """
    elif theme == "forest":
        bg_code = """
        body, html { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #022c22; }
        .bg-fx { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; pointer-events: none; background: radial-gradient(circle at 20% 80%, rgba(16, 185, 129, 0.15) 0%, transparent 50%); }
        """
    else:
        bg_code = """
        body, html { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #03070c; }
        .bg-fx { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; pointer-events: none; }
        """

    bg_html = f"""<!DOCTYPE html><html><head><style>{bg_code}</style></head><body><div class="bg-fx"><div class="grid-line"></div></div></body></html>"""
    components.html(f"""
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -999; pointer-events: none;">
        <iframe srcdoc="{bg_html.replace('"', '&quot;')}" style="width: 100%; height: 100%; border: none; pointer-events: none;"></iframe>
    </div>
    """, height=0, width=0)

render_permanent_background(current_theme)

# --- 4. قاموس الترجمة للغات الثلاث ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً",
        "tab1_title": "📊 تحويل PDF و CSV إلى Excel",
        "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات",
        "card1_desc": "ارفع ملفاتك لتحويل أي جدول داخل الـ PDF أو ملفات CSV إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي",
        "card2_desc": "استخراج النصوص العربية والإنجليزية والأوردو بدقة كاملة من المستندات المصورة والـ PDF",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF أو CSV الخاصة بالجداول هنا",
        "uploader_ocr": "ارفع صورة الفاتورة أو المستند (JPG, PNG) أو ملف PDF",
        "btn_convert": "بدء تحويل وجدولة الملف",
        "btn_ocr": "🚀 تشغيل الذكاء الاصطناعي لقراءة النص",
        "status_preparing": "📁 ملف قيد التحضير: ",
        "status_loading": "جاري تفكيك الجداول وهيكلتها...",
        "status_ocr_loading": "جاري المسح الضوئي للمستند وتفسير الحروف...",
        "success_convert": "🚀 اكتمل التحويل بنجاح وبأعلى دقة!",
        "warning_no_tables": "⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.",
        "warning_no_text": "نعتذر، لم نكتشف حروفاً أو نصوصاً مقروءة في هذا المستند.",
        "download_excel": "📥 تحميل ملف Excel المستخرج",
        "download_txt": "📥 تحميل النص كملف TXT",
        "ocr_result_header": "#### ✅ النصوص التي تم العثور عليها:",
        "opt1": "📋 النسخ السريع:",
        "opt2": "📥 التنزيل المباشر:",
        "btn_copy": "📋 نسخ النص بالكامل",
        "copied": "✅ تم النسخ بنجاح!",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr",
        "align": "left",
        "title": "📊 Smart Accountant <span style='font-size:22px; font-weight:normal;'>Pro</span>",
        "subtitle": "Advanced cloud system for smart data and table processing",
        "tab1_title": "📊 Convert PDF & CSV to Excel",
        "tab2_title": "🔍 Smart Text Extraction (OCR)",
        "card1_title": "Data Table Extractor",
        "card1_desc": "Upload your files to automatically convert any table inside PDF or CSV files into a formatted Excel file",
        "card2_title": "Text Reader & Scanner",
        "card2_desc": "Extract Arabic, English, and Urdu text with full accuracy from scanned documents and images",
        "uploader_pdf": "Drag and drop your PDF or CSV table files here",
        "uploader_ocr": "Upload invoice/document image (JPG, PNG) or PDF file",
        "btn_convert": "Start Converting File",
        "btn_ocr": "🚀 Launch AI to Read Text",
        "status_preparing": "📁 File preparing: ",
        "status_loading": "Deconstructing and structuring tables...",
        "status_ocr_loading": "Scanning document and interpreting characters...",
        "success_convert": "🚀 Conversion completed successfully with highest accuracy!",
        "warning_no_tables": "⚠️ No clear numerical tables detected in this file.",
        "warning_no_text": "Sorry, no readable characters or text detected in this document.",
        "download_excel": "📥 Download Extracted Excel File",
        "download_txt": "📥 Download Text as TXT File",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "opt1": "📋 Quick Copy:",
        "opt2": "📥 Direct Download:",
        "btn_copy": "📋 Copy Full Text",
        "copied": "✅ Copied Successfully!",
        "motto": "Separation of liability... connection in trust"
    },
    "اردو": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; font-weight:normal;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "tab1_title": "📊 پی ڈی ایف اور سی ایس وی کو ایکسل میں تبدیل کریں",
        "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "card1_desc": "پی ڈی ایف یا سی ایس وی فائلوں کو خودکار طور پر فارمیٹ شدہ ایکسل فائل میں تبدیل کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسکینر",
        "card2_desc": "اسکین شدہ دستاویزات اور تصاویر سے درستگی کے ساتھ عربی، انگریزی اور اردو متن نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف یا سی ایس وی فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "دستاویز کی تصویر (JPG, PNG) یا پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "فائل کی تبدیلی شروع کریں",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "📁 فائل کی تیاری: ",
        "status_loading": "ٹیبلز کو سٹرکچر کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین کیا جا رہا ہے...",
        "success_convert": "🚀 تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح عددی ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی متن نہیں ملا۔",
        "download_excel": "📥 ایکسل فائل ڈاؤن لوڈ کریں",
        "download_txt": "📥 ٹیکسٹ فائل ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "opt1": "📋 فوری کاپی:",
        "opt2": "📥 براہ راست ڈاؤن لوڈ:",
        "btn_copy": "📋 پورا متن کاپی کریں",
        "copied": "✅ کامیابی سے کاپی ہو گیا!",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

lang = translations[selected_lang]

# --- 5. محرك الأنماط الديناميكي ---
def apply_theme_and_styles(direction, align, theme):
    if theme == "cyberpunk":
        font_family = "'Orbitron', 'Cairo', sans-serif"
        bg_gradient = "linear-gradient(135deg, rgba(10, 10, 20, 0.95) 0%, rgba(20, 5, 25, 0.95) 100%)"
        text_color = "#f43f5e"
        main_text = "#ffffff"
        card_bg = "linear-gradient(145deg, rgba(18, 18, 35, 0.9) 0%, rgba(10, 10, 20, 0.95) 100%)"
        border_color = "#f43f5e"
        accent_color = "#06b6d4"
        btn_gradient = "linear-gradient(135deg, #f43f5e 0%, #06b6d4 100%)"
        btn_hover = "linear-gradient(135deg, #06b6d4 0%, #f43f5e 100%)"
        select_bg = "#0f0f1a"
        dropdown_hover = "#1e1b4b"
        # ألوان التبويبات
        tab_bg = "rgba(255, 255, 255, 0.08)"
        tab_selected_bg = btn_gradient
        tab_text = "#ffffff" # الأبيض الناصع
    elif theme == "gold":
        font_family = "'Amiri', 'Cairo', serif"
        bg_gradient = "linear-gradient(135deg, rgba(15, 13, 11, 0.96) 0%, rgba(28, 22, 15, 0.96) 100%)"
        text_color = "#fbbf24"
        main_text = "#fffbeb"
        card_bg = "linear-gradient(145deg, rgba(30, 24, 16, 0.9) 0%, rgba(18, 14, 9, 0.95) 100%)"
        border_color = "#d97706"
        accent_color = "#fbbf24"
        btn_gradient = "linear-gradient(135deg, #d97706 0%, #b45309 100%)"
        btn_hover = "linear-gradient(135deg, #fbbf24 0%, #d97706 100%)"
        select_bg = "#1c140c"
        dropdown_hover = "#451a03"
        # ألوان التبويبات
        tab_bg = "rgba(255, 255, 255, 0.08)"
        tab_selected_bg = btn_gradient
        tab_text = "#fffbeb"
    elif theme == "forest":
        font_family = "'Tajawal', 'Cairo', sans-serif"
        bg_gradient = "linear-gradient(135deg, rgba(2, 44, 34, 0.95) 0%, rgba(1, 20, 15, 0.95) 100%)"
        text_color = "#34d399"
        main_text = "#f0fdf4"
        card_bg = "linear-gradient(145deg, rgba(4, 58, 44, 0.9) 0%, rgba(2, 35, 27, 0.95) 100%)"
        border_color = "#059669"
