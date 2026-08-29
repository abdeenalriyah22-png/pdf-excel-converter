import pdfplumber
import arabic_reshaper
from bidi.algorithm import get_display
import streamlit as st
import pandas as pd
import io

# ---------------------------------------------------------
# 1. دالة معالجة واستعادة النصوص والمصطلحات المحاسبية
# ---------------------------------------------------------
def fix_pdf_text_cell(text):
    if not isinstance(text, str) or not text.strip():
        return text

    # إصلاح الأخطاء الخاصة بالعملة
    text = text.replace('.س.ر', 'ر.س.').replace('س.ر.', 'ر.س.')

    # فحص وجود حروف عربية
    has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
    if not has_arabic:
        return text

    # ضبط الترتيب والبصمة البصرية للنص العربي في ملفات التصدير الخارجية
    try:
        reshaped = arabic_reshaper.reshape(text)
        corrected = get_display(reshaped)
    except Exception:
        corrected = text
        
    return corrected

# ---------------------------------------------------------
# 2. دالة استخراج الجداول المتقدمة (محدثة لدعم كافة أنواع الجداول)
# ---------------------------------------------------------
def extract_tables_from_pdf(pdf_file):
    extracted_dfs = []
    
    strategies = [
        {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
        {"vertical_strategy": "text", "horizontal_strategy": "text", "snap_tolerance": 5, "join_tolerance": 5},
        {"vertical_strategy": "explicit", "horizontal_strategy": "text"}
    ]
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = []
            
            for settings in strategies:
                try:
                    tables = page.extract_tables(table_settings=settings)
                    if tables and len(tables) > 0:
                        break
                except Exception:
                    continue
            
            if not tables:
                try:
                    tables = page.extract_tables()
                except Exception:
                    tables = []
            
            if not tables:
                continue
                
            for tbl_idx, table in enumerate(tables):
                if not table or len(table) < 1:
                    continue
                
                df = pd.DataFrame(table)
                df = df.dropna(how='all').dropna(how='all', axis=1)
                if df.empty or df.shape[0] < 1:
                    continue

                if df.shape[0] > 1:
                    df.columns = [str(col) if col is not None else "" for col in df.iloc[0]]
                    df = df[1:].reset_index(drop=True)

                try:
                    df = df.map(fix_pdf_text_cell)
                    df.columns = [fix_pdf_text_cell(str(col)) for col in df.columns]
                except Exception:
                    df = df.applymap(fix_pdf_text_cell)
                    df.columns = [fix_pdf_text_cell(str(col)) for col in df.columns]

                sheet_name = f"P{page_num+1}_T{tbl_idx+1}"[:31]
                extracted_dfs.append((sheet_name, df))
                
    return extracted_dfs

# ---------------------------------------------------------
# 3. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="المحاسب الذكي Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 4. القاموس متعدد اللغات
# ---------------------------------------------------------
TRANSLATIONS = {
    "ar": {
        "title": "المحاسب الذكي Pro",
        "subtitle": "النظام السحابي المتطور لمعالجة الجداول والبيانات ذكياً",
        "motto": "« الفصل في الذمة.. الوصل في الأمانة »",
        "tab_convert": "📄 تحويل PDF و CSV إلى جداول Excel",
        "tab_ocr": "🔍 استخراج النصوص الذكي (OCR)",
        "extractor_title": "مستخرج جداول البيانات",
        "extractor_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF أو ملفات CSV إلى ملف إكسيل منسق تلقائياً",
        "upload_label": "قم بسحب وإفلات ملفات الـ PDF أو CSV الخاصة بالجداول هنا",
        "ocr_title": "مستخرج النصوص والمسندات (OCR)",
        "ocr_desc": "ارفع صورة المستند أو الفاتورة لاستخراج النصوص والبيانات منها مباشرة",
        "ocr_upload_label": "قم بسحب وإفلات صور المستندات (PNG, JPG, JPEG) هنا",
        "convert_btn": "⚡ بدء تحويل الملفات واستخراج الجداول",
        "download_btn": "📥 تحميل ملف Excel المنسق",
        "processing": "جاري معالجة الملفات وإصلاح اتجاه النصوص العربية...",
        "success": "تمت معالجة الملفات واستخراج الجداول بنجاح!",
        "no_tables": "لم يتم العثور على جداول صالحة. تأكد أن ملف الـ PDF يحتوي على نصوص جدولية وليست صوراً مسحوحة ضوئياً (Scanned).",
        "select_file_warn": "يرجى رفع ملف واحد على الأقل أولاً."
    },
    "en": {
        "title": "Smart Accountant Pro",
        "subtitle": "Advanced Cloud System for Smart Table & Data Processing",
        "motto": "« الفصل في الذمة.. الوصل في الأمانة »",
        "tab_convert": "📄 Convert PDF & CSV to Excel",
        "tab_ocr": "🔍 Smart Text Extraction (OCR)",
        "extractor_title": "Data Table Extractor",
        "extractor_desc": "Upload your files to automatically convert silent tables in PDF or CSV to formatted Excel files",
        "upload_label": "Drag and drop your PDF or CSV table files here",
        "ocr_title": "Document Text Extractor (OCR)",
        "ocr_desc": "Upload image documents or invoices to extract text and data directly",
        "ocr_upload_label": "Drag and drop document images (PNG, JPG, JPEG) here",
        "convert_btn": "⚡ Start Converting Files & Extract Tables",
        "download_btn": "📥 Download Formatted Excel File",
        "processing": "Processing files and extracting tables...",
        "success": "Files processed successfully!",
        "no_tables": "No valid tables found. Ensure the PDF contains text tables and not scanned images.",
        "select_file_warn": "Please upload at least one file first."
    },
    "ur": {
        "title": "سمارٹ اکاؤنٹنٹ Pro",
        "subtitle": "سمارٹ ٹیبل اور ڈیٹا پروسیسنگ کے لیے ایڈوانسڈ کلاؤڈ سسٹم",
        "motto": "« الفصل في الذمة.. الوصل في الأمانة »",
        "tab_convert": "📄 PDF اور CSV کو Excel میں تبدیل کریں",
        "tab_ocr": "🔍 سمارٹ ٹیکسٹ ایکسٹریکشن (OCR)",
        "extractor_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "extractor_desc": "PDF یا CSV میں خاموش ٹیبلز کو فارمیٹ شدہ ایکسل فائلوں میں خودکار تبدیل کرنے کے لیے فائلیں اپ لوڈ کریں",
        "upload_label": "اپنی PDF یا CSV فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "ocr_title": "ڈاکیومنٹ ٹیکسٹ ایکسٹریکٹر (OCR)",
        "ocr_desc": "متن اور ڈیٹا کو براہ راست نکالنے کے لیے دستاویز کی تصاویر اپ لوڈ کریں",
        "ocr_upload_label": "تصاویر (PNG, JPG, JPEG) یہاں ڈریگ اور ڈراپ کریں",
        "convert_btn": "⚡ فائلوں کو تبدیل کرنا شروع کریں",
        "download_btn": "📥 ڈاؤن لوڈ کریں فارمیٹ شدہ ایکسل فائل",
        "processing": "فائلوں پر کارروائی ہو رہی ہے...",
        "success": "فائلیں کامیابی کے ساتھ پروسیس ہو گئیں!",
        "no_tables": "کوئی جدول نہیں ملا۔ یقینی بنائیں کہ PDF میں اسکین شدہ تصاویر کے بجائے متن موجود ہے۔",
        "select_file_warn": "برائے مہربانی پہلے کم از کم ایک فائل اپ لوڈ کریں۔"
    }
}

# ---------------------------------------------------------
# 5. شريط الخيارات العلوي والترويسة
# ---------------------------------------------------------
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    theme_choice = st.selectbox(
        "Theme / المظهر 🎨",
        ["الفاتح العصري (Light Theme)", "الداكن الأنيق (Dark Theme)"],
        index=0
    )

with top_col2:
    lang_choice = st.selectbox(
        "Choose Language / اختر اللغة / زبان کا انتخاب کریں 🌐",
        ["العربية", "English", "اردو"],
        index=0
    )

lang_code = "ar" if lang_choice == "العربية" else ("en" if lang_choice == "English" else "ur")
t = TRANSLATIONS[lang_code]
is_dark = "Dark" in theme_choice
direction = "rtl" if lang_code in ["ar", "ur"] else "ltr"
text_align = "right" if direction == "rtl" else "left"

# ---------------------------------------------------------
# 6. الألوان وتصحيح القوائم المنسدلة للوضع الداكن
# ---------------------------------------------------------
if is_dark:
    bg_color = "#090d16"
    card_bg = "#111827"
    card_border = "#1f2937"
    text_primary = "#f3f4f6"
    text_secondary = "#9ca3af"
    accent_primary = "#3b82f6"
    accent_gradient = "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
    shadow_effect = "0 10px 30px -10px rgba(0, 0, 0, 0.5)"
    
    dropdown_bg = "#1f2937"
    dropdown_text = "#ffffff"
    dropdown_hover = "#374151"
else:
    bg_color = "#f8fafc"
    card_bg = "#ffffff"
    card_border = "#e2e8f0"
    text_primary = "#0f172a"
    text_secondary = "#64748b"
    accent_primary = "#2563eb"
    accent_gradient = "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)"
    shadow_effect = "0 10px 25px -5px rgba(0, 0, 0, 0.05)"
    
    dropdown_bg = "#ffffff"
    dropdown_text = "#0f172a"
    dropdown_hover = "#f1f5f9"

st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_color};
    color: {text_primary};
    direction: {direction};
    text-align: {text_align};
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}
.stMarkdown, .stSelectbox, .stFileUploader, .stTabs, .stButton {{
    direction: {direction};
    text-align: {text_align};
}}

