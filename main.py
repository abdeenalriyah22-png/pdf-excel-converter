import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="المحاسب الذكي Pro / Smart Accountant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. دمج كود جوجل أدسنس ---
components.html("""
<meta name="google-adsense-account" content="ca-pub-1091631464795781">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781"
     crossorigin="anonymous"></script>
""", height=0, width=0)

# --- 3. اختيار اللغة والمظهر ---
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
        ["ثلاثي الأبعاد الداكن (3D Dark)", "ثلاثي الأبعاد الفاتح (3D Light)"],
        index=0,
        key="theme_selector"
    )

# --- 4. قاموس الترجمة ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "المحاسب الذكي <span style='color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>Pro</span>",
        "subtitle": "نظام معالجة وتحويل المستندات والبيانات المحاسبية",
        "badge": "PDF / CSV ➔ Excel",
        "motto": "الفصل في الذمة.. الوصل في الأمانة",
        "tab1_title": "📊 تحويل PDF و CSV إلى جداول Excel",
        "tab2_title": "🔍 استخراج النصوص الذكي (OCR)",
        "card1_title": "مستخرج جداول البيانات",
        "card1_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF أو ملفات CSV إلى ملف إكسيل منسق تلقائياً",
        "card2_title": "قارئ النصوص والماسح الضوئي",
        "card2_desc": "استخراج النصوص العربية والإنجليزية والأوردو بدقة كاملة من المستندات المصورة والـ PDF",
        "uploader_pdf": "قم بسحب وإفلات ملفات الـ PDF أو CSV الخاصة بالجداول هنا",
        "uploader_ocr": "ارفع صورة الفاتورة/المستند (JPG, PNG) أو ملف PDF الممسوح",
        "btn_convert": "بدء التحويل والجداول: ",
        "btn_ocr": "🚀 إطلاق الذكاء الاصطناعي لقراءة النص",
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
        "copied": "✅ تم النسخ بنجاح!"
    },
    "English": {
        "direction": "ltr",
        "align": "left",
        "title": "Smart Accountant <span style='color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>Pro</span>",
        "subtitle": "Accounting Documents & Data Processing System",
        "badge": "PDF / CSV ➔ Excel",
        "motto": "Separation of liability... connection in trust",
        "tab1_title": "📊 Convert PDF & CSV to Excel",
        "tab2_title": "🔍 Smart Text Extraction (OCR)",
        "card1_title": "Data Table Extractor",
        "card1_desc": "Upload your files to automatically convert tables inside PDF or CSV into formatted Excel files",
        "card2_title": "Text Reader & Scanner",
        "card2_desc": "Extract Arabic, English, and Urdu text with full accuracy from scanned documents and images",
        "uploader_pdf": "Drag and drop your PDF or CSV table files here",
        "uploader_ocr": "Upload invoice/document image (JPG, PNG) or scanned PDF file",
        "btn_convert": "Start Converting: ",
        "btn_ocr": "🚀 Launch AI to Read Text",
        "status_preparing": "📁 Preparing file: ",
        "status_loading": "Processing and structuring data...",
        "status_ocr_loading": "Scanning document and interpreting text...",
        "success_convert": "🚀 Conversion completed successfully!",
        "warning_no_tables": "⚠️ No clear numerical tables detected in this file.",
        "warning_no_text": "Sorry, no readable text detected in this document.",
        "download_excel": "📥 Click here to download extracted Excel file",
        "download_txt": "📥 Download text as TXT file",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "opt1": "📋 Option 1:",
        "opt2": "📥 Option 2:",
        "btn_copy": "📋 Copy Full Text",
        "copied": "✅ Copied Successfully!"
    },
    "اردو": {
        "direction": "rtl",
        "align": "right",
        "title": "سمارٹ اکاؤنٹنٹ <span style='color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.5);'>Pro</span>",
        "subtitle": "دستاویزات اور محاسباتی ڈیٹا کی پروسیسنگ کا نظام",
        "badge": "PDF / CSV ➔ Excel",
        "motto": "الفصل في الذمة.. الوصل في الأمانة",
        "tab1_title": "📊 پی ڈی ایف اور سی ایس وی کو ایکسل میں تبدیل کریں",
        "tab2_title": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "card1_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "card1_desc": "پی ڈی ایف کے اندر موجود کسی بھی ٹیبل کو خودکار طور پر فارمیٹ شدہ ایکسل فائل میں تبدیل کریں",
        "card2_title": "ٹیکسٹ ریڈر اور اسكينر",
        "card2_desc": "اسکین شدہ دستاویزات اور تصاویر سے مکمل درستگی کے ساتھ متن نکالیں",
        "uploader_pdf": "اپنی پی ڈی ایف یا سی ایس وی ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر یا اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی شروع کریں: ",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "فائل کی تیاری: ",
        "status_loading": "ڈیٹا کو پروسیس کیا جا رہا ہے...",
        "status_ocr_loading": "دستاویز کو اسکین کیا جا رہا ہے...",
        "success_convert": "🚀 تبدیلی کامیابی سے مکمل ہو گئی!",
        "warning_no_tables": "⚠️ اس فائل میں کوئی واضح ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل متن نہیں ملا۔",
        "download_excel": "📥 ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں",
        "download_txt": "📥 متن کو TXT فائل کے طور پر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "opt1": "پہلا آپشن:",
        "opt2": "دوسرا آپشن:",
        "btn_copy": "📋 پورا متن کاپی کریں",
        "copied": "✅ کامیابی سے کاپی ہو گیا!"
    }
}

