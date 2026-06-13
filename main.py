import streamlit as st
import streamlit.components.v1 as components
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import fitz  # PyMuPDF المعتمدة

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="المحاسب الذكي Pro / Smart Accountant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. دمج كود جوجل أدسنس والتحقق في الخلفية ---
components.html("""
<meta name="google-adsense-account" content="ca-pub-1091631464795781">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1091631464795781"
     crossorigin="anonymous"></script>
""", height=0, width=0)

# --- 3. إعدادات القائمة الجانبية (اختيار اللغة والوضع المظهر) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#1f6feb; font-weight:bold; margin-bottom:10px;'>⚙️ لوحة التحكم</h2>", unsafe_allow_html=True)
    
    # خيار التبديل بين الوضع الفاتح والداكن
    theme_choice = st.radio(
        "🌓 مظهر الموقع / Theme Mode:",
        ["داكن / Dark Mode", "فاتح / Light Mode"],
        index=0,
        key="theme_selector"
    )
    
    st.markdown("---")
    
    # اختيار اللغة
    selected_lang = st.selectbox(
        "🌐 Language / اللغة / زبان",
        ["العربية", "English", "اردو"],
        index=0,
        key="language_selector"
    )

# --- 4. قاموس الترجمة للغات الثلاث ---
translations = {
    "العربية": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 المحاسب الذكي <span style='font-size:22px; color:#1f6feb; font-weight:normal;'>Pro</span>",
        "subtitle": "المنصة السحابية المتكاملة لإدارة ومعالجة ملفات وجداول PDF ذكياً",
        "menu_title": "🛠️ اختر الأداة المطلوبة:",
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
        "status_preparing": "📁 ملف قيد التحضير: ",
        "status_loading": "جاري تفكيك البيانات وهيكلتها...",
        "success_convert": "🚀 اكتملت العملية بنجاح وبأعلى دقة!",
        "warning_no_tables": "⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.",
        "warning_no_text": "نعتذر، لم نكتشف حروفاً أو نصوصاً مقروءة في هذا المستند.",
        "download_excel": "📥 اضغط هنا لتحميل ملف Excel المستخرج",
        "download_txt": "📥 تحميل النص كملف TXT",
        "ocr_result_header": "#### ✅ النصوص التي تم العثور عليها ومسحها:",
        "btn_copy": "📋 نسخ النص بالكامل",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    },
    "English": {
        "direction": "ltr",
        "align": "left",
        "title": "📊 Smart Accountant <span style='font-size:22px; color:#1f6feb; font-weight:normal;'>Pro</span>",
        "subtitle": "Integrated cloud platform for smart PDF management, processing and table extraction",
        "menu_title": "🛠️ Select Required Tool:",
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
        "status_preparing": "📁 File preparing: ",
        "status_loading": "Processing and structuring data...",
        "success_convert": "🚀 Process completed successfully with highest accuracy!",
        "warning_no_tables": "⚠️ No clear numerical tables detected.",
        "warning_no_text": "Sorry, no readable text detected in this document.",
        "download_excel": "📥 Click here to download Excel file",
        "download_txt": "📥 Download text as TXT file",
        "ocr_result_header": "#### ✅ Extracted Text:",
        "btn_copy": "📋 Copy Full Text",
        "motto": "Separation of liability... connection in trust"
    },
    "اردو": {
        "direction": "rtl",
        "align": "right",
        "title": "📊 سمارٹ اکاؤنٹنٹ <span style='font-size:22px; color:#1f6feb; font-weight:normal;'>Pro</span>",
        "subtitle": "سمارٹ ڈیٹا، پی ڈی ایف مینجمنٹ اور ٹیبل پروسیسنگ کے لیے جدید کلاؤڈ سسٹم",
        "menu_title": "🛠️ مطلوبہ ٹول منتخب کریں:",
        "tool_excel": "📊 پی ڈی ایف کو ایکسل میں تبدیل کریں",
        "tool_ocr": "🔍 سمارٹ ٹیکسٹ نکالنا (OCR)",
        "tool_merge": "📂 متعدد پی ڈی ایف فائلیں ضم کریں",
        "tool_delete": "✂️ پی ڈی ایف سے صفحات حذف کریں",
        "tool_reorder": "🔀 پی ڈی ایف صفحات کو دوبارہ ترتیب دیں",
        "tool_sign": "✍️ دستاویز پر ڈیجیٹل دستخط کریں",
        "uploader_pdf": "اپنی پی ڈی ایف ٹیبل فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "uploader_ocr": "انوائس/دستاویز کی تصویر (JPG, PNG) أو اسکین شدہ پی ڈی ایف فائل اپ لوڈ کریں",
        "btn_convert": "تبدیلی شروع کریں: ",
        "btn_ocr": "🚀 ٹیکسٹ پڑھنے کے لیے AI لانچ کریں",
        "status_preparing": "📁 فائل کی تیاری: ",
        "status_loading": "ڈیٹا پر کارروائی کی جا رہی ہے...",
        "success_convert": "🚀 عمل اعلیٰ ترین درستگی کے ساتھ کامیابی سے مکمل ہو گیا!",
        "warning_no_tables": "⚠️ کوئی واضح ٹیبل نہیں ملا۔",
        "warning_no_text": "معذرت، اس دستاویز میں کوئی پڑھنے کے قابل متن نہیں ملا۔",
        "download_excel": "📥 ایکسل فائل ڈاؤن لوڈ کرنے کے لیے یہاں کلک کریں",
        "download_txt": "📥 متن کو TXT فائل کے طور پر ڈاؤن لوڈ کریں",
        "ocr_result_header": "#### ✅ نکالا گیا متن:",
        "btn_copy": "📋 پورا متن کاپی کریں",
        "motto": "الفصل في الذمة.. الوصل في الأمانة"
    }
}