.stSelectbox div[data-baseweb="select"] > div {{
    background-color: {dropdown_bg} !important;
    color: {dropdown_text} !important;
    border-color: {card_border} !important;
}}
.stSelectbox span {{
    color: {dropdown_text} !important;
}}
div[data-baseweb="popover"] div {{
    background-color: {dropdown_bg} !important;
    color: {dropdown_text} !important;
}}
div[role="option"] {{
    background-color: {dropdown_bg} !important;
    color: {dropdown_text} !important;
}}
div[role="option"]:hover {{
    background-color: {dropdown_hover} !important;
    color: {dropdown_text} !important;
}}

.app-header {{
    text-align: center;
    padding: 25px 0 15px 0;
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 20px;
    margin-bottom: 25px;
    box-shadow: {shadow_effect};
}}
.main-title {{
    font-size: 2.4rem;
    font-weight: 800;
    color: {text_primary};
    margin: 0;
    letter-spacing: -0.5px;
}}
.main-subtitle {{
    font-size: 1.02rem;
    color: {text_secondary};
    margin-top: 8px;
    font-weight: 400;
}}
.card-box {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 20px;
    padding: 32px;
    margin-top: 15px;
    box-shadow: {shadow_effect};
    transition: all 0.3s ease;
}}
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background-color: {card_bg};
    padding: 6px;
    border-radius: 14px;
    border: 1px solid {card_border};
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 10px;
    color: {text_secondary};
    font-weight: 600;
    padding: 10px 20px;
}}
.stTabs [aria-selected="true"] {{
    background: {accent_gradient} !important;
    color: #ffffff !important;
}}
.stButton button {{
    background: {accent_gradient};
    color: white;
    border-radius: 12px;
    font-weight: 600;
    border: none;
    padding: 0.6rem 1.2rem;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    transition: all 0.2s ease-in-out;
}}
.stButton button:hover {{
    opacity: 0.95;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}}
