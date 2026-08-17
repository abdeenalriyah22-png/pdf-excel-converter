import sys
import subprocess

# تثبيت المكتبات تلقائياً في حال عدم وجودها
try:
    import pdfplumber
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber", "openpyxl"])
    import pdfplumber

import streamlit as st
import pandas as pd
import io

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="المحاسب الذكي Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. القاموس متعدد اللغات
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
        "ocr_title": "مستخرج النصوص والمستندات (OCR)",
        "ocr_desc": "ارفع صورة المستند أو الفاتورة لاستخراج النصوص والبيانات منها مباشرة",
        "ocr_upload_label": "قم بسحب وإفلات صور المستندات (PNG, JPG, JPEG) هنا",
        "theme_label": "المظهر / Theme 🎨",
        "lang_label": "اختر اللغة / Choose Language 🌐",
        "download_btn": "📥 تحميل ملف Excel المنسق",
        "processing": "جاري معالجة الملفات واستخراج الجداول...",
        "success": "تمت معالجة الملفات بنجاح!"
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
        "theme_label": "Theme / المظهر 🎨",
        "lang_label": "Choose Language / اختر اللغة 🌐",
        "download_btn": "📥 Download Formatted Excel File",
        "processing": "Processing files and extracting tables...",
        "success": "Files processed successfully!"
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
        "theme_label": "Theme / المظهر 🎨",
        "lang_label": "زبان کا انتخاب کریں / Choose Language 🌐",
        "download_btn": "📥 ڈاؤن لوڈ کریں فارمیٹ شدہ ایکسل فائل",
        "processing": "فائلوں پر کارروائی ہو رہی ہے...",
        "success": "فائلیں کامیابی کے ساتھ پروسیس ہو گئیں!"
    }
}

# 3. شريط الخيارات العلوي (المظهر الفاتح افتراضي + اللغة)
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

# تحديد رمز اللغة والمظهر والاتجاه
lang_code = "ar" if lang_choice == "العربية" else ("en" if lang_choice == "English" else "ur")
t = TRANSLATIONS[lang_code]
is_dark = "Dark" in theme_choice
direction = "rtl" if lang_code in ["ar", "ur"] else "ltr"
text_align = "right" if direction == "rtl" else "left"

# 4. تنسيقات CSS لدعم الاتجاه والتصميم الداكن/الفاتح
bg_color = "#0b0f19" if is_dark else "#f1f5f9"
text_primary = "#f8fafc" if is_dark else "#0f172a"
text_secondary = "#94a3b8" if is_dark else "#475569"
card_bg = "#1e293b" if is_dark else "#ffffff"
card_border = "#334155" if is_dark else "#cbd5e1"
accent_color = "#3b82f6"

st.markdown(f"""
<style>
/* ضبط الاتجاه العام للتطبيق بناءً على اللغة */
.stApp {{
    background-color: {bg_color};
    color: {text_primary};
    direction: {direction};
    text-align: {text_align};
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

/* محاذاة نصوص ومكونات Streamlit */
.stMarkdown, .stSelectbox, .stFileUploader, .stTabs {{
    direction: {direction};
    text-align: {text_align};
}}

/* حاوية الدوائر ثلاثية الأبعاد 3D */
.spheres-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 90px;
    position: relative;
    perspective: 800px;
}}

.sphere {{
    border-radius: 50%;
    position: absolute;
    background: radial-gradient(circle at 35% 35%, #60a5fa, #2563eb, #1e3a8a);
    box-shadow: inset -5px -5px 12px rgba(0, 0, 0, 0.4),
                inset 5px 5px 12px rgba(255, 255, 255, 0.7),
                0 10px 20px rgba(0, 0, 0, 0.3);
    animation: bounce 2.4s infinite ease-in-out alternate;
}}

.s1 {{ width: 44px; height: 44px; left: 15%; animation-delay: 0s; animation-duration: 2.1s; }}
.s2 {{ width: 24px; height: 24px; left: 38%; animation-delay: 0.4s; animation-duration: 1.7s; background: radial-gradient(circle at 35% 35%, #f43f5e, #e11d48, #881337); }}
.s3 {{ width: 50px; height: 50px; left: 60%; animation-delay: 0.8s; animation-duration: 2.5s; background: radial-gradient(circle at 35% 35%, #34d399, #059669, #064e3b); }}
.s4 {{ width: 20px; height: 20px; left: 82%; animation-delay: 0.2s; animation-duration: 1.4s; background: radial-gradient(circle at 35% 35%, #fbbf24, #d97706, #78350f); }}

@keyframes bounce {{
    0% {{ transform: translateY(22px) scale(0.88) rotateX(15deg); }}
    50% {{ transform: translateY(-18px) scale(1.1) rotateX(-20deg); }}
    100% {{ transform: translateY(15px) scale(0.92) rotateX(25deg); }}
}}

/* الترويسة الرئيسية */
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

.main-title span {{
    color: {accent_color};
}}

.main-subtitle {{
    font-size: 1.05rem;
    color: {text_secondary};
    margin-top: 6px;
}}

/* بطاقات العرض */
.card-box {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 28px;
    margin-top: 10px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}}

/* العبارة / التوقيع في الأسفل بالمنتصف */
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
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}}
</style>
""", unsafe_allow_html=True)

# 5. الهيدر الرئيسي وتنسيق الكور ثلاثية الأبعاد
header_col1, header_col2, header_col3 = st.columns([1.2, 2.6, 1.2])

with header_col1:
    st.markdown("""
    <div class="spheres-container">
        <div class="sphere s1"></div>
        <div class="sphere s2"></div>
        <div class="sphere s3"></div>
        <div class="sphere s4"></div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown(f"""
    <div class="main-header">
        <h1 class="main-title">{t['title']}</h1>
        <p class="main-subtitle">{t['subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)

with header_col3:
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 90px;">
        <svg width="100%" height="75" viewBox="0 0 300 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="300" height="80" rx="12" fill="#3b82f6" fill-opacity="0.15"/>
            <rect x="20" y="35" width="18" height="30" rx="3" fill="#2563eb"/>
            <rect x="50" y="20" width="18" height="45" rx="3" fill="#3b82f6"/>
            <rect x="80" y="45" width="18" height="20" rx="3" fill="#60a5fa"/>
            <rect x="110" y="15" width="18" height="50" rx="3" fill="#2563eb"/>
            <rect x="140" y="30" width="18" height="35" rx="3" fill="#3b82f6"/>
            <rect x="170" y="25" width="18" height="40" rx="3" fill="#60a5fa"/>
            <rect x="200" y="10" width="18" height="55" rx="3" fill="#2563eb"/>
            <path d="M 20 40 Q 80 10 140 30 T 260 15" stroke="#10b981" stroke-width="4" fill="none" stroke-linecap="round"/>
        </svg>
    </div>
    """, unsafe_allow_html=True)

# 6. التبويبات (تحويل الملفات / استخراج النصوص OCR)
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

# 7. أسفل الصفحة: التوقيع / العبارة متوسّطة
st.markdown(f"""
<div class="footer-motto-wrapper">
    <div class="footer-motto-box">{t['motto']}</div>
</div>
""", unsafe_allow_html=True)
