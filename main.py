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

    # تقسيم الكلمات وإعادة ترتيب الكلمات المعكوسة
    words = text.split()
    reversed_words = words[::-1]
    reconstructed_text = " ".join(reversed_words)

    # تطبيق إعادة التشكيل والاتجاه RTL
    try:
        reshaped = arabic_reshaper.reshape(reconstructed_text)
        corrected = get_display(reshaped)
    except Exception:
        corrected = text
        
    return corrected

# ---------------------------------------------------------
# 2. دالة تحويل الأعمدة الرقمية لمنع ظهور علامة التعجب
# ---------------------------------------------------------
def clean_numeric_columns(df):
    for col in df.columns:
        # محاولة تحويل الأعمدة التي تحتوي على أقيم رقمية بحتة أو بعد إزالة الرموز إلى أرقام حقيقية
        try:
            # إزالة المسافات الزائدة
            converted = pd.to_numeric(df[col].astype(str).str.strip(), errors='ignore')
            if pd.api.types.is_numeric_dtype(converted):
                df[col] = converted
        except Exception:
            pass
    return df

# ---------------------------------------------------------
# 3. دالة استخراج الجداول المتقدمة
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

                # تنزيل وتحويل الأرقام لتتخلص من علامة التعجب
                df = clean_numeric_columns(df)

                sheet_name = f"P{page_num+1}_T{tbl_idx+1}"[:31]
                extracted_dfs.append((sheet_name, df))
                
    return extracted_dfs

# ---------------------------------------------------------
# 4. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="المحاسب الذكي Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 5. القاموس متعدد اللغات
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
        "processing": "جاري معالجة الملفات وإصلاح النصوص والأرقام...",
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
        "processing": "Processing files and extracting numbers...",
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
# 6. شريط الخيارات العلوي
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
# 7. تنسيقات CSS
# ---------------------------------------------------------
bg_color = "#0b0f19" if is_dark else "#f1f5f9"
text_primary = "#f8fafc" if is_dark else "#0f172a"
text_secondary = "#94a3b8" if is_dark else "#475569"
card_bg = "#1e293b" if is_dark else "#ffffff"
card_border = "#334155" if is_dark else "#cbd5e1"
accent_color = "#3b82f6"

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
.main-header {{
    text-align: center;
    padding: 10px 0 20px 0;
}}
.main-title {{
    font-size: 2.6rem;
    font-weight: 800;
    color: {text_primary};
    margin: 0;
}}
.main-subtitle {{
    font-size: 1.05rem;
    color: {text_secondary};
    margin-top: 6px;
}}
.card-box {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 28px;
    margin-top: 10px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}}
.footer-motto-wrapper {{
    text-align: center;
    margin-top: 40px;
    margin-bottom: 20px;
}}
.footer-motto-box {{
    text-align: center;
    font-size: 1.1rem;
    font-weight: 700;
    color: {accent_color};
    background: {'rgba(59, 130, 246, 0.12)' if is_dark else 'rgba(59, 130, 246, 0.08)'};
    padding: 8px 24px;
    border-radius: 25px;
    display: inline-block;
    border: 1px solid {'rgba(59, 130, 246, 0.3)' if is_dark else 'rgba(59, 130, 246, 0.2)'};
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. التبويبات والمعالجة
# ---------------------------------------------------------
tab1, tab2 = st.tabs([t['tab_convert'], t['tab_ocr']])

with tab1:
    st.markdown(f"""
    <div class="card-box">
        <div style="text-align: center; margin-bottom: 15px;">
            <div style="font-size: 2.8rem; color: #10b981;">📊</div>
            <h2 style="margin: 5px 0; color: {text_primary};">{t['extractor_title']}</h2>
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
                                df = clean_numeric_columns(df)
                                
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

                if tables_count > 0:
                    st.success(t['success'])
                    st.download_button(
                        label=t['download_btn'],
                        data=output_buffer.getvalue(),
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
            <div style="font-size: 2.8rem; color: #3b82f6;">🖼️</div>
            <h2 style="margin: 5px 0; color: {text_primary};">{t['ocr_title']}</h2>
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
# 9. التوقيع السفلي
# ---------------------------------------------------------
st.markdown(f"""
<div class="footer-motto-wrapper">
    <div class="footer-motto-box">{t['motto']}</div>
</div>
""", unsafe_allow_html=True)