lang = translations[selected_lang]
is_dark = "Dark" in selected_theme or "الداكن" in selected_theme

# --- 5. ستايل الواجهة والمظهر الداكن المتطابق مع الصورة ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;900&display=swap');

html, body, [class*="st-emotion-cache"], p, div, h1, h2, h3, span, label, textarea {{
    font-family: 'Cairo', sans-serif !important;
    direction: {lang["direction"]} !important;
    text-align: {lang["align"]} !important;
}}

.stApp {{
    background-color: {"#0d1117" if is_dark else "#f4f6f9"} !important;
    color: {"#f0f6fc" if is_dark else "#1f2937"};
}}

header, [data-testid="stHeader"] {{
    visibility: hidden;
    display: none;
}}

[data-testid="stAppViewBlockContainer"] {{
    padding-top: 1.5rem !important;
    padding-bottom: 8rem !important;
    max-width: 1100px !important;
}}

/* === بطاقة الهيدر الرئيسية المتطابقة مع الصورة === */
.hero-card {{
    background: linear-gradient(145deg, #161b22 0%, #0d1117 100%);
    border: 1px solid #30363d;
    border-radius: 28px;
    padding: 30px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 0 2px rgba(56, 189, 248, 0.3);
    margin-bottom: 35px;
    position: relative;
    overflow: hidden;
}}

.hero-top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    flex-wrap: wrap;
    gap: 15px;
}}

.hero-badge {{
    background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%);
    color: #ffffff;
    font-weight: 800;
    font-size: 16px;
    padding: 8px 22px;
    border-radius: 50px;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
    letter-spacing: 0.5px;
}}

.hero-title-group {{
    text-align: {lang["align"]};
}}

.hero-title {{
    font-size: 38px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}}

.hero-subtitle {{
    font-size: 18px !important;
    color: #8b949e !important;
    font-weight: 700 !important;
    margin-top: 4px !important;
}}

/* البطاقة الداخلية لشعار الجملة النصية */
.motto-box {{
    background: linear-gradient(180deg, #092540 0%, #0284c7 60%, #0369a1 100%);
    border-radius: 20px;
    padding: 60px 20px;
    text-align: center;
    position: relative;
    box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.4), 0 10px 30px rgba(2, 132, 199, 0.25);
    border: 1px solid rgba(56, 189, 248, 0.3);
    overflow: hidden;
}}