lang = translations[selected_lang]

# --- 5. شريط التنقل الجانبي بين الأدوات المتعددة ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    current_tool = st.radio(
        lang["menu_title"],
        [lang["tool_excel"], lang["tool_ocr"], lang["tool_merge"], lang["tool_delete"], lang["tool_reorder"], lang["tool_sign"]]
    )

# --- 6. تطبيق ديناميكي لخصائص المظهر الفاتح والداكن وحل عيوب التباين ---
def apply_custom_theme(theme_mode, direction, align):
    # إعداد متغيرات الألوان بناءً على اختيار المستخدم
    if theme_mode == "فاتح / Light Mode":
        bg_style = "background: #f8f9fa !important; color: #212529 !important;"
        card_bg = "linear-gradient(145deg, #ffffff 0%, #f1f3f5 100%)"
        card_border = "#dee2e6"
        text_color = "#212529 !important;"
        sub_text_color = "#495057"
        sidebar_bg = "#f1f3f5 !important;"
        input_bg = "#ffffff !important;"
        input_text = "#212529 !important;"
        input_border = "#ced4da !important;"
    else:
        bg_style = "background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important; color: #e6edf3 !important;"
        card_bg = "linear-gradient(145deg, #161b22 0%, #0f1319 100%)"
        card_border = "#30363d"
        text_color = "#ffffff !important;"
        sub_text_color = "#8b949e"
        sidebar_bg = "#0d1117 !important;"
        input_bg = "#0d1117 !important;"
        input_text = "#e6edf3 !important;"
        input_border = "#30363d !important;"

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

    /* تخصيص القائمة الجانبية بالكامل وضمان تباينها وعلاج النصوص فيها */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg}
        border-right: 1px solid #30363d !important;
    }}

    [data-testid="stSidebar"] * {{
        direction: {direction} !important;
        text-align: {align} !important;
        color: {text_color}
    }}

    header, [data-testid="stHeader"] {{
        visibility: hidden;
        display: none;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        padding: 1rem 5rem 8rem 5rem;
    }}

    /* === حل مشكلة القائمة المنسدلة للغة والنصوص بداخلها واختيارات السيلكت بوكس === */
    [data-testid="stSelectbox"] label p, [data-testid="stRadio"] label p {{
        font-size: 16px !important;
        font-weight: bold !important;
        color: #1f6feb !important;
    }}
    
    div[data-baseweb="select"] {{
        background-color: {input_bg}
        border: 1px solid {input_border}
        border-radius: 12px !important;
    }}
    
    div[data-baseweb="select"] div {{
        color: {text_color}
        font-weight: bold !important;
    }}

    div[data-baseweb="popover"] {{
        background-color: #161b22 !important;
    }}
    
    /* معالجة عناصر قائمة خيارات اللغة لمنع شفافيتها واختفائها */
    li[role="option"], li[role="option"] span, div[role="listbox"] div, div[role="listbox"] span, ul[role="listbox"] li {{
        color: #ffffff !important;
        font-weight: 600 !important;
        background-color: #161b22 !important;
    }}
    
    div[data-baseweb="popover"] li:hover, li[role="option"]:hover {{
        background-color: #1f6feb !important;
        color: #ffffff !important;
    }}

    /* تحسين خيارات واجهة أزرار الرفع */
    [data-testid="stFileUploader"] button span span {{
        display: none !important;
    }}
    [data-testid="stFileUploader"] button span::after {{
        content: "Upload" !important;
        color: white !important;
    }}

    .custom-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
    }}

    .icon-container {{
        font-size: 55px;
        margin-bottom: 15px;
        display: inline-block;
    }}
    
    .excel-icon {{ color: #2ea043; text-shadow: 0 0 20px rgba(46, 160, 67, 0.4); }}
    .ocr-icon {{ color: #58a6ff; text-shadow: 0 0 20px rgba(88, 166, 255, 0.4); }}
    .pdf-tool-icon {{ color: #ff7b72; text-shadow: 0 0 20px rgba(255, 123, 114, 0.4); }}

    h1, h3 {{
        color: {text_color}
    }}

    /* الأزرار الرئيسية المتوافقة */
    .stButton>button {{
        background: linear-gradient(135deg, #1f6feb 0%, #104ba3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 2rem !important;
        font-weight: bold !important;
        font-size: 16px !important;
        width: 100%;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.2);
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(31, 111, 235, 0.5);
    }}

    [data-testid="stDownloadButton"] button {{
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        width: 100%;
    }}

    .stTextArea textarea, .stTextInput input, .stNumberInput input {{
        background-color: {input_bg}
        color: {input_text}
        border: 1px solid {input_border}
        border-radius: 12px !important;
    }}

    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: {sidebar_bg};
        backdrop-filter: blur(8px);
        color: {sub_text_color};
        text-align: center;
        padding: 12px;
        border-top: 1px solid {card_border};
        font-size: 14px;
        z-index: 999;
    }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme(theme_choice, lang["direction"], lang["align"])

# --- 7. واجهة البرنامج الرئيسية المترجمة ---
st.markdown(f"""
<div style='text-align: {lang["align"]}; margin-bottom: 10px;'>
    <h1>{lang["title"]}</h1>
    <p style='font-size:16px; color:#8b949e; margin-top:-10px;'>{lang["subtitle"]}</p>
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
        <h3 style='margin:0;'>تحويل الجداول الرقمية إلى Excel</h3>
        <p style='font-size:14px; margin:5px 0;'>ارفع الكشوفات والتقارير المالية لتحويلها تلقائياً إلى جداول بيانات ميكروسوفت إكسيل منسقة</p>
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
        <h3 style='margin:0;'>قارئ النصوص والماسح الضوئي الذكي</h3>
        <p style='font-size:14px; margin:5px 0;'>استخرج الحروف والكلمات بدقة من الفواتير والملفات المصورة والممسوحة ضوئياً</p>
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
    st.markdown("""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-file-medical"></i></div>
    <h3 style='margin:0;'>📂 دمج ملفات PDF متعددة</h3>
    <p style='font-size:14px; margin:5px 0;'>قم برفع كشوفات ومستندات متعددة ليتم تجميعها فوراً في ملف PDF واحد متسلسل</p></div>
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
    st.markdown("""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-file-circle-minus"></i></div>
    <h3 style='margin:0;'>✂️ حذف صفحات معينة من المستند</h3>
    <p style='font-size:14px; margin:5px 0;'>تخلص من الصفحات الفارغة أو الزائدة داخل التقارير عبر تحديد أرقامها بسهولة</p></div>
    """, unsafe_allow_html=True)
    
    del_file = st.file_uploader("ارفع ملف الـ PDF المراد تعديله:", type=["pdf"], key="del_up")
    if del_file:
        pages_to_del = st.text_input("أدخل أرقام الصفحات المراد حذفها مفصولة بفاصلة (مثال: 2, 5, 7):")
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
    st.markdown("""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-file-signature"></i></div>
    <h3 style='margin:0;'>🔀 إعادة ترتيب وتنظيم الصفحات</h3>
    <p style='font-size:14px; margin:5px 0;'>قم بإعادة صياغة هيكل الصفحات بالترتيب المناسب لاعتماداتك المالية</p></div>
    """, unsafe_allow_html=True)
    
    reorder_file = st.file_uploader("ارفع الملف لإعادة ترتيبه:", type=["pdf"], key="reorder_up")
    if reorder_file:
        doc = fitz.open(stream=reorder_file.read(), filetype="pdf")
        st.info(f"💡 هذا المستند يحتوي على إجمالي: ({len(doc)}) صفحات.")
        order_input = st.text_input("اكتب الترتيب الجديد للصفحات مفصولة بفاصلة (مثال: 3, 1, 2, 4):")
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
    st.markdown("""
    <div class="custom-card"><div class="icon-container pdf-tool-icon"><i class="fa-solid fa-pen-nib"></i></div>
    <h3 style='margin:0;'>✍️ التوقيع الإلكتروني الذكي على المستندات</h3>
    <p style='font-size:14px; margin:5px 0;'>قم بإسقاط وتثبيت ختمك أو توقيعك الشخصي فوق أي مستند رسمي بمرونة مذهلة</p></div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        main_pdf = st.file_uploader("1. ارفع ملف المستند أو الفاتورة (PDF):", type=["pdf"], key="sign_pdf")
    with col_f2:
        sign_img = st.file_uploader("2. ارفع صورة توقيعك أو الختم (يفضل PNG بخلفية شفافة):", type=["png", "jpg", "jpeg"], key="sign_img")
        
    if main_pdf and sign_img:
        st.markdown("---")
        st.markdown("#### 🎯 لوحة التحكم بإحداثيات وأبعاد التوقيع:")
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
                with st.spinner("جاري تثبيت الختم وحماية المستند..."):
                    page = doc[target_page - 1]
                    sign_bytes = sign_img.getvalue()
                    rect = fitz.Rect(x_pos, y_pos, x_pos + sig_width, y_pos + int(sig_width * 0.6))
                    page.insert_image(rect, stream=sign_bytes)
                    
                    output_bytes = doc.write()
                    st.success("✍️ تم دمج وختم التوقيع الإلكتروني على الصفحة المحددة بنجاح!")
                    st.download_button("📥 تحميل المستند الموقع والمختوم جاهزاً", data=output_bytes, file_name="Signed_Document.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"حدث خطأ أثناء التوقيع: {e}")

# --- 8. مساحة إعلانية متجاوبة في الأسفل ---
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
        المحاسب الذكي Pro | <span style="color:#1f6feb;">{lang["motto"]}</span> | 2026 ©
    </div>
""", unsafe_allow_html=True)
