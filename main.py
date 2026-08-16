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

# --- 3. اختيار اللغة والمظهر في أعلى الموقع (الوضع الفاتح افتراضي) ---
col_lang, col_theme = st.columns([2, 1])

with col_lang:
    selected_lang = st.selectbox(
        "🌐 Choose Language / اختر اللغة / زبان کا انتخاب کریں",
        ["العربية", "English", "اردو"],
        index=0,
        key="language_selector"
    )

with col_theme:
    selected_theme = st.selectbox(
        "🎨 Theme / المظهر / مظهر",
        ["الوضع الفاتح (Light)", "الوضع الداكن (Dark)"],
        index=0,
        key="theme_selector"
    )

# --- 4. قاموس الترجمة للغات الثلاث ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#0969da; font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً",
        "tab1_title": "📊 تحويل PDF و CSV إلى جداول Excel",
        "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات",
        "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF أو ملفات CSV إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي",
        "card2_desc": "استخراج النصوص العربية والإنجليزية والأوردو بدقة كاملة من المستندات المصورة والـ PDF",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF أو CSV الخاصة بالجداول هنا",
        "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدأ تحويل وجدولة: ",
        "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي لقراءة النص",
        "status_preparing": "📁 ملف قيد التحضير: ",
        "status_loading": "جاري معالجة البيانات وهيكلتها...",
        "status_ocr_loading": "جاري المسح الضوئي للمستند وتفسير الحروف...",
        "success_convert": "🚀 اكتمل التحويل بنجاح وبأعلى دقة!",
        "warning_no_tables": "⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.",
        "warning_no_text": "نعتذر، لم نكتشف حروفاً أو نصوصاً مقروءة في هذا المستند.",
        "download_excel": "📥 اضغط هنا لتحميل ملف Excel المستخرج",
        "download_txt": "📥 تحميل النص كملف TXT",
        "ocr_result_header": "#### ✅ النصوص التي تم العثور عليها ومسحها:",
        "opt1": "📋 الخيار الأول:",
        "opt2": "📥 الخيار الثاني:",
        "btn_copy": "📋 نسخ النص بالكامل",
        "copied": "✅ تم النسخ بنجاح!",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr",
        "align": "left",
        "title": "📊 Smart Accountant <span style='font-size:22px; color:#0969da; font-weight:normal;'>Pro</span>",
        "subtitle": "Advanced cloud system for smart data and table processing",
        "tab1_title": "📊 Convert PDF & CSV to Excel",
        "tab2_title": "🔍 Smart Text Extraction (OCR)",
        "card1_title": "Data Table Extractor",
        "card1_desc": "Upload your files to automatically convert any silent table inside PDF or CSV files into a formatted Excel file",
        "card2_title": "Text Reader & Scanner",
        "card2_desc": "Extract Arabic, English, and Urdu text with full accuracy from scanned documents and images",
        "uploader_pdf": "Drag and drop your PDF or CSV table files here",
        "uploader_ocr": "Upload invoice/document image (JPG, PNG) or scanned PDF file",
        "btn_convert": "Start Converting & Scheduling: ",
        "btn_ocr": "🚀 Launch AI to Read Text",
        "status_preparing": "📁 File preparing: ",
        "status_loading": "Processing and structuring data...",
        "status_ocr_loading": "Scanning document and interpreting characters...",
        "success_convert": "🚀 Conversion completed successfully with highest accuracy!",
        "warning_no_tables": "⚠️ No clear numerical tables detected in this file.",
        "warning_no_text": "Sorry, no readable characters or text detected in this document.",
        "download_excel": "📥 Click here to download the extracted Excel file",
        "download_txt": "📥 Download text as TXT file",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "opt1": "📋 Option 1:",
        "opt2": "📥 Option 2:",
        "btn_copy": "📋 Copy Full Text",
        "copied": "✅ Copied Successfully!",
        "motto": "Separation of liability... connection in trust"
    },
    "اردو": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:#0969da; font-weight:normal;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "tab1_title": "📊 پی ڈی ایف اور سی ایس وی کو ایکسل میں تبدیل کریں",
        "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "card1_desc": "پی ڈی ایف کے اندر موجود کسی بھی پوشیدہ ٹیبل یا سی ایس وی فائلوں کو خودکار طور پر فارمیٹ شدہ ایکسل فائل میں تبدیل کرنے کے لیے اپنی فائلیں اپ لوڈ کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسكينر",
        "card2_desc": "اسکین شدہ दस्तावेजات اور تصاویر سے مکمل درستگی کے ساتھ عربی، انگریزی اور اردو متن نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف یا سی ایس وی ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر (JPG, PNG) أو اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی اور شیڈولنگ شروع کریں: ",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "فائل کی تیاری: ",
        "status_loading": "ڈیٹا کو پروسیس اور سٹرکچر کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین اور حروف کی تشریح کی جا رہی ہے...",
        "success_convert": "🚀 اعلیٰ ترین درستگی کے ساتھ تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح عددی ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل حروف یا متن نہیں ملا۔",
        "download_excel": "📥 نکالی گئی ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں",
        "download_txt": "📥 متن کو TXT فائل کے طور بر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "opt1": "پہلا آپشن:",
        "opt2": "دوسرا آپشن:",
        "btn_copy": "📋 پورا متن کاپی کریں",
        "copied": "✅ کامیابی سے کاپی ہو گیا!",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

