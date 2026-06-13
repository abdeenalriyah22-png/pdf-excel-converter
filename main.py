import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# --- 1. إعدادات الصفحة الأساسية الفخمة ---
st.set_page_config(
    page_title="المحاسب الذكي Pro / Smart Accountant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. دمج كود جوجل أدسنس والتحقق في الخلفية بشكل آمن ---
components.html("""
<meta name="google-adsense-account" content="ca-pub-1091631464795781">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781"
     crossorigin="anonymous"></script>
""", height=0, width=0)

# --- 3. قاموس الترجمة المصلح والمستقر بالكامل لتفادي KeyError ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe;'>Pro</span>",
        "subtitle": "المنصة السحابية المتكاملة لإدارة ومعالجة ملفات وجداول PDF ذكياً",
        "menu_title": "🛠️ تفعيل الأدوات الذكية:",
        "theme_title": "🌓 مظهر الموقع / Theme Mode :",
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
        "direction": "ltr",
        "align": "left",
        "title": "📊 Smart Accountant <span style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe;'>Pro</span>",
        "subtitle": "Integrated cloud platform for smart PDF management, processing and table extraction",
        "menu_title": "🛠️ Activate Smart Tools:",
        "theme_title": "🌓 Theme Mode / مظهر الموقع :",
        "tool_excel": "📊 Convert PDF to Excel Tables",
        "tool_ocr": "🔍 Smart Text Extraction (OCR)",
        "tool_merge": "📂 Merge Multiple PDF Files",
        "tool_delete": "✂️ Delete Pages from PDF",
        "tool_reorder": "🔀 Reorder PDF Pages",
        "tool_sign": "✍️ Digital Signature on Document",
        "uploader_pdf": "Drag and drop your PDF table files here",
        "uploader_ocr": "Upload invoice/document image (JPG, PNG) or scanned PDF file",
        "btn_convert": "Start Converting: ",
        "btn_ocr": "🚀 Launch AI to Read Text",
        "status_loading": "Processing and structuring data...",
        "success_convert": "🚀 Process completed successfully with highest accuracy!",
        "warning_no_tables": "⚠️ No clear numerical tables detected.",
        "warning_no_text": "Sorry, no readable text detected in this document.",
        "download_excel": "📥 Click here to download Excel file",
        "download_txt": "📥 Download text as TXT file",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "motto": "Separation of liability... connection in trust"
    },
    "اردو": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='color:#00f2fe; text-shadow: 0 0 10px #00f2fe;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا، پی ڈی ایف مینجمنٹ اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "menu_title": "🛠️ مطلوبہ ٹول منتخب کریں:",
        "theme_title": "🌓 سائٹ کا انداز / Theme Mode :",
        "tool_excel": "📊 پی ڈی ایف کو ایکسل میں تبدیل کریں",
        "tool_ocr": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "tool_merge": "📂 متعدد پی ڈی ایف فائلیں ضم کریں",
        "tool_delete": "✂️ پی ڈی ایف سے صفحات حذف کریں",
        "tool_reorder": "🔀 پی ڈی ایف صفحات کو دوبارہ ترتیب دیں",
        "tool_sign": "✍️ دستاویز پر ڈیجیٹل دستخط کریں",
        "uploader_pdf": "اپنی پی ڈی ایف ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر (JPG, PNG) یا اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی شروع کریں: ",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_loading": "ڈیٹا پر کارروائی کی جا رہی ہے...",
        "success_convert": "🚀 عمل اعلیٰ ترین درستگی کے ساتھ کامیابی سے مکمل ہو گیا!",
        "warning_no_tables": "⚠️ کوئی واضح ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل متن نہیں ملا۔",
        "download_excel": "📥 ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں",
        "download_txt": "📥 متن کو TXT فائل کے طور پر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

# --- 4. بناء لوحة التحكم الجانبية الثابتة والمعدلة الهيكلية ---
with st.sidebar:
    # أ. رفع اختيار اللغة في أعلى القائمة الجانبية تماماً قبل كل شيء
    selected_lang = st.selectbox(
        "🌐 Language / اللغة / زبان",
        ["العربية", "English", "اردو"],
        index=0,
        key="language_selector"
    )

# جلب قاموس اللغة بناء على الاختيار فوراً لمنع KeyError
lang = translations.get(selected_lang, translations["العربية"])

