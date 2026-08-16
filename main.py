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

# --- 3. اختيار اللغة والمظهر في أعلى الموقع ---
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
        ["ثلاثي الأبعاد الفاتح (3D Light)", "ثلاثي الأبعاد الداكن (3D Dark)"],
        index=1,
        key="theme_selector"
    )

# --- 4. قاموس الترجمة للغات الثلاث ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:28px; color:#38bdf8; font-weight:bold;'>Pro</span>",
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
        "title": "📊 Smart Accountant <span style='font-size:28px; color:#38bdf8; font-weight:bold;'>Pro</span>",
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
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:28px; color:#38bdf8; font-weight:bold;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "tab1_title": "📊 پی ڈی ایف اور سی ایس وی کو ایکسل میں تبدیل کریں",
        "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "card1_desc": "پی ڈی ایف کے اندر موجود کسی بھی پوشیدہ ٹیبل یا سی ایس وی فائلوں کو خودکار طور پر فارمیٹ شدہ ایکسل فائل میں تبدیل کرنے کے لیے اپنی فائلیں اپ لوڈ کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسكينر",
        "card2_desc": "اسکین شدہ دستاویزات اور تصاویر سے مکمل درستگی کے ساتھ عربی، انگریزی اور اردو متن نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف یا سی ایس وی ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر (JPG, PNG) یا اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی اور شیڈولنگ شروع کریں: ",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "فائل کی تیاری: ",
        "status_loading": "ڈیٹا کو پروسیس اور سٹرکچر کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین اور حروف کی تشریح کی جا رہی ہے...",
        "success_convert": "🚀 اعلیٰ ترین درستگی کے ساتھ تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح عددی ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل حروف یا متن نہیں ملا۔",
        "download_excel": "📥 نکالی گئی ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں",
        "download_txt": "📥 متن کو TXT فائل کے طور پر ڈاؤن لوڈ کریں",
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