.footer-motto-wrapper {{
    text-align: center;
    margin-top: 50px;
    margin-bottom: 25px;
}}
.footer-motto-box {{
    text-align: center;
    font-size: 1.1rem;
    font-weight: 700;
    color: {accent_primary};
    background: {'rgba(59, 130, 246, 0.1)' if is_dark else 'rgba(37, 99, 235, 0.06)'};
    padding: 10px 28px;
    border-radius: 30px;
    display: inline-block;
    border: 1px solid {'rgba(59, 130, 246, 0.25)' if is_dark else 'rgba(37, 99, 235, 0.15)'};
    box-shadow: {shadow_effect};
}}
</style>

<div class="app-header">
    <div class="main-title">{t['title']}</div>
    <div class="main-subtitle">{t['subtitle']}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. التبويبات والمعالجة
# ---------------------------------------------------------
tab1, tab2 = st.tabs([t['tab_convert'], t['tab_ocr']])

with tab1:
    st.markdown(f"""
    <div class="card-box">
        <div style="text-align: center; margin-bottom: 15px;">
            <div style="font-size: 2.8rem; margin-bottom: 5px;">📊</div>
            <h2 style="margin: 5px 0; color: {text_primary}; font-size: 1.5rem;">{t['extractor_title']}</h2>
            <p style="color: {text_secondary}; font-size: 0.95rem;">{t['extractor_desc']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        t['upload_label'],
        type=["pdf", "csv"],
        accept_multiple_files=True,
        key="table_uploader"
    )

    if st.button(t['convert_btn'], type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning(t['select_file_warn'])
        else:
            with st.spinner(t['processing']):
                output_buffer = io.BytesIO()
                tables_count = 0
                
                # إنشاء ملف الـ Excel وضبط إعدادات الـ RTL لكل ورقة عمل (Sheet) لمنع انعكاس الحروف
                with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                    for idx, file in enumerate(uploaded_files):
                        if file.name.endswith('.csv'):
                            try:
                                df = pd.read_csv(file)
                                try:
                                    df = df.map(fix_pdf_text_cell)
                                except Exception:
                                    df = df.applymap(fix_pdf_text_cell)
                                df.columns = [fix_pdf_text_cell(str(col)) for col in df.columns]
                                
                                sheet_name = f"CSV_{idx+1}"[:31]
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                tables_count += 1
                            except Exception as e:
                                st.error(f"خطأ في معالجة ملف CSV: {e}")
                        
                        elif file.name.endswith('.pdf'):
                            try:
                                extracted_tables = extract_tables_from_pdf(file)
                                for sheet_name, df in extracted_tables:
                                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                                    tables_count += 1
                            except Exception as e:
                                st.error(f"خطأ في استخراج جدول الـ PDF: {e}")

                # ضبط اتجاه الأوراق برمجياً في openpyxl لتظهر باليمين لليسار طبيعياً
                if tables_count > 0:
                    output_buffer.seek(0)
                    import openpyxl
                    wb = openpyxl.load_workbook(output_buffer)
                    for sheet in wb.sheetnames:
                        ws = wb[sheet]
                        ws.views.sheetView[0].rightToLeft = True
                    
                    final_buffer = io.BytesIO()
                    wb.save(final_buffer)
                    final_buffer.seek(0)

                    st.success(t['success'])
                    st.download_button(
                        label=t['download_btn'],
                        data=final_buffer.getvalue(),
                        file_name="converted_tables.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                else:
                    st.warning(t['no_tables'])

with tab2:
    st.markdown(f"""
    <div class="card-box">
        <div style="text-align: center; margin-bottom: 15px;">
            <div style="font-size: 2.8rem; margin-bottom: 5px;">🖼️</div>
            <h2 style="margin: 5px 0; color: {text_primary}; font-size: 1.5rem;">{t['ocr_title']}</h2>
            <p style="color: {text_secondary}; font-size: 0.95rem;">{t['ocr_desc']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_ocr_images = st.file_uploader(
        t['ocr_upload_label'],
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="ocr_uploader"
    )

# ---------------------------------------------------------
# 8. التوقيع السفلي
# ---------------------------------------------------------
st.markdown(f"""
<div class="footer-motto-wrapper">
    <div class="footer-motto-box">{t['motto']}</div>
</div>
""", unsafe_allow_html=True)