with st.sidebar:
    st.markdown("<hr style='border-color: rgba(0, 242, 254, 0.2); margin: 10px 0;'>", unsafe_allow_html=True)
    
    # ب. إضافة ميزة اختيار المظهر (داكن / فاتح) بعد اللغة مباشرة
    theme_choice = st.radio(
        lang["theme_title"],
        ["Dark Mode / داكن 🌑", "Light Mode / فاتح ☀️"],
        index=0,
        key="theme_selector"
    )
    
    st.markdown("<hr style='border-color: rgba(0, 242, 254, 0.2); margin: 10px 0;'>", unsafe_allow_html=True)
    
    # ج. أدوات الاختيار الأساسية
    tool_options = [lang["tool_excel"], lang["tool_ocr"], lang["tool_merge"], lang["tool_delete"], lang["tool_reorder"], lang["tool_sign"]]
    current_tool = st.radio(lang["menu_title"], tool_options)

# تتبع حالة الثيم المختار لبناء التنسيق الاحترافي المناسب ديناميكياً
is_dark = "Dark" in theme_choice

# تحديد الألوان بناء على اختيار المستخدم للمظهر
bg_app = "radial-gradient(circle at 50% 50%, #0b0f19 0%, #04060a 100%)" if is_dark else "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)"
text_main = "#f8fafc" if is_dark else "#0f172a"
bg_sidebar = "rgba(10, 15, 26, 0.98)" if is_dark else "#ffffff"
bg_card = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)" if is_dark else "linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%)"
border_card = "rgba(0, 242, 254, 0.2)" if is_dark else "rgba(79, 172, 254, 0.3)"
bg_input = "#0f172a" if is_dark else "#ffffff"
border_input = "#334155" if is_dark else "#cbd5e1"

# --- 5. نظام الـ CSS المتطور للنيون والتوهج مفصول كلياً لحل مشكلة التداخل والتصغير ---
css_code = f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;600;700;900&display=swap');

/* تطبيق الخطوط على التطبيق ككل */
html, body, [class*="st-emotion-cache"], p, div, h1, h2, h3, span, label, textarea, input {{
    font-family: 'Cairo', sans-serif !important;
}}

/* جسم التطبيق الأساسي المتجاوب */
.stApp {{
    background: {bg_app} !important;
    color: {text_main} !important;
}}

