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

# --- 3. اختيار اللغة في أعلى الموقع (تم رفعها وتكبيرها وتعديل تصميمها) ---
selected_lang = st.selectbox(
    "🌐 Choose Language / اختر اللغة / زبان کا انتخاب کریں",
    ["العربية", "English", "اردو"],
    index=0,
    key="language_selector"
)

# --- 4. قاموس الترجمة للغات الثلاث ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً",
        "tab1_title": "📊 تحويل PDF إلى جداول Excel",
        "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات",
        "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي",
        "card2_desc": "استخراج النصوص العربية والإنجليزية والأوردو بدقة كاملة من المستندات المصورة والـ PDF",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF الخاصة بالجداول هنا",
        "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدأ تحويل وجدولة: ",
        "btn_ocr": "🚀 اطلَق الذكاء الاصطناعي لقراءة النص",
        "status_preparing": "📁 ملف قيد التحضير: ",
        "status_loading": "جاري تفكيك الجداول وهيكلتها...",
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
        "title": "📊 Smart Accountant <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "Advanced cloud system for smart data and table processing",
        "tab1_title": "📊 Convert PDF to Excel",
        "tab2_title": "🔍 Smart Text Extraction (OCR)",
        "card1_title": "Data Table Extractor",
        "card1_desc": "Upload your files to automatically convert any silent table inside PDF into a formatted Excel file",
        "card2_title": "Text Reader & Scanner",
        "card2_desc": "Extract Arabic, English, and Urdu text with full accuracy from scanned documents and images",
        "uploader_pdf": "Drag and drop your PDF table files here",
        "uploader_ocr": "Upload invoice/document image (JPG, PNG) or scanned PDF file",
        "btn_convert": "Start Converting & Scheduling: ",
        "btn_ocr": "🚀 Launch AI to Read Text",
        "status_preparing": "📁 File preparing: ",
        "status_loading": "Deconstructing and structuring tables...",
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
    "urdu": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "tab1_title": "📊 پی ڈی ایف کو ایکسل میں تبدیل کریں",
        "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "card1_desc": "پی ڈی ایف کے اندر موجود کسی بھی پوشیدہ ٹیبل کو خودکار طور پر فارمیٹ شدہ ایکسل فائل میں تبدیل کرنے کے لیے اپنی فائلیں اپ لوڈ کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسكينر",
        "card2_desc": "اسکین شدہ दस्तावेजات اور تصاویر سے مکمل درستگی کے ساتھ عربی، انگریزی اور اردو متن نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر (JPG, PNG) یا اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی اور شیڈولنگ شروع کریں: ",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "📁 فائل کی تیاری: ",
        "status_loading": "ٹیبلز کو ڈی کنسٹریکٹ اور سٹرکچر کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین اور حروف کی تشریح کی جا رہی ہے...",
        "success_convert": "🚀 اعلیٰ ترین درستگی کے ساتھ تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح عددی ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل حروف یا متن نہیں ملا۔",
        "download_excel": "📥 نکالی گئی ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں",
        "download_txt": "📥 متن کو TXT فائل کے طور پر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "opt1": "📋 پہلا آپشن:",
        "opt2": "📥 دوسرا آپشن:",
        "btn_copy": "📋 پورا متن کاپی کریں",
        "copied": "✅ کامیابی سے کاپی ہو گیا!",
        "motto": "ذمہ داری کی علیحدگی... امانت میں ملاپ"
    }
}

lang = translations[selected_lang]

