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

# --- 3. قاموس الترجمة للغات الثلاث ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:26px; font-weight:bold;'>Pro</span>",
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
        "success_convert": "🚀 اكتمل التحويل بنجاح تام وتم تجهيز ملف Excel!",
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
        "title": "📊 Smart Accountant <span style='font-size:26px; font-weight:bold;'>Pro</span>",
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
        "success_convert": "🚀 Conversion completed successfully!",
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
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:26px; font-weight:bold;'>Pro</span>",
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

# --- 4. محرك الأنماط الديناميكي ---
def get_theme_colors(theme):
    if theme == "cyberpunk":
        return {
            "font_family": "'Orbitron', 'Cairo', sans-serif",
            "bg_gradient": "linear-gradient(135deg, rgba(10, 10, 20, 0.98) 0%, rgba(20, 5, 25, 0.98) 100%)",
            "text_color": "#ff2a6d",
            "main_text": "#ffffff",
            "card_bg": "linear-gradient(145deg, rgba(22, 22, 45, 0.95) 0%, rgba(12, 12, 25, 0.98) 100%)",
            "border_color": "#05d9e8",
            "accent_color": "#05d9e8",
            "btn_gradient": "linear-gradient(135deg, #ff2a6d 0%, #05d9e8 100%)",
            "btn_hover": "linear-gradient(135deg, #05d9e8 0%, #ff2a6d 100%)",
            "select_bg": "#0f0f1a",
            "dropdown_hover": "#1e1b4b",
            "tab_text_color": "#ffffff"
        }
    elif theme == "gold":
        return {
            "font_family": "'Amiri', 'Cairo', serif",
            "bg_gradient": "linear-gradient(135deg, rgba(15, 13, 11, 0.98) 0%, rgba(28, 22, 15, 0.98) 100%)",
            "text_color": "#fcd34d",
            "main_text": "#fffbeb",
            "card_bg": "linear-gradient(145deg, rgba(40, 32, 20, 0.95) 0%, rgba(20, 15, 10, 0.98) 100%)",
            "border_color": "#f59e0b",
            "accent_color": "#fcd34d",
            "btn_gradient": "linear-gradient(135deg, #d97706 0%, #b45309 100%)",
            "btn_hover": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
            "select_bg": "#1c140c",
            "dropdown_hover": "#451a03",
            "tab_text_color": "#fffbeb"
        }
    elif theme == "forest":
        return {
            "font_family": "'Tajawal', 'Cairo', sans-serif",
            "bg_gradient": "linear-gradient(135deg, rgba(2, 44, 34, 0.98) 0%, rgba(1, 20, 15, 0.98) 100%)",
            "text_color": "#6ee7b7",
            "main_text": "#f0fdf4",
            "card_bg": "linear-gradient(145deg, rgba(6, 78, 59, 0.95) 0%, rgba(2, 44, 34, 0.98) 100%)",
            "border_color": "#10b981",
            "accent_color": "#6ee7b7",
            "btn_gradient": "linear-gradient(135deg, #059669 0%, #047857 100%)",
            "btn_hover": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            "select_bg": "#022c22",
            "dropdown_hover": "#064e3b",
            "tab_text_color": "#f0fdf4"
        }
    else:
        return {
            "font_family": "'Cairo', sans-serif",
            "bg_gradient": "linear-gradient(180deg, rgba(10,25,47,0.95) 0%, rgba(6,16,30,0.98) 100%)",
            "text_color": "#38bdf8",
            "main_text": "#ffffff",
            "card_bg": "linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%)",
            "border_color": "#38bdf8",
            "accent_color": "#38bdf8",
            "btn_gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
            "btn_hover": "linear-gradient(135deg, #0369a1 0%, #0284c7 100%)",
            "select_bg": "#0b1329",
            "dropdown_hover": "#1e293b",
            "tab_text_color": "#ffffff"
        }

colors = get_theme_colors(current_theme)