# --- 5. ستايل Google Expressive بالتباين العالي والخطوط الكبيرة ---
def apply_theme_style(direction, align, is_light_mode):
    if is_light_mode:
        bg_style = """
        background: #f8fafc !important;
        color: #0f172a;
        """
        card_bg = """
        background: #ffffff;
        border: 2px solid #cbd5e1;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
        """
        card_title_color = "#0f172a"
        card_desc_color = "#334155"
        title_gradient = "color: #0284c7;"
        select_bg = "background: #ffffff !important; border: 2px solid #0284c7 !important;"
        select_text = "color: #0369a1 !important;"
        popover_bg = "background-color: #ffffff !important;"
        popover_text = "color: #0f172a !important;"
        uploader_bg = """
        background: #f1f5f9 !important;
        border: 3px dashed #0284c7 !important;
        """
        uploader_text = "color: #0f172a !important;"
        tab_bg = "background: #e2e8f0; border: 1px solid #cbd5e1;"
        tab_unselected = "color: #475569;"
        textarea_bg = "background: #ffffff !important; color: #0f172a !important; border: 2px solid #94a3b8 !important;"
        footer_bg = "background: #ffffff; color: #334155; border-top: 2px solid #cbd5e1;"
    else:
        # تصميم داكن بتباين عالي بأسلوب Google Expressive M3
        bg_style = """
        background: #090d16 !important;
        color: #f8fafc;
        """
        card_bg = """
        background: #111827;
        border: 2px solid #1e293b;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
        """
        card_title_color = "#ffffff"
        card_desc_color = "#cbd5e1"
        title_gradient = "background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"
        select_bg = "background: #111827 !important; border: 2px solid #38bdf8 !important;"
        select_text = "color: #38bdf8 !important;"
        popover_bg = "background-color: #111827 !important;"
        popover_text = "color: #f8fafc !important;"
        uploader_bg = """
        background: #0f172a !important;
        border: 3px dashed #38bdf8 !important;
        box-shadow: inset 0 0 20px rgba(56, 189, 248, 0.05) !important;
        """
        uploader_text = "color: #f8fafc !important;"
        tab_bg = "background: #111827; border: 2px solid #1e293b;"
        tab_unselected = "color: #94a3b8;"
        textarea_bg = "background: #0b0f19 !important; color: #38bdf8 !important; border: 2px solid #38bdf8 !important;"
        footer_bg = "background: #0b0f19; color: #cbd5e1; border-top: 2px solid #1e293b;"

    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;900&display=swap');
    
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
        padding-top: 2rem !important;
        padding-bottom: 9rem !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
    }}

    [data-testid="stSelectbox"] label p {{
        font-size: 18px !important;
        font-weight: 900 !important;
        {select_text}
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        {select_bg}
        border-radius: 16px !important;
        font-size: 18px !important;
    }}

    div[data-baseweb="popover"] {{
        {popover_bg}
        border: 2px solid #38bdf8 !important;
        border-radius: 16px !important;
        z-index: 999999 !important;
    }}
    
    div[data-baseweb="popover"] li, li[role="option"] span {{
        {popover_text}
        font-size: 17px !important;
        font-weight: 700 !important;
    }}
    
    div[data-baseweb="popover"] li:hover {{
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 16px;
        {tab_bg}
        padding: 12px;
        border-radius: 20px;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 56px;
        background-color: transparent;
        border-radius: 14px;
        {tab_unselected}
        border: none;
        padding: 0 30px;
        font-size: 18px !important;
        font-weight: 900 !important;
        transition: all 0.3s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.4);
    }}

    [data-testid="stFileUploader"] {{
        {uploader_bg}
        border-radius: 24px !important;
        padding: 40px !important;
        transition: all 0.3s ease !important;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: #34d399 !important;
        transform: translateY(-4px);
    }}

    [data-testid="stFileUploader"] section *, 
    [data-testid="stFileUploader"] p {{
        {uploader_text}
        font-size: 18px !important;
        font-weight: 700 !important;
    }}

    .icon-container {{
        font-size: 64px;
        margin-bottom: 15px;
    }}
    
    .excel-icon {{ color: #34d399; filter: drop-shadow(0 0 12px rgba(52, 211, 153, 0.4)); }}
    .ocr-icon {{ color: #38bdf8; filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.4)); }}

    .custom-card {{
        {card_bg}
        border-radius: 24px;
        padding: 35px;
        text-align: center;
        margin-bottom: 30px;
    }}

    .custom-card h3 {{
        color: {card_title_color} !important;
        font-size: 28px !important;
        font-weight: 900 !important;
    }}

    .custom-card p {{
        color: {card_desc_color} !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }}

    h1 {{
        font-size: 42px !important;
        font-weight: 900 !important;
        {title_gradient}
    }}

    .stButton>button {{
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        width: 100%;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.35);
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(16, 185, 129, 0.5);
    }}

    [data-testid="stDownloadButton"] button {{
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        font-size: 19px !important;
        font-weight: 900 !important;
        padding: 0.9rem 2rem !important;
        box-shadow: 0 10px 25px rgba(56, 189, 248, 0.35);
        width: 100%;
    }}

    .stTextArea textarea {{
        {textarea_bg}
        border-radius: 18px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        line-height: 1.8 !important;
    }}

    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        {footer_bg}
        text-align: center;
        padding: 18px;
        font-size: 18px;
        font-weight: 900;
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
    height: 130px;
    position: relative;
    border-radius: 20px;
    background: linear-gradient(180deg, rgba(56, 189, 248, 0.15) 0%, rgba(15, 23, 42, 0.2) 100%);
    border: 2px solid rgba(56, 189, 248, 0.3);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

.skyline {
    position: absolute;
    bottom: 30px;
    width: 100%;
    height: 60px;
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    opacity: 0.5;
}

.building {
    background: #38bdf8;
    width: 24px;
}
.b1 { height: 48px; }
.b2 { height: 32px; width: 32px; border-top: 4px solid #34d399; }
.b3 { height: 58px; }

.smoke {
    position: absolute;
    width: 8px;
    height: 8px;
    background: rgba(56, 189, 248, 0.8);
    border-radius: 50%;
    animation: puff 2s infinite ease-out;
}
.s1 { left: 22%; bottom: 85px; animation-delay: 0s; }
.s2 { left: 23%; bottom: 85px; animation-delay: 0.7s; }

@keyframes puff {
    0% { transform: translateY(0) scale(1); opacity: 0.9; }
    100% { transform: translateY(-30px) scale(2.8); opacity: 0; }
}

.road {
    width: 100%;
    height: 32px;
    background: rgba(56, 189, 248, 0.2);
    border-top: 2px solid rgba(56, 189, 248, 0.4);
    position: relative;
}

.truck {
    position: absolute;
    top: 6px;
    width: 36px;
    height: 14px;
    background: #38bdf8;
    border-radius: 4px;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.9);
    animation: drive 6s linear infinite;
}

.pedestrian {
    position: absolute;
    bottom: 4px;
    width: 5px;
    height: 12px;
    background: #34d399;
    border-radius: 2px;
    box-shadow: 0 0 10px rgba(52, 211, 153, 0.9);
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
            <p style='font-size:20px; font-weight:700; margin-top:-10px;'>{lang["subtitle"]}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    with col_title:
        st.markdown(f"""
        <div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
            <h1>{lang["title"]}</h1>
            <p style='font-size:20px; font-weight:700; margin-top:-10px;'>{lang["subtitle"]}</p>
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
        <p style='margin:10px 0;'>{lang["card1_desc"]}</p>
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
        <p style='margin:10px 0;'>{lang["card2_desc"]}</p>
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
                    st.text_area("", value=full_text, height=350)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"<p style='font-size:16px; font-weight:bold; margin-bottom:5px;'>{lang['opt1']}</p>", unsafe_allow_html=True)
                        st_copy_to_clipboard(text=full_text, before_copy_label=lang["btn_copy"], after_copy_label=lang["copied"])
                        
                    with col2:
                        st.markdown(f"<p style='font-size:16px; font-weight:bold; margin-bottom:5px;'>{lang['opt2']}</p>", unsafe_allow_html=True)
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
        المحاسب الذكي Pro | <span style="color:#38bdf8;">الفصل في الذمة.. الوصل في الأمانة</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