# --- 5. ستايل النيون المتطور وتوجيه المحاذاة وتخصيص صندوق اللغة (CSS) ---
def apply_neon_style(direction, align):
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
        background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important;
        color: #e6edf3;
    }}

    header, [data-testid="stHeader"] {{
        visibility: hidden;
        display: none;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        padding: 1rem 5rem 8rem 5rem;
    }}

    /* --- تخصيص وتكبير وتلوين خيار تحديد اللغة بالنيون الأزرق --- */
    [data-testid="stSelectbox"] label p {{
        font-size: 18px !important;
        font-weight: bold !important;
        color: #58a6ff !important;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.5);
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
    }}
    
    [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {{
        border-color: #58a6ff !important;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
    }}

    div[role="listbox"] {{
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px;
        background-color: rgba(22, 27, 34, 0.5);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #21262d;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        color: #8b949e;
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

    [data-testid="stFileUploader"] {{
        background-color: rgba(22, 27, 34, 0.7) !important;
        border: 2px dashed #21262d !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.4s ease;
    }}
    
    [data-testid="stFileUploader"]:hover {{
        border-color: #58a6ff !important;
        background-color: rgba(28, 33, 40, 0.9) !important;
        box-shadow: 0 0 25px rgba(88, 166, 255, 0.25);
        transform: translateY(-4px);
    }}

    [data-testid="stFileUploader"] section *, 
    [data-testid="stFileUploader"] div, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] p {{
        color: #ffffff !important;
    }}

    .icon-container {{
        font-size: 55px;
        margin-bottom: 15px;
        transition: all 0.4s ease;
        display: inline-block;
    }}
    
    .excel-icon {{ color: #2ea043; text-shadow: 0 0 20px rgba(46, 160, 67, 0.4); }}
    .ocr-icon {{ color: #58a6ff; text-shadow: 0 0 20px rgba(88, 166, 255, 0.4); }}
    
    .custom-card:hover .excel-icon {{
        transform: scale(1.15) translateY(-5px);
        filter: drop-shadow(0 0 15px #2ea043);
    }}
    .custom-card:hover .ocr-icon {{
        transform: scale(1.15) rotate(10deg);
        filter: drop-shadow(0 0 15px #58a6ff);
    }}

    .custom-card {{
        background: linear-gradient(145deg, #161b22 0%, #0f1319 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        transition: 0.3s;
    }}

    h1 {{
        color: #ffffff !important;
        font-weight: 900 !important;
        background: linear-gradient(to right, #ffffff, #58a6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
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
        background-color: rgba(22, 27, 34, 0.9);
        backdrop-filter: blur(8px);
        color: #8b949e;
        text-align: center;
        padding: 12px;
        border-top: 1px solid #30363d;
        font-size: 14px;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_neon_style(lang["direction"], lang["align"])

# --- 6. واجهة البرنامج الرئيسية المترجمة ---
st.markdown(f"""
<div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
    <h1>{lang["title"]}</h1>
    <p style='font-size:16px; color:#8b949e; margin-top:-10px;'>{lang["subtitle"]}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

# --- التبويب الأول: تحويل الجداول لـ Excel ---
with tab1:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container excel-icon"><i class="fa-solid fa-file-excel"></i></div>
        <h3 style='margin:0; color:#ffffff;'>{lang["card1_title"]}</h3>
        <p style='font-size:14px; color:#8b949e; margin:5px 0;'>{lang["card1_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], key="pdf_main", accept_multiple_files=True)
    
    if pdf_files:
        for uploaded_pdf in pdf_files:
            st.write("")
            with st.container():
                st.info(f"{lang['status_preparing']}{uploaded_pdf.name}")
                if st.button(f"{lang['btn_convert']}{uploaded_pdf.name}"):
                    try:
                        with st.spinner(lang["status_loading"]):
                            dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                            
                            if dfs:
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    current_row = 0
                                    for df in dfs:
                                        df = df.fillna('').replace([float('inf'), float('-inf')], 0)
                                        df.to_excel(writer, index=False, startrow=current_row, sheet_name='Data')
                                        current_row += len(df) + 2
                                    
                                st.success(lang["success_convert"])
                                st.download_button(
                                    label=lang["download_excel"],
                                    data=output.getvalue(),
                                    file_name=f"Excel_{uploaded_pdf.name.replace('.pdf', '')}.xlsx",
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
        <h3 style='margin:0; color:#ffffff;'>{lang["card2_title"]}</h3>
        <p style='font-size:14px; color:#8b949e; margin:5px 0;'>{lang["card2_desc"]}</p>
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
                        st.markdown(f"<p style='font-size:14px; color:#8b949e; margin-bottom:5px;'>{lang['opt1']}</p>", unsafe_allow_html=True)
                        st_copy_to_clipboard(text=full_text, before_copy_label=lang["btn_copy"], after_copy_label=lang["copied"])
                        
                    with col2:
                        st.markdown(f"<p style='font-size:14px; color:#8b949e; margin-bottom:5px;'>{lang['opt2']}</p>", unsafe_allow_html=True)
                        st.download_button(
                            label=lang["download_txt"],
                            data=full_text,
                            file_name="extracted_text.txt"
                        )
                else:
                    st.warning(lang["warning_no_text"])
            except Exception as e:
                st.error(f"OCR Error: {e}")

# --- 7. مساحة إعلانية مخصصة ومتجاوبة في أسفل المحتوى ---
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

# التذييل الاحترافي الثابت في قاع الموقع
st.markdown(f"""
    <div class="footer">
        المحاسب الذكي Pro | <span style="color:#58a6ff;">{lang["motto"]}</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