lang = translations[selected_lang]
is_light = "Light" in selected_theme or "الفاتح" in selected_theme

# --- 5. ستايل النيون والتصميم المتجاوب مع خلفية شبكة النقاط ---
def apply_theme_style(direction, align, is_light_mode):
    if is_light_mode:
        # خلفية شبكة النقاط - الوضع الفاتح
        bg_style = """
        background-color: #f8f9fa !important;
        background-image: radial-gradient(#0969da 0.8px, transparent 0.8px);
        background-size: 18px 18px;
        color: #1c2128;
        """
        card_bg = "background: rgba(255, 255, 255, 0.95); border: 1px solid #e1e4e8;"
        card_title_color = "#1f2328"
        card_desc_color = "#57606a"
        title_gradient = "background: linear-gradient(to right, #0969da, #1f6feb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
        select_bg = "background-color: #ffffff !important; border: 2px solid #0969da !important;"
        select_text = "color: #0969da !important;"
        popover_bg = "background-color: #ffffff !important;"
        popover_text = "color: #1f2328 !important;"
        uploader_bg = "background-color: rgba(255, 255, 255, 0.9) !important; border: 2px dashed #0969da !important;"
        uploader_text = "color: #1f2328 !important;"
        tab_bg = "background-color: rgba(241, 243, 245, 0.9); border: 1px solid #d0d7de;"
        tab_unselected = "color: #57606a;"
        textarea_bg = "background-color: #ffffff !important; color: #1f2328 !important; border: 1px solid #d0d7de !important;"
        footer_bg = "background-color: rgba(255, 255, 255, 0.95); color: #57606a; border-top: 1px solid #d0d7de;"
    else:
        # خلفية شبكة النقاط - الوضع الداكن
        bg_style = """
        background-color: #0d1117 !important;
        background-image: radial-gradient(rgba(88, 166, 255, 0.18) 1px, transparent 1px);
        background-size: 20px 20px;
        color: #e6edf3;
        """
        card_bg = "background: linear-gradient(145deg, rgba(22, 27, 34, 0.95) 0%, rgba(15, 19, 25, 0.95) 100%); border: 1px solid #30363d;"
        card_title_color = "#ffffff"
        card_desc_color = "#8b949e"
        title_gradient = "background: linear-gradient(to right, #ffffff, #58a6ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
        select_bg = "background: linear-gradient(135deg, rgba(31, 111, 235, 0.25) 0%, rgba(13, 68, 165, 0.4) 100%) !important; background-color: #161b22 !important; border: 2px solid #58a6ff !important;"
        select_text = "color: #58a6ff !important;"
        popover_bg = "background-color: #161b22 !important;"
        popover_text = "color: #ffffff !important;"
        uploader_bg = "background-color: rgba(22, 27, 34, 0.85) !important; border: 2px dashed #30363d !important;"
        uploader_text = "color: #ffffff !important;"
        tab_bg = "background-color: rgba(22, 27, 34, 0.7); border: 1px solid #21262d;"
        tab_unselected = "color: #8b949e;"
        textarea_bg = "background-color: #0d1117 !important; color: #e6edf3 !important; border: 1px solid #30363d !important;"
        footer_bg = "background-color: rgba(22, 27, 34, 0.95); color: #8b949e; border-top: 1px solid #30363d;"

    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700;900&display=swap');
    
    html, body, [class*="st-emotion-cache"], p, div, h1, h2, h3, span, label, textarea {{
        font-family: 'Cairo', sans-serif !important;
        direction: {direction} !important;
        text-align: {align} !important;
    }}

    .stApp {{
        {bg_style}
    }}

    header, [data-testid="stHeader"] {{
        visibility: hidden;
        display: none;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 1.5rem !important;
        padding-bottom: 8rem !important;
        padding-left: 5rem !important;
        padding-right: 5rem !important;
    }}

    [data-testid="stSelectbox"] {{
        margin-bottom: 20px !important;
        z-index: 9999 !important;
    }}

    [data-testid="stSelectbox"] label p {{
        font-size: 16px !important;
        font-weight: bold !important;
        {select_text}
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        {select_bg}
        border-radius: 12px !important;
        transition: all 0.3s ease-in-out;
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] div {{
        font-weight: bold !important;
    }}

    div[data-baseweb="popover"] {{
        {popover_bg}
        border: 2px solid #0969da !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        z-index: 999999 !important;
    }}
    
    div[data-baseweb="popover"] ul[role="listbox"],
    [data-testid="stSelectboxVirtualDropdown"] {{
        {popover_bg}
        border-radius: 12px !important;
    }}
    
    div[data-baseweb="popover"] li, li[role="option"] span, div[role="listbox"] div {{
        {popover_text}
        font-weight: 600 !important;
    }}
    
    div[data-baseweb="popover"] li:hover, li[role="option"]:hover {{
        background-color: #1f6feb !important;
        color: #ffffff !important;
    }}

    [data-testid="stFileUploader"] button span span {{
        display: none !important;  
    }}
    [data-testid="stFileUploader"] button span::after {{
        content: "Upload" !important; 
        color: white !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px;
        {tab_bg}
        padding: 8px;
        border-radius: 12px;
        backdrop-filter: blur(5px);
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        {tab_unselected}
        border: none;
        padding: 0 25px;
        font-weight: bold;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #1f6feb 0%, #0d44a5 100%) !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(31, 111, 235, 0.6);
        transform: scale(1.02);
    }}

    /* === صندوق رفع الملفات وتأثير التوهج عند التمرير === */
    [data-testid="stFileUploader"] {{
        {uploader_bg}
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        backdrop-filter: blur(5px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: #0969da !important;
        transform: translateY(-4px) scale(1.01) !important;
        box-shadow: 0 0 25px rgba(9, 105, 218, 0.45), 0 0 10px rgba(31, 111, 235, 0.2) !important;
    }}

    [data-testid="stFileUploader"] section *, 
    [data-testid="stFileUploader"] div, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] p {{
        {uploader_text}
    }}

    .icon-container {{
        font-size: 55px;
        margin-bottom: 15px;
        transition: all 0.4s ease;
        display: inline-block;
    }}
    
    .excel-icon {{ color: #2ea043; text-shadow: 0 0 20px rgba(46, 160, 67, 0.4); }}
    .ocr-icon {{ color: #0969da; text-shadow: 0 0 20px rgba(9, 105, 218, 0.4); }}
    
    .custom-card:hover .excel-icon {{
        transform: scale(1.15) translateY(-5px);
        filter: drop-shadow(0 0 15px #2ea043);
    }}
    .custom-card:hover .ocr-icon {{
        transform: scale(1.15) rotate(10deg);
        filter: drop-shadow(0 0 15px #0969da);
    }}

    .custom-card {{
        {card_bg}
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
        transition: 0.3s;
    }}

    .custom-card h3 {{
        color: {card_title_color} !important;
    }}

    .custom-card p {{
        color: {card_desc_color} !important;
    }}

    h1 {{
        font-weight: 900 !important;
        {title_gradient}
    }}

    .stButton>button {{
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 2rem !important;
        font-weight: bold !important;
        font-size: 16px !important;
        width: 100%;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    
    .stButton>button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(46, 160, 67, 0.5);
    }}

    [data-testid="stDownloadButton"] button {{
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }}

    .stTextArea textarea {{
        {textarea_bg}
        border-radius: 12px !important;
    }}

    .stCopyButton button {{
        background: linear-gradient(135deg, #8a2be2 0%, #4b0082 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }}

    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        {footer_bg}
        backdrop-filter: blur(8px);
        text-align: center;
        padding: 12px;
        font-size: 14px;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme_style(lang["direction"], lang["align"], is_light)

# --- 6. واجهة البرنامج الرئيسية مع أنيميشن المدينة الصناعية ---
col_anim, col_title = st.columns([1, 1.8]) if lang["direction"] == "rtl" else st.columns([1.8, 1])

industrial_city_anim_html = """
<style>
.city-container {
    width: 100%;
    height: 120px;
    position: relative;
    border-radius: 15px;
    background: linear-gradient(180deg, rgba(9, 105, 218, 0.1) 0%, rgba(13, 17, 23, 0.05) 100%);
    border: 1px solid rgba(9, 105, 218, 0.25);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    backdrop-filter: blur(4px);
}

.skyline {
    position: absolute;
    bottom: 30px;
    width: 100%;
    height: 60px;
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    opacity: 0.3;
}

.building {
    background: #0969da;
    width: 22px;
}
.b1 { height: 45px; }
.b2 { height: 30px; width: 30px; border-top: 3px solid #58a6ff; }
.b3 { height: 55px; }

.smoke {
    position: absolute;
    width: 6px;
    height: 6px;
    background: rgba(88, 166, 255, 0.6);
    border-radius: 50%;
    animation: puff 2s infinite ease-out;
}
.s1 { left: 22%; bottom: 85px; animation-delay: 0s; }
.s2 { left: 23%; bottom: 85px; animation-delay: 0.7s; }

@keyframes puff {
    0% { transform: translateY(0) scale(1); opacity: 0.8; }
    100% { transform: translateY(-25px) scale(2.5); opacity: 0; }
}

.road {
    width: 100%;
    height: 30px;
    background: rgba(9, 105, 218, 0.15);
    border-top: 2px solid rgba(9, 105, 218, 0.35);
    position: relative;
}

.truck {
    position: absolute;
    top: 5px;
    width: 32px;
    height: 12px;
    background: #0969da;
    border-radius: 3px;
    box-shadow: 0 0 8px rgba(9, 105, 218, 0.6);
    animation: drive 6s linear infinite;
}
.truck::after {
    content: '';
    position: absolute;
    right: -6px;
    bottom: 0;
    width: 8px;
    height: 8px;
    background: #58a6ff;
    border-radius: 2px;
}

.pedestrian {
    position: absolute;
    bottom: 4px;
    width: 4px;
    height: 10px;
    background: #2ea043;
    border-radius: 2px;
    box-shadow: 0 0 6px rgba(46, 160, 67, 0.8);
    animation: walk 10s linear infinite;
}

@keyframes drive {
    0% { left: -40px; }
    100% { left: 105%; }
}

@keyframes walk {
    0% { right: -20px; }
    100% { right: 105%; }
}
</style>

<div class="city-container">
    <div class="smoke s1"></div>
    <div class="smoke s2"></div>
    <div class="skyline">
        <div class="building b1"></div>
        <div class="building b2"></div>
        <div class="building b3"></div>
    </div>
    <div class="road">
        <div class="truck"></div>
        <div class="pedestrian"></div>
    </div>
</div>
"""

if lang["direction"] == "rtl":
    with col_anim:
        st.markdown(industrial_city_anim_html, unsafe_allow_html=True)
    with col_title:
        st.markdown(f"""
        <div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
            <h1>{lang["title"]}</h1>
            <p style='font-size:16px; margin-top:-10px;'>{lang["subtitle"]}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    with col_title:
        st.markdown(f"""
        <div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
            <h1>{lang["title"]}</h1>
            <p style='font-size:16px; margin-top:-10px;'>{lang["subtitle"]}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_anim:
        st.markdown(industrial_city_anim_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

# --- التبويب الأول: تحويل الجداول لـ Excel ---
with tab1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container excel-icon"><i class="fa-solid fa-file-excel"></i></div>
        <h3 style='margin:0;'>{lang["card1_title"]}</h3>
        <p style='font-size:14px; margin:5px 0;'>{lang["card1_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(lang["uploader_pdf"], type=["pdf", "csv"], key="table_uploader_main", accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            st.write("")
            with st.container():
                st.info(f"{lang['status_preparing']}{file.name}")
                if st.button(f"{lang['btn_convert']}{file.name}"):
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
                                        df = df.fillna('').replace([float('inf'), float('-inf')], 0)
                                        df.to_excel(writer, index=False, startrow=current_row, sheet_name='Data')
                                        current_row += len(df) + 2
                                    
                                st.success(lang["success_convert"])
                                clean_name = file.name.rsplit('.', 1)[0]
                                st.download_button(
                                    label=lang["download_excel"],
                                    data=output.getvalue(),
                                    file_name=f"Excel_{clean_name}.xlsx",
                                    mime="application/vnd.ms-excel"
                                )
                            else:
                                st.warning(lang["warning_no_tables"])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# --- التبويب الثاني: استخراج النصوص OCR ---
with tab2:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container ocr-icon"><i class="fa-solid fa-eye"></i></div>
        <h3 style='margin:0;'>{lang["card2_title"]}</h3>
        <p style='font-size:14px; margin:5px 0;'>{lang["card2_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    ocr_file = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "jpeg", "pdf"], key="ocr_main")
    
    if ocr_file:
        if st.button(lang["btn_ocr"]):
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
                        st.markdown(f"<p style='font-size:14px; margin-bottom:5px;'>{lang['opt1']}</p>", unsafe_allow_html=True)
                        st_copy_to_clipboard(text=full_text, before_copy_label=lang["btn_copy"], after_copy_label=lang["copied"])
                        
                    with col2:
                        st.markdown(f"<p style='font-size:14px; margin-bottom:5px;'>{lang['opt2']}</p>", unsafe_allow_html=True)
                        st.download_button(
                            label=lang["download_txt"],
                            data=full_text,
                            file_name="extracted_text.txt"
                        )
                else:
                    st.warning(lang["warning_no_text"])
            except Exception as e:
                st.error(f"OCR Error: {e}")

# --- 7. المساحة الإعلانية المخصصة والتذييل ---
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
        المحاسب الذكي Pro | <span style="color:#0969da;">الفصل في الذمة.. الوصل في الأمانة</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
