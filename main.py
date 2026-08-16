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

# --- 3. اختيار اللغة والمظهر ---
# استخدام الجلسة للحفاظ على القيم
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "العربية"
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "ثلاثي الأبعاد الفاتح (3D Light)"

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

# --- 5. ستايل وتنسيق الصفحة والأنيميشن المدمجة بالخلفية ---
def apply_theme_style(direction, align, is_light_mode):
    if is_light_mode:
        bg_style = """
        background: 
            radial-gradient(circle at 20% 20%, rgba(9, 105, 218, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 80% 30%, rgba(46, 160, 67, 0.12) 0%, transparent 45%),
            linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%) !important;
        background-attachment: fixed !important;
        color: #1f2328;
        """
        card_bg = "background: rgba(255, 255, 255, 0.75); border: 1px solid rgba(255, 255, 255, 0.9); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);"
        card_title_color = "#0f172a"
        card_desc_color = "#475569"
        title_color = "color: #0f172a;"
        select_bg = "background: rgba(255, 255, 255, 0.9) !important; border: 2px solid #0969da !important;"
        select_text = "color: #0969da !important;"
        uploader_bg = "background: rgba(255, 255, 255, 0.7) !important; border: 2px dashed #0969da !important;"
        uploader_text = "color: #0f172a !important;"
        tab_bg = "background: rgba(255, 255, 255, 0.6); border: 1px solid rgba(208, 215, 222, 0.8);"
        tab_unselected = "color: #64748b;"
        textarea_bg = "background: rgba(255, 255, 255, 0.9) !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important;"
        footer_bg = "background: rgba(255, 255, 255, 0.9); color: #475569; border-top: 1px solid #e2e8f0;"
        header_box_bg = "rgba(255, 255, 255, 0.65)"
    else:
        bg_style = """
        background: 
            radial-gradient(circle at 15% 15%, rgba(56, 139, 253, 0.22) 0%, transparent 45%),
            radial-gradient(circle at 85% 25%, rgba(46, 160, 67, 0.18) 0%, transparent 45%),
            linear-gradient(135deg, #0b0f17 0%, #111827 100%) !important;
        background-attachment: fixed !important;
        color: #f1f5f9;
        """
        card_bg = "background: rgba(17, 24, 39, 0.75); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);"
        card_title_color = "#ffffff"
        card_desc_color = "#94a3b8"
        title_color = "color: #ffffff;"
        select_bg = "background: rgba(17, 24, 39, 0.9) !important; border: 2px solid #3b82f6 !important;"
        select_text = "color: #60a5fa !important;"
        uploader_bg = "background: rgba(17, 24, 39, 0.7) !important; border: 2px dashed #3b82f6 !important;"
        uploader_text = "color: #f1f5f9 !important;"
        tab_bg = "background: rgba(17, 24, 39, 0.6); border: 1px solid rgba(255, 255, 255, 0.08);"
        tab_unselected = "color: #94a3b8;"
        textarea_bg = "background: rgba(11, 15, 23, 0.9) !important; color: #f1f5f9 !important; border: 1px solid #1e293b !important;"
        footer_bg = "background: rgba(17, 24, 39, 0.9); color: #94a3b8; border-top: 1px solid #1e293b;"
        header_box_bg = "rgba(17, 24, 39, 0.65)"

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
        padding-top: 1rem !important;
        padding-bottom: 8rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }}

    /* === حاوية الهيدر الموحدة المستطيلة مع خلفية الأنيميشن === */
    .header-wrapper {{
        position: relative;
        width: 100%;
        border-radius: 20px;
        background: {header_box_bg};
        border: 2px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        padding: 25px;
        margin-bottom: 30px;
        backdrop-filter: blur(12px);
    }}

    /* خلفية المدينة الصناعية المتحركة بنفس أبعاد المستطيل الأحمر */
    .header-bg-anim {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 1;
        pointer-events: none;
        opacity: 0.25;
    }}

    .header-content {{
        position: relative;
        z-index: 2;
    }}

    .city-skyline {{
        position: absolute;
        bottom: 25px;
        width: 100%;
        height: 70px;
        display: flex;
        align-items: flex-end;
        justify-content: space-around;
    }}

    .building {{
        background: #2563eb;
        width: 30px;
    }}
    .b1 {{ height: 50px; }}
    .b2 {{ height: 35px; width: 45px; border-top: 3px solid #60a5fa; }}
    .b3 {{ height: 65px; }}

    .smoke {{
        position: absolute;
        width: 8px;
        height: 8px;
        background: rgba(96, 165, 250, 0.7);
        border-radius: 50%;
        animation: puff 2.5s infinite ease-out;
    }}
    .s1 {{ left: 22%; bottom: 95px; animation-delay: 0s; }}
    .s2 {{ left: 23%; bottom: 95px; animation-delay: 0.8s; }}

    @keyframes puff {{
        0% {{ transform: translateY(0) scale(1); opacity: 0.8; }}
        100% {{ transform: translateY(-30px) scale(3); opacity: 0; }}
    }}

    .road {{
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 25px;
        background: rgba(37, 99, 235, 0.2);
        border-top: 2px solid rgba(59, 130, 246, 0.4);
    }}

    .truck {{
        position: absolute;
        top: 4px;
        width: 40px;
        height: 14px;
        background: #2563eb;
        border-radius: 3px;
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.8);
        animation: drive 8s linear infinite;
    }}

    @keyframes drive {{
        0% {{ left: -50px; }}
        100% {{ left: 105%; }}
    }}

    [data-testid="stSelectbox"] label p {{
        font-size: 15px !important;
        font-weight: bold !important;
        {select_text}
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        {select_bg}
        border-radius: 12px !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px;
        {tab_bg}
        padding: 10px;
        border-radius: 16px;
        backdrop-filter: blur(12px);
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        background-color: transparent;
        border-radius: 10px;
        {tab_unselected}
        border: none;
        padding: 0 25px;
        font-weight: bold;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    }}

    [data-testid="stFileUploader"] {{
        {uploader_bg}
        border-radius: 20px !important;
        padding: 30px !important;
    }}

    .custom-card {{
        {card_bg}
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin-bottom: 25px;
        backdrop-filter: blur(12px);
    }}

    .custom-card h3 {{ color: {card_title_color} !important; }}
    .custom-card p {{ color: {card_desc_color} !important; }}

    h1 {{
        font-weight: 900 !important;
        {title_color}
        margin: 0 !important;
    }}

    .stButton>button {{
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 0.8rem 2rem !important;
        font-weight: bold !important;
        width: 100%;
    }}

    [data-testid="stDownloadButton"] button {{
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        width: 100%;
    }}

    .stTextArea textarea {{
        {textarea_bg}
        border-radius: 14px !important;
    }}

    /* === التذييل الموحد مع وضع العبارة في المنتصف تماماً === */
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        {footer_bg}
        backdrop-filter: blur(12px);
        text-align: center !important;
        padding: 12px;
        font-size: 15px;
        font-weight: bold;
        z-index: 999;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
    }}

    .footer-motto {{
        color: #10b981;
        font-size: 16px;
        letter-spacing: 0.5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# تطبيق الأسلوب حسب خيارات المستخدم
selected_lang = st.session_state.selected_lang
selected_theme = st.session_state.selected_theme
lang = translations[selected_lang]
is_light = "Light" in selected_theme or "الفاتح" in selected_theme

apply_theme_style(lang["direction"], lang["align"], is_light)

# --- 6. المستطيل الأحمر العشرين الموحد (الهيدر مع الصورة المتحركة بالخلفية) ---
st.markdown("""
<div class="header-wrapper">
    <div class="header-bg-anim">
        <div class="smoke s1"></div>
        <div class="smoke s2"></div>
        <div class="city-skyline">
            <div class="building b1"></div>
            <div class="building b2"></div>
            <div class="building b3"></div>
        </div>
        <div class="road">
            <div class="truck"></div>
        </div>
    </div>
    <div class="header-content">
""", unsafe_allow_html=True)

# وضع القوائم والعنوان داخل الحاوية المصممة
col_sel1, col_sel2 = st.columns(2)

with col_sel1:
    st.selectbox(
        "🌐 Choose Language / اختر اللغة / زبان کا انتخاب کریں",
        ["العربية", "English", "اردو"],
        key="selected_lang"
    )

with col_sel2:
    st.selectbox(
        "🎨 Theme / المظهر / مظهر",
        ["ثلاثي الأبعاد الفاتح (3D Light)", "ثلاثي الأبعاد الداكن (3D Dark)"],
        key="selected_theme"
    )

st.markdown(f"""
    <div style='text-align: center; padding-top: 10px;'>
        <h1>{lang["title"]}</h1>
        <p style='font-size:17px; margin-top:5px; font-weight: bold;'>{lang["subtitle"]}</p>
    </div>
</div>
</div>
""", unsafe_allow_html=True)

# --- 7. التبويبات المخصصة للتطبيق ---
tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

# --- التبويب الأول: تحويل الجداول ל- Excel ---
with tab1:
    st.markdown(f"""
    <div class="custom-card">
        <div style="font-size: 50px; color: #10b981; margin-bottom: 10px;"><i class="fa-solid fa-file-excel"></i></div>
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
        <div style="font-size: 50px; color: #3b82f6; margin-bottom: 10px;"><i class="fa-solid fa-eye"></i></div>
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

# --- 8. المساحة الإعلانية والتذييل السفلي (المستطيل الأخضر) ---
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

# وضع الشعار والمقولة في أسفل الصفحة بالمنتصف تماماً
st.markdown(f"""
    <div class="footer">
        <span>المحاسب الذكي Pro © 2026</span>
        <span>|</span>
        <span class="footer-motto">« {lang["motto"]} »</span>
    </div>
""", unsafe_allow_html=True)
