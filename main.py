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

# --- 2. دمج الخلفية المتحركة عبر مكون HTML مستقل تماماً (iframe لا يعيد التحميل أبداً) ---
def render_permanent_background(theme):
    bg_color = "#03070c" if theme == "dark" else "#7dd3fc"
    accent_color = "#38bdf8" if theme == "dark" else "#0284c7"
    
    bg_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: {bg_color};
        }}
        .nature-background {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            z-index: 9999;
            pointer-events: none;
        }}
        .ocean-waves {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 200%;
            height: 120px;
            background: linear-gradient(0deg, rgba(2, 132, 199, 0.35), transparent);
            border-radius: 100% 100% 0 0;
            animation: waveAnimation 8s ease-in-out infinite alternate;
        }}
        .ocean-waves:nth-child(2) {{
            bottom: -25px;
            opacity: 0.6;
            animation: waveAnimation 12s ease-in-out infinite alternate-reverse;
        }}
        @keyframes waveAnimation {{
            0% {{ transform: translateX(-10%) translateY(0); }}
            100% {{ transform: translateX(-30%) translateY(-15px); }}
        }}
        .trees-silhouette {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 90px;
            background: repeating-linear-gradient(90deg, rgba(16, 185, 129, 0.25), rgba(16, 185, 129, 0.25) 30px, transparent 30px, transparent 60px);
            clip-path: polygon(0% 100%, 5% 40%, 10% 100%, 15% 30%, 20% 100%, 25% 50%, 30% 100%, 35% 20%, 40% 100%, 45% 45%, 50% 100%, 55% 35%, 60% 100%, 65% 25%, 70% 100%, 75% 50%, 80% 100%, 85% 30%, 90% 100%, 95% 45%, 100% 100%);
        }}
        .bird {{
            position: absolute;
            width: 20px;
            height: 10px;
            border-bottom: 2px solid {accent_color};
            border-radius: 50%;
            opacity: 0.8;
            animation: flyBird 20s linear infinite;
        }}
        .bird:nth-of-type(1) {{ top: 15%; left: -10%; animation-duration: 18s; animation-delay: 0s; }}
        .bird:nth-of-type(2) {{ top: 25%; left: -15%; animation-duration: 24s; animation-delay: 4s; transform: scale(0.7); }}
        .bird:nth-of-type(3) {{ top: 10%; left: -20%; animation-duration: 15s; animation-delay: 8s; transform: scale(0.5); }}
        @keyframes flyBird {{
            0% {{ transform: translateX(0) translateY(0) rotate(0deg); }}
            50% {{ transform: translateX(60vw) translateY(-40px) rotate(-10deg); }}
            100% {{ transform: translateX(120vw) translateY(10px) rotate(5deg); }}
        }}
    </style>
    </head>
    <body>
        <div class="nature-background">
            <div class="bird"></div>
            <div class="bird"></div>
            <div class="bird"></div>
            <div class="trees-silhouette"></div>
            <div class="ocean-waves"></div>
            <div class="ocean-waves"></div>
        </div>
    </body>
    </html>
    """
    components.html(f"""
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -999; pointer-events: none;">
        <iframe srcdoc="{bg_html.replace('"', '&quot;')}" style="width: 100%; height: 100%; border: none; pointer-events: none;"></iframe>
    </div>
    """, height=0, width=0)

# --- 3. زر تبديل الثيم (داكن / فاتح) واختيار اللغة في الأعلى ---
col_top1, col_top2 = st.columns([6, 1])

with col_top1:
    selected_lang = st.selectbox(
        "🌐 Choose Language / اختر اللغة / زبان کا انتخاب کریں",
        ["العربية", "English", "اردو"],
        index=0,
        key="language_selector"
    )

with col_top2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    theme_mode = st.toggle("☀️ / 🌙", value=True, key="theme_switcher_toggle", help="تبديل الثيم (داكن / فاتح)")

current_theme = "dark" if theme_mode else "light"

# استدعاء الخلفية الثابتة والمستقلة للحركة
render_permanent_background(current_theme)

# --- 4. قاموس الترجمة للغات الثلاث (تم تنظيف النصوص المكررة ومنع تداخل الكلمات) ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; color:var(--accent-color); font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً",
        "tab1_title": "📊 تحويل PDF و CSV إلى Excel",
        "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات",
        "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF أو ملفات CSV إلى ملف إكسيل منسق تلقائياً",
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
        "title": "📊 Smart Accountant <span style='font-size:22px; color:var(--accent-color); font-weight:normal;'>Pro</span>",
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
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:var(--accent-color); font-weight:normal;'>Pro</span>",
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

# --- 5. تطبيق التنسيقات العامة للواجهة واللمسات الفنية التفاعلية للأزرار ---
def apply_ui_style(direction, align, theme):
    bg_gradient = "linear-gradient(180deg, rgba(10,25,47,0.85) 0%, rgba(6,16,30,0.85) 60%, rgba(3,7,12,0.85) 100%)" if theme == "dark" else "linear-gradient(180deg, rgba(224,242,254,0.85) 0%, rgba(186,230,253,0.85) 60%, rgba(125,211,252,0.85) 100%)"
    text_color = "#e6edf3" if theme == "dark" else "#0f172a"
    card_bg = "linear-gradient(145deg, rgba(22, 27, 34, 0.9) 0%, rgba(15, 19, 25, 0.95) 100%)" if theme == "dark" else "linear-gradient(145deg, rgba(255, 255, 255, 0.9) 100%, rgba(240, 249, 255, 0.9) 100%)"
    border_color = "#30363d" if theme == "dark" else "#bae6fd"
    sub_text = "#8b949e" if theme == "dark" else "#334155"
    accent_color = "#38bdf8" if theme == "dark" else "#0284c7"
    
    select_bg = "#0b1329" if theme == "dark" else "#ffffff"
    select_text = "#f8fafc" if theme == "dark" else "#0f172a"
    dropdown_hover = "#1e293b" if theme == "dark" else "#e0f2fe"
    
    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    html, body, [class*="st-emotion-cache"], p, div, h1, h2, h3, span, label, textarea {{
        font-family: 'Cairo', sans-serif !important;
        direction: {direction} !important;
        text-align: {align} !important;
    }}

    .stApp {{
        background: {bg_gradient} !important;
        color: {text_color};
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

    /* صندوق اختيار اللغة الرئيسي */
    [data-testid="stSelectbox"] {{
        background-color: {select_bg} !important;
        padding: 10px 15px !important;
        border-radius: 14px !important;
        border: 2px solid {accent_color} !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }}

    [data-testid="stSelectbox"] label p {{
        font-size: 16px !important;
        font-weight: 700 !important;
        color: {accent_color} !important;
        margin-bottom: 5px !important;
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background-color: {select_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        color: {select_text} !important;
    }}

    [data-testid="stSelectbox"] div[data-baseweb="select"] * {{
        color: {select_text} !important;
        background-color: transparent !important;
    }}

    /* القائمة المنبثقة وعناصر القائمة لمنع الشفافية وضمان عدم التداخل */
    div[data-baseweb="popover"], 
    div[data-baseweb="menu"], 
    ul[role="listbox"],
    div[id^="baseui-menu-"] {{
        background-color: {select_bg} !important;
        background: {select_bg} !important;
        border: 2px solid {accent_color} !important;
        border-radius: 12px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.7) !important;
        opacity: 1 !important;
    }}

    li[role="option"], 
    div[role="option"],
    [data-baseweb="menu"] li {{
        background-color: {select_bg} !important;
        color: {select_text} !important;
        font-family: 'Cairo', sans-serif !important;
        font-weight: bold !important;
        padding: 10px 15px !important;
        opacity: 1 !important;
    }}

    li[role="option"]:hover, 
    div[role="option"]:hover,
    [data-baseweb="menu"] li:hover {{
        background-color: {dropdown_hover} !important;
        color: {accent_color} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px;
        background-color: rgba(22, 27, 34, 0.7);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid {border_color};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        color: {sub_text};
        border: none;
        padding: 0 25px;
        font-weight: bold;
        transition: all 0.4s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1) !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.5);
        transform: scale(1.02);
    }}

    [data-testid="stFileUploader"] {{
        background-color: {card_bg} !important;
        border: 2px dashed {border_color} !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}

    .custom-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        backdrop-filter: blur(5px);
    }}

    h1 {{
        color: {text_color} !important;
        font-weight: 900 !important;
        background: linear-gradient(to right, {text_color}, {accent_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* --- اللمسة الفنية العصرية للأزرار والتفاعل مع حركة الماوس (Hover Effects & Glassmorphism) --- */
    .stButton>button, [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: white !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 14px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }}

    /* تأثير التوهج والارتفاع عند مرور الماوس (Hover Animation) */
    .stButton>button:hover, [data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-primary"]:hover {{
        background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 8px 25px rgba(56, 189, 248, 0.5), 0 0 15px rgba(56, 189, 248, 0.3) !important;
        transform: translateY(-3px) scale(1.01) !important;
    }}

    /* تأثير عند الضغط على الزر (Active Click) */
    .stButton>button:active {{
        transform: translateY(1px) scale(0.99) !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4) !important;
    }}

    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(8px);
        color: {sub_text};
        text-align: center;
        padding: 12px;
        border-top: 1px solid {border_color};
        font-size: 14px;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_ui_style(lang["direction"], lang["align"], current_theme)

# --- 6. واجهة البرنامج الرئيسية ---
st.markdown(f"""
<div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
    <h1>{lang["title"]}</h1>
    <p style='font-size:16px; color:var(--text-secondary); margin-top:-10px;'>{lang["subtitle"]}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

# --- التبويب الأول ---
with tab1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container excel-icon"><i class="fa-solid fa-file-excel" style="font-size: 50px; color: #38bdf8;"></i></div>
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
                                        df = df.fillna('').replace([float('inf'), float('-inf')], 0)
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
        <div class="icon-container ocr-icon"><i class="fa-solid fa-eye" style="font-size: 50px; color: #38bdf8;"></i></div>
        <h3 style='margin:0;'>{lang["card2_title"]}</h3>
        <p style='font-size:14px; margin:5px 0;'>{lang["card2_desc"]}</p>
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
                        st.markdown(f"<p style='font-size:14px; margin-bottom:5px;'>{lang['opt1']}</p>", unsafe_allow_html=True)
                        st_copy_to_clipboard(text=full_text, before_copy_label=lang["btn_copy"], after_copy_label=lang["copied"])
                        
                    with col2:
                        st.markdown(f"<p style='font-size:14px; margin-bottom:5px;'>{lang['opt2']}</p>", unsafe_allow_html=True)
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
        المحاسب الذكي Pro | <span style="color:#38bdf8;">{lang["motto"]}</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