def apply_theme_and_styles(direction, align, c):
    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700;900&family=Orbitron:wght@500;700;900&family=Tajawal:wght@450;700;900&display=swap" rel="stylesheet">
    
    <style>
    html, body, [class*="st-emotion-cache"], p, div, h1, h2, h3, span, label, textarea {{
        font-family: {c['font_family']} !important;
        direction: {direction} !important;
        text-align: {align} !important;
    }}

    .stApp {{
        background: {c['bg_gradient']} !important;
        color: {c['main_text']} !important;
    }}

    header, [data-testid="stHeader"] {{
        visibility: hidden;
        display: none;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 0rem !important;
        padding-bottom: 8rem !important;
        padding-left: 5rem !important;
        padding-right: 5rem !important;
    }}

    h1 {{
        font-size: 38px !important;
        color: {c['text_color']} !important;
        font-weight: 900 !important;
        text-shadow: 0 3px 15px rgba(0,0,0,0.6);
        letter-spacing: 0.5px;
    }}

    h3 {{
        font-size: 22px !important;
        color: {c['text_color']} !important;
        font-weight: 800 !important;
    }}

    p, span, label, div {{
        font-size: 17px !important;
        color: {c['main_text']} !important;
        letter-spacing: 0.3px;
    }}

    [data-testid="stSelectbox"] {{
        background-color: {c['select_bg']} !important;
        padding: 12px 18px !important;
        border-radius: 16px !important;
        border: 2px solid {c['border_color']} !important;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.6) !important;
    }}

    [data-testid="stSelectbox"] label p, [data-testid="stSelectbox"] label span {{
        font-size: 17px !important;
        font-weight: 800 !important;
        color: {c['text_color']} !important;
        margin-bottom: 8px !important;
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"],
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background-color: {c['select_bg']} !important;
        border: none !important;
        border-radius: 12px !important;
    }}

    [data-testid="stSelectbox"] span,
    [data-testid="stSelectbox"] div,
    [data-testid="stSelectbox"] input {{
        color: {c['main_text']} !important;
        -webkit-text-fill-color: {c['main_text']} !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        background-color: transparent !important;
    }}

    div[data-baseweb="popover"], 
    div[data-baseweb="menu"], 
    ul[role="listbox"],
    div[id^="baseui-menu-"] {{
        background-color: {c['select_bg']} !important;
        background: {c['select_bg']} !important;
        border: 2px solid {c['border_color']} !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.9) !important;
        opacity: 1 !important;
    }}

    li[role="option"], 
    div[role="option"],
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] li span {{
        background-color: {c['select_bg']} !important;
        color: {c['main_text']} !important;
        -webkit-text-fill-color: {c['main_text']} !important;
        font-size: 17px !important;
        font-weight: 800 !important;
        padding: 14px 20px !important;
        opacity: 1 !important;
    }}

    li[role="option"]:hover, 
    div[role="option"]:hover,
    [data-baseweb="menu"] li:hover {{
        background-color: {c['dropdown_hover']} !important;
        color: {c['text_color']} !important;
        -webkit-text-fill-color: {c['text_color']} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px;
        background-color: rgba(0, 0, 0, 0.6);
        padding: 12px;
        border-radius: 16px;
        border: 2px solid {c['border_color']};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 55px;
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        color: {c['tab_text_color']} !important;
        -webkit-text-fill-color: {c['tab_text_color']} !important;
        border: 1px solid {c['border_color']};
        padding: 0 30px;
        font-weight: 900 !important;
        font-size: 19px !important;
        transition: all 0.4s ease;
        opacity: 1 !important;
    }}

    .stTabs [data-baseweb="tab"] *,
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] div {{
        color: {c['tab_text_color']} !important;
        -webkit-text-fill-color: {c['tab_text_color']} !important;
        font-size: 19px !important;
        font-weight: 900 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: {c['btn_gradient']} !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        box-shadow: 0 0 30px {c['border_color']};
        transform: scale(1.02);
        border-color: #ffffff !important;
    }}

    .stTabs [aria-selected="true"] *,
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 19px !important;
        font-weight: 900 !important;
    }}

    [data-testid="stFileUploader"] {{
        background-color: {c['card_bg']} !important;
        border: 3px dashed {c['border_color']} !important;
        border-radius: 20px !important;
        padding: 35px !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.5);
    }}

    [data-testid="stFileUploader"] section {{
        background-color: transparent !important;
    }}

    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] small, 
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] div {{
        color: {c['main_text']} !important;
        font-size: 17px !important;
        font-weight: 700 !important;
    }}

    .custom-card {{
        background: {c['card_bg']};
        border: 2px solid {c['border_color']};
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.6);
        backdrop-filter: blur(10px);
    }}

    .custom-card h3 {{
        font-size: 26px !important;
        color: {c['text_color']} !important;
        font-weight: 900 !important;
        margin-bottom: 10px !important;
    }}

    .custom-card p {{
        font-size: 17px !important;
        color: {c['main_text']} !important;
        opacity: 0.95;
    }}

    .stButton>button, [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {{
        background: {c['btn_gradient']} !important;
        color: white !important;
        border: 2px solid {c['border_color']} !important;
        border-radius: 16px !important;
        padding: 0.85rem 2.2rem !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        width: 100%;
        box-shadow: 0 6px 20px rgba(0,0,0,0.5);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    .stButton>button:hover, [data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-primary"]:hover {{
        background: {c['btn_hover']} !important;
        border-color: {c['text_color']} !important;
        box-shadow: 0 10px 35px {c['border_color']}, 0 0 25px {c['accent_color']} !important;
        transform: translateY(-3px) scale(1.01) !important;
    }}

    textarea {{
        font-size: 17px !important;
        font-weight: 700 !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
        color: {c['main_text']} !important;
        border: 2px solid {c['border_color']} !important;
        border-radius: 14px !important;
    }}

    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(5, 5, 10, 0.95);
        backdrop-filter: blur(10px);
        color: {c['text_color']};
        text-align: center;
        padding: 15px;
        border-top: 2px solid {c['border_color']};
        font-size: 16px;
        font-weight: 800;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme_and_styles(lang["direction"], lang["align"], colors)

# --- 5. الخلفية المتحركة ---
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

# --- 6. واجهة البرنامج الرئيسية ---
st.markdown(f"""
<div style='text-align: {lang["align"]}; margin-bottom: 15px;'>
    <h1>{lang["title"]}</h1>
    <p style='font-size:18px; margin-top:-8px; opacity: 0.9;'>{lang["subtitle"]}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

# --- التبويب الأول ---
with tab1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container"><i class="fa-solid fa-file-excel" style="font-size: 55px; color: {colors['text_color']};"></i></div>
        <h3>{lang["card1_title"]}</h3>
        <p>{lang["card1_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(lang["uploader_pdf"], type=["pdf", "csv"], key="table_uploader_main", accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            st.write("")
            with st.container():
                st.info(f"{lang['status_preparing']}{file.name}")
                if st.button(f"{lang['btn_convert']} ({file.name})", key=f"btn_{file.name}"):
                    try:
                        with st.spinner(lang["status_loading"]):
                            dfs = []
                            if file.name.lower().endswith('.csv'):
                                df_csv = pd.read_csv(file)
                                dfs.append(df_csv)
                            else:
                                dfs = tabula.read_pdf(file, pages='all', multiple_tables=True, lattice=True)
                            
                            if dfs:
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    current_row = 0
                                    for df in dfs:
                                        df = df.fillna('')
                                        df.to_excel(writer, index=False, startrow=current_row, sheet_name='Data')
                                        current_row += len(df) + 2
                                
                                st.success(lang["success_convert"])
                                clean_name = file.name.rsplit('.', 1)[0]
                                st.download_button(
                                    label=lang["download_excel"],
                                    data=output.getvalue(),
                                    file_name=f"Excel_{clean_name}.xlsx",
                                    mime="application/vnd.ms-excel",
                                    key=f"dl_{file.name}"
                                )
                            else:
                                st.warning(lang["warning_no_tables"])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# --- التبويب الثاني ---
with tab2:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container"><i class="fa-solid fa-eye" style="font-size: 55px; color: {colors['text_color']};"></i></div>
        <h3>{lang["card2_title"]}</h3>
        <p>{lang["card2_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    ocr_file = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "jpeg", "pdf"], key="ocr_main")
    
    if ocr_file:
        if st.button(lang["btn_ocr"], key="ocr_run_btn"):
            full_text = ""
            try:
                with st.spinner(lang["status_ocr_loading"]):
                    if ocr_file.type == "application/pdf":
                        doc = fitz.open(stream=ocr_file.read(), filetype="pdf")
                        for page in doc:
                            text = page.get_text()
                            if text.strip():
                                full_text += text + "\n"
                            else:
                                pix = page.get_pixmap()
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                full_text += pytesseract.image_to_string(img, lang='ara+eng') + "\n"
                    else:
                        img = Image.open(ocr_file)
                        full_text = pytesseract.image_to_string(img, lang='ara+eng+urd')

                if full_text.strip():
                    st.markdown(lang["ocr_result_header"])
                    st.text_area("", value=full_text, height=320)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"<p style='font-size:16px; font-weight:800; margin-bottom:8px;'>{lang['opt1']}</p>", unsafe_allow_html=True)
                        st_copy_to_clipboard(text=full_text, before_copy_label=lang["btn_copy"], after_copy_label=lang["copied"])
                        
                    with col2:
                        st.markdown(f"<p style='font-size:16px; font-weight:800; margin-bottom:8px;'>{lang['opt2']}</p>", unsafe_allow_html=True)
                        st.download_button(
                            label=lang["download_txt"],
                            data=full_text,
                            file_name="extracted_text.txt",
                            key="dl_txt_file"
                        )
                else:
                    st.warning(lang["warning_no_text"])
            except Exception as e:
                st.error(f"OCR Error: {e}")

# --- 7. الإعلانات والتذييل ---
st.markdown("<br><br>", unsafe_allow_html=True)

ads_code = """
<div style="text-align: center; width: 100%;">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781"
         crossorigin="anonymous"></script>
    <ins class="adsbygoogle"
         style="display:block; min-width:300px; max-width:970px; width:100%; height:90px; margin:auto;"
         data-ad-client="ca-pub-1091631464795781"
         data-ad-slot="8159670732"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</div>
"""
components.html(ads_code, height=110)

st.markdown(f"""
    <div class="footer">
        المحاسب الذكي Pro | <span>{lang["motto"]}</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