/* إخفاء الهيدر الافتراضي المزعج لشكل أكثر احترافية */
[data-testid="stHeader"] {{
    visibility: hidden;
    display: none;
}

/* تنسيق لوحة التحكم الجانبية */
[data-testid="stSidebar"] {{
    background-color: {bg_sidebar} !important;
    border-right: {"2px solid #1e293b" if is_dark else "2px solid #e2e8f0"} !important;
}}

/* حل مشكلة التصغير العبقري: منع انهيار القائمة الجانبية وجعلها مرنة ومستقرة دائماً */
[data-testid="stSidebarNav"] {{
    background-color: transparent !important;
}}
[data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] .stSelectbox {{
    padding: 5px 10px !important;
}}

/* تنسيق البطاقات الاحترافية المضيئة والمتحركة */
.custom-card {{
    background: {bg_card} !important;
    border: 1px solid {border_card} !important;
    border-radius: 20px !important;
    padding: 30px !important;
    text-align: center !important;
    margin-bottom: 25px !important;
    box-shadow: {"0 10px 25px rgba(0,0,0,0.3)" if is_dark else "0 10px 25px rgba(0,0,0,0.05)"} !important;
    transition: all 0.4s ease-in-out !important;
}}
.custom-card:hover {{
    transform: translateY(-4px) !important;
    border-color: #00f2fe !important;
    box-shadow: 0 15px 35px rgba(0, 242, 254, 0.25) !important;
}}

.icon-container {{
    font-size: 55px !important;
    margin-bottom: 12px !important;
    display: inline-block !important;
    animation: pulse 2.5s infinite !important;
}}
@keyframes pulse {{
    0% {{ transform: scale(1); opacity: 0.9; }}
    50% {{ transform: scale(1.04); opacity: 1; }}
    100% {{ transform: scale(1); opacity: 0.9; }}
}}

.excel-icon {{ color: #00f2fe !important; text-shadow: 0 0 25px #00f2fe !important; }}
.ocr-icon {{ color: #4facfe !important; text-shadow: 0 0 25px #4facfe !important; }}
.pdf-tool-icon {{ color: #ff5e62 !important; text-shadow: 0 0 25px #ff5e62 !important; }}

h1 {{
    font-weight: 900 !important;
    background: linear-gradient(to right, {"#ffffff" if is_dark else "#0f172a"}, #00f2fe, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* الأزرار الاحترافية بنظام نيون فخم */
.stButton>button {{
    background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 900 !important;
    font-size: 16px !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3) !important;
    transition: all 0.3s ease-in-out !important;
}}
.stButton>button:hover {{
    box-shadow: 0 0 25px #00f2fe !important;
    color: #ffffff !important;
}}

[data-testid="stDownloadButton"] button {{
    background: linear-gradient(90deg, #2ea043 0%, #238636 100%) !important;
    color: white !important;
    font-weight: 700 !important;
}}

/* تجميل حقول السحب والإفلات للملفات لتناسب السيم المظلم/الفاتح */
[data-testid="stFileUploader"] {{
    background: {bg_input} !important;
    border: 2px dashed rgba(0, 242, 254, 0.4) !important;
    border-radius: 14px !important;
}}

/* صناديق الخيارات والقوائم المنسدلة */
div[data-baseweb="select"] {{
    background: {bg_input} !important;
    border: 1px solid {border_input} !important;
    border-radius: 10px !important;
}}
div[data-baseweb="select"] * {{
    color: {text_main} !important;
}}

/* مدخلات النصوص والمساحات الكتابية */
.stTextArea textarea, .stTextInput input, .stNumberInput input {{
    background-color: {bg_input} !important;
    color: {text_main} !important;
    border: 1px solid {border_input} !important;
    border-radius: 10px !important;
}}

/* التذييل الثابت والذكي للموقع بشعارك المحدث */
.footer {{
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: {"rgba(15, 23, 42, 0.96)" if is_dark else "rgba(241, 245, 249, 0.96)"};
    backdrop-filter: blur(10px);
    color: {"#94a3b8" if is_dark else "#475569"};
    text-align: center;
    padding: 10px;
    border-top: 1px solid {"#1e293b" if is_dark else "#e2e8f0"};
    font-size: 13px;
    z-index: 999;
}}
</style>
"""

# حقن التنسيق لضمان ثبات الواجهة برمجياً وبشكل تجاوبي كامل
components.html(css_code, height=0, width=0)

# تفعيل الإتجاهات للنصوص الأساسية بالموقع حسب اختيار اللغة المفعّل
st.markdown(f"""
<style>
.stApp, p, div, h1, h2, h3, span, label, textarea, input {{
    direction: {lang["direction"]} !important;
    text-align: {lang["align"]} !important;
}}
</style>
""", unsafe_allow_html=True)

# --- 6. عنوان التطبيق الرئيسي المتوهج ---
st.markdown(f"""
<div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
    <h1>{lang["title"]}</h1>
    <p style='font-size:15px; color:{"#94a3b8" if is_dark else "#475569"}; margin-top:-10px;'>{lang["subtitle"]}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================================
# 1. أداة تحويل PDF إلى جداول إكسيل
# =========================================================================
if current_tool == lang["tool_excel"]:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container excel-icon"><i class="fa-solid fa-file-excel"></i></div>
        <h3 style='margin:0; color:{"#fff" if is_dark else "#0f172a"};'>تحويل الجداول الرقمية إلى Excel</h3>
        <p style='font-size:14px; color:{"#94a3b8" if is_dark else "#475569"}; margin:5px 0;'>ارفع الكشوفات والتقارير المالية لتحويلها تلقائياً إلى ملفات إكسيل منسقة بدقة</p>
    </div>
    """, unsafe_allow_html=True)
    
    pdf_files = st.file_uploader(lang["uploader_pdf"], type=["pdf"], key="pdf_main", accept_multiple_files=True)
    if pdf_files:
        for uploaded_pdf in pdf_files:
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
                            st.download_button(label=lang["download_excel"], data=output.getvalue(), file_name=f"Excel_{uploaded_pdf.name.replace('.pdf', '')}.xlsx", mime="application/vnd.ms-excel")
                        else:
                            st.warning(lang["warning_no_tables"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# =========================================================================
# 2. أداة استخراج النصوص الذكي (OCR)
# =========================================================================
elif current_tool == lang["tool_ocr"]:
    st.markdown(f"""
    <div class="custom-card">
        <div class="icon-container ocr-icon"><i class="fa-solid fa-eye"></i></div>
        <h3 style='margin:0; color:{"#fff" if is_dark else "#0f172a"};'>قارئ النصوص والماسح الضوئي الذكي</h3>
        <p style='font-size:14px; color:{"#94a3b8" if is_dark else "#475569"}; margin:5px 0;'>استخراج فوري للبيانات من الكشوفات المصورة التي تفتقر لخطوط الشبكة الواضحة</p>
    </div>
    """, unsafe_allow_html=True)
    
    ocr_file = st.file_uploader(lang["uploader_ocr"], type=["jpg", "png", "jpeg", "pdf"], key="ocr_main")
    if ocr_file:
        if st.button(lang["btn_ocr"]):
            full_text = ""
            try:
                with st.spinner(lang["status_loading"]):
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
                    st.text_area("", value=full_text, height=250)
                    st.download_button(label=lang["download_txt"], data=full_text, file_name="extracted_text.txt")
                else:
                    st.warning(lang["warning_no_text"])
            except Exception as e:
                st.error(f"OCR Error: {e}")

# =========================================================================
# 3. أداة دمج ملفات PDF
# =========================================================================
elif current_tool == lang["tool_merge"]:
    st.markdown(f"""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-file-medical"></i></div>
    <h3 style='margin:0; color:{"#fff" if is_dark else "#0f172a"};'>📂 دمج ملفات PDF متعددة</h3>
    <p style='font-size:14px; color:{"#94a3b8" if is_dark else "#475569"}; margin:5px 0;'>تجميع الكشوفات الدورية والسجلات المشتتة في ملف مستند واحد متصل ومتسلسل</p></div>
    """, unsafe_allow_html=True)
    
    merge_files = st.file_uploader("اختر ملفات PDF لدمجها معاً:", type=["pdf"], accept_multiple_files=True, key="merge_up")
    if merge_files and len(merge_files) >= 2:
        if st.button("🚀 ابدأ دمج المستندات الآن"):
            try:
                with st.spinner("جاري دمج وترتيب الصفحات..."):
                    main_doc = fitz.open()
                    for f in merge_files:
                        sub_doc = fitz.open(stream=f.read(), filetype="pdf")
                        main_doc.insert_pdf(sub_doc)
                    output_bytes = main_doc.write()
                    st.success(lang["success_convert"])
                    st.download_button("📥 تحميل ملف PDF المدمج الجديد", data=output_bytes, file_name="Merged_Document.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الدمج: {e}")

# =========================================================================
# 4. أداة حذف صفحات من ملف PDF
# =========================================================================
elif current_tool == lang["tool_delete"]:
    st.markdown(f"""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-file-circle-minus"></i></div>
    <h3 style='margin:0; color:{"#fff" if is_dark else "#0f172a"};'>✂️ حذف صفحات معينة من المستند</h3>
    <p style='font-size:14px; color:{"#94a3b8" if is_dark else "#475569"}; margin:5px 0;'>تنقية السجلات والملفات من الصفحات البيضاء أو الملحقات الزائدة</p></div>
    """, unsafe_allow_html=True)
    
    del_file = st.file_uploader("ارفع ملف الـ PDF المراد تعديله:", type=["pdf"], key="del_up")
    if del_file:
        pages_to_del = st.text_input("أدخل أرقام الصفحات المراد حذفها مفصولة بفاصلة (مثال: 2, 5):")
        if st.button("❌ احذف الصفحات المحددة"):
            try:
                with st.spinner("جاري تنقيح الملف وفصل الصفحات..."):
                    doc = fitz.open(stream=del_file.read(), filetype="pdf")
                    indices = sorted([int(p.strip()) - 1 for p in pages_to_del.split(",") if p.strip().isdigit()], reverse=True)
                    for idx in indices:
                        if 0 <= idx < len(doc):
                            doc.delete_page(idx)
                    output_bytes = doc.write()
                    st.success(lang["success_convert"])
                    st.download_button("📥 تحميل المستند المنقح", data=output_bytes, file_name="Edited_Document.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# =========================================================================
# 5. أداة إعادة ترتيب صفحات PDF
# =========================================================================
elif current_tool == lang["tool_reorder"]:
    st.markdown(f"""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-file-signature"></i></div>
    <h3 style='margin:0; color:{"#fff" if is_dark else "#0f172a"};'>🔀 إعادة ترتيب وتنظيم الصفحات</h3>
    <p style='font-size:14px; color:{"#94a3b8" if is_dark else "#475569"}; margin:5px 0;'>أعد صياغة هيكلية الصفحات بالترتيب المتوافق مع متطلباتك</p></div>
    """, unsafe_allow_html=True)
    
    reorder_file = st.file_uploader("ارفع الملف لإعادة ترتيبه:", type=["pdf"], key="reorder_up")
    if reorder_file:
        doc = fitz.open(stream=reorder_file.read(), filetype="pdf")
        st.info(f"💡 هذا المستند يحتوي على إجمالي: ({len(doc)}) صفحات.")
        order_input = st.text_input("اكتب الترتيب الجديد للصفحات مفصولة بفاصلة (مثال: 3, 1, 2):")
        if st.button("⚙️ تطبيق الهيكلة الجديدة"):
            try:
                with st.spinner("جاري تبديل مواضع الصفحات..."):
                    new_order = [int(x.strip()) - 1 for x in order_input.split(",") if x.strip().isdigit()]
                    new_doc = fitz.open()
                    for idx in new_order:
                        if 0 <= idx < len(doc):
                            new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
                    output_bytes = new_doc.write()
                    st.success(lang["success_convert"])
                    st.download_button("📥 تحميل الملف بالترتيب الجديد", data=output_bytes, file_name="Reordered_Document.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")

# =========================================================================
# 6. أداة التوقيع الإلكتروني على المستند
# =========================================================================
elif current_tool == lang["tool_sign"]:
    st.markdown(f"""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-pen-nib"></i></div>
    <h3 style='margin:0; color:{"#fff" if is_dark else "#0f172a"};'>✍️ التوقيع الإلكتروني الذكي على المستندات</h3>
    <p style='font-size:14px; color:{"#94a3b8" if is_dark else "#475569"}; margin:5px 0;'>إسقاط وتثبيت الأختام والتواقيع بصورة رسمية وغير قابلة للتعديل داخل التقارير</p></div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        main_pdf = st.file_uploader("1. ارفع ملف المستند أو الفاتورة (PDF):", type=["pdf"], key="sign_pdf")
    with col_f2:
        sign_img = st.file_uploader("2. ارفع صورة توقيعك أو الختم (PNG شفافة):", type=["png", "jpg", "jpeg"], key="sign_img")
        
    if main_pdf and sign_img:
        st.markdown("---")
        st.markdown("#### 🎯 أبعاد وإحداثيات إسقاط الختم:")
        doc = fitz.open(stream=main_pdf.read(), filetype="pdf")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            target_page = st.number_input("رقم الصفحة المستهدفة للتوقيع:", min_value=1, max_value=len(doc), value=1)
        with c2:
            sig_width = st.slider("عرض التوقيع (الحجم الحجمي):", min_value=50, max_value=300, value=120, step=10)
        with c3:
            x_pos = st.slider("الموضع الأفقي (اليمين واليسار):", min_value=0, max_value=600, value=400, step=10)
        with c4:
            y_pos = st.slider("الموضع العمودي (الأعلى والأسفل):", min_value=0, max_value=800, value=700, step=10)
            
        if st.button("✍️ دمج وختم التوقيع داخل الـ PDF"):
            try:
           # --- 4. بناء لوحة التحكم الجانبية الثابتة والمُعاد ترتيبها ---
with st.sidebar:
    # 1. اختيار اللغة في الأعلى
    selected_lang = st.selectbox(
        "🌐 Language / اللغة / زبان",
        ["العربية", "English", "اردو"],
        index=0,
        key="language_selector"
    )
    
    # 2. اختيار المظهر (تم إضافته هنا)
    st.markdown("<hr style='border-color:#1e293b;'>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "🌓 Theme Mode / مظهر الموقع",
        ["Dark Mode 🌑", "Light Mode ☀️"],
        index=0
    )
    
    # 3. الأدوات
    st.markdown("<hr style='border-color:#1e293b;'>", unsafe_allow_html=True)
    lang = translations[selected_lang]
    tool_options = [lang["tool_excel"], lang["tool_ocr"], lang["tool_merge"], lang["tool_delete"], lang["tool_reorder"], lang["tool_sign"]]
    current_tool = st.radio(lang["menu_title"], tool_options)

# ملاحظة: تأكد عند استخدام f-string في CSS داخل الكود أن تستخدم {{ لتجنب أخطاء SyntaxError
                    
                    output_bytes = doc.write()
                    st.success("✍️ تم دمج وختم التوقيع الإلكتروني بنجاح!")
                    st.download_button("📥 تحميل المستند الموقع والمختوم جاهزاً", data=output_bytes, file_name="Signed_Document.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"حدث خطأ أثناء التوقيع: {e}")

# --- 7. مساحة إعلانية متجاوبة آمنة ومغلقة بالكامل في الأسفل ---
st.markdown("<br><br>", unsafe_allow_html=True)
ads_code = """
<div style="text-align: center; width: 100%;">
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

# التذييل الاحترافي المتوهج الثابت في قاع الموقع بالشعار المحدث
st.markdown(f"""
    <div class="footer">
        المحاسب الذكي Pro | <span style="color:#00f2fe; text-shadow: 0 0 5px #00f2fe;">{lang["motto"]}</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