.motto-box::after {{
    content: "";
    position: absolute;
    bottom: -20px;
    left: -10%;
    width: 120%;
    height: 60px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 50%;
    transform: rotate(-2deg);
}}

.motto-text {{
    font-size: 32px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 0 0 30px rgba(56, 189, 248, 0.6);
    position: relative;
    z-index: 2;
    margin: 0;
}}

/* === تنسيق التبويبات والأزرار === */
.stTabs [data-baseweb="tab-list"] {{
    gap: 12px;
    background: #161b22;
    padding: 10px;
    border-radius: 18px;
    border: 1px solid #30363d;
}}

.stTabs [data-baseweb="tab"] {{
    height: 50px;
    border-radius: 12px;
    color: #8b949e;
    font-size: 17px !important;
    font-weight: 800 !important;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 18px rgba(2, 132, 199, 0.3);
}}

[data-testid="stFileUploader"] {{
    background: #161b22 !important;
    border: 2px dashed #30363d !important;
    border-radius: 20px !important;
    padding: 30px !important;
}}

[data-testid="stFileUploader"]:hover {{
    border-color: #38bdf8 !important;
}}

.stButton>button {{
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 2rem !important;
    font-weight: 800 !important;
    font-size: 18px !important;
    width: 100%;
    box-shadow: 0 8px 20px rgba(2, 132, 199, 0.3);
}}

.stTextArea textarea {{
    background: #161b22 !important;
    color: #38bdf8 !important;
    border: 1px solid #30363d !important;
    border-radius: 16px !important;
    font-size: 17px !important;
    font-weight: 700 !important;
}}

.footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
    text-align: center;
    padding: 14px;
    font-size: 16px;
    font-weight: 800;
    z-index: 999;
}}
</style>
""", unsafe_allow_html=True)

# --- 6. عرض الهيدر المطابق للصورة ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-top-bar" style="direction: ltr;">
        <div class="hero-badge">{lang["badge"]}</div>
        <div class="hero-title-group" style="direction: {lang["direction"]};">
            <h1 class="hero-title">{lang["title"]}</h1>
            <div class="hero-subtitle">{lang["subtitle"]}</div>
        </div>
    </div>
    <div class="motto-box">
        <h2 class="motto-text">{lang["motto"]}</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 7. التبويبات والوظائف ---
tab1, tab2 = st.tabs([lang["tab1_title"], lang["tab2_title"]])

# --- التبويب الأول: تحويل الجداول لـ Excel ---
with tab1:
    st.markdown(f"""
    <div style="background:#161b22; border:1px solid #30363d; border-radius:20px; padding:25px; margin-bottom:25px; text-align:center;">
        <h3 style="color:#ffffff; margin:0 0 8px 0; font-weight:900;">{lang["card1_title"]}</h3>
        <p style="color:#8b949e; margin:0; font-weight:700;">{lang["card1_desc"]}</p>
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
    <div style="background:#161b22; border:1px solid #30363d; border-radius:20px; padding:25px; margin-bottom:25px; text-align:center;">
        <h3 style="color:#ffffff; margin:0 0 8px 0; font-weight:900;">{lang["card2_title"]}</h3>
        <p style="color:#8b949e; margin:0; font-weight:700;">{lang["card2_desc"]}</p>
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
                        st.markdown(f"<p style='font-size:15px; font-weight:bold; margin-bottom:5px;'>{lang['opt1']}</p>", unsafe_allow_html=True)
                        st_copy_to_clipboard(text=full_text, before_copy_label=lang["btn_copy"], after_copy_label=lang["copied"])
                        
                    with col2:
                        st.markdown(f"<p style='font-size:15px; font-weight:bold; margin-bottom:5px;'>{lang['opt2']}</p>", unsafe_allow_html=True)
                        st.download_button(
                            label=lang["download_txt"],
                            data=full_text,
                            file_name="extracted_text.txt"
                        )
                else:
                    st.warning(lang["warning_no_text"])
            except Exception as e:
                st.error(f"OCR Error: {e}")

# --- 8. الإعلانات والتذييل ---
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
