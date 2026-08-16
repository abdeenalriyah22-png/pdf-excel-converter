import streamlit as st

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
        "title": "المحاسب الذكي",
        "subtitle": "النظام السحابي المتطور لمعالجة الجداول والبيانات ذكياً",
        "motto": "« الفصل في الذمة.. الوصل في الأمانة »",
        "tab_convert": "📄 تحويل PDF و CSV إلى جداول Excel",
        "tab_ocr": "🔍 استخراج النصوص الذكي (OCR)",
        "extractor_title": "مستخرج جداول البيانات",
        "extractor_desc": "ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF أو ملفات CSV إلى ملف إكسيل منسق تلقائياً",
        "upload_label": "قم بسحب وإفلات ملفات الـ PDF أو CSV الخاصة بالجداول هنا",
        "theme_label": "المظهر / Theme 🎨",
        "lang_label": "اختر اللغة / Choose Language 🌐"
    },
    "en": {
        "title": "Smart Accountant",
        "subtitle": "Advanced Cloud System for Smart Table & Data Processing",
        "motto": "« الفصل في الذمة.. الوصل في الأمانة »",
        "tab_convert": "📄 Convert PDF & CSV to Excel",
        "tab_ocr": "🔍 Smart Text Extraction (OCR)",
        "extractor_title": "Data Table Extractor",
        "extractor_desc": "Upload your files to automatically convert silent tables in PDF or CSV to formatted Excel files",
        "upload_label": "Drag and drop your PDF or CSV table files here",
        "theme_label": "Theme / المظهر 🎨",
        "lang_label": "Choose Language / اختر اللغة 🌐"
    },
    "ur": {
        "title": "سمارٹ اکاؤنٹنٹ",
        "subtitle": "سمارٹ ٹیبل اور ڈیٹا پروسیسنگ کے لیے ایڈوانسڈ کلاؤڈ سسٹم",
        "motto": "« الفصل في الذمة.. الوصل في الأمانة »",
        "tab_convert": "📄 PDF اور CSV کو Excel میں تبدیل کریں",
        "tab_ocr": "🔍 سمارٹ ٹیکسٹ ایکسٹریکشن (OCR)",
        "extractor_title": "ڈیٹا ٹیبل ایکسٹریکٹر",
        "extractor_desc": "PDF یا CSV میں خاموش ٹیبلز کو فارمیٹ شدہ ایکسل فائلوں میں خودکار تبدیل کرنے کے لیے فائلیں اپ لوڈ کریں",
        "upload_label": "اپنی PDF یا CSV فائلیں یہاں ڈریگ اور ڈراپ کریں",
        "theme_label": "Theme / المظهر 🎨",
        "lang_label": "زبان کا انتخاب کریں / Choose Language 🌐"
    }
}

# 3. شريط الخيارات العلوي (اللغة والمظهر)
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    theme_choice = st.selectbox(
        "Theme / المظهر 🎨",
        ["ثلاثي الأبعاد الفاتح (3D Light)", "ثلاثي الأبعاد الداكن (3D Dark)"],
        index=0
    )

with top_col2:
    lang_choice = st.selectbox(
        "Choose Language / اختر اللغة / زبان کا انتخاب کریں 🌐",
        ["العربية", "English", "اردو"],
        index=0
    )

# تحديد رمز اللغة والمظهر
lang_code = "ar" if lang_choice == "العربية" else ("en" if lang_choice == "English" else "ur")
t = TRANSLATIONS[lang_code]
is_dark = "Dark" in theme_choice

# 4. تنسيقات CSS للمظهر والدوائر ثلاثية الأبعاد 3D
bg_color = "#0f172a" if is_dark else "#f8fafc"
text_primary = "#f8fafc" if is_dark else "#1e293b"
text_secondary = "#94a3b8" if is_dark else "#64748b"
card_bg = "#1e293b" if is_dark else "#ffffff"
card_border = "#334155" if is_dark else "#e2e8f0"

st.markdown(f"""
<style>
/* خلفية التطبيق العامة */
.stApp {{
    background-color: {bg_color};
    color: {text_primary};
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

/* حاوية الدوائر ثلاثية الأبعاد */
.spheres-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 110px;
    position: relative;
    perspective: 800px;
}}

/* نمط الدائرة الأساسي ثلاثي الأبعاد 3D */
.sphere {{
    border-radius: 50%;
    position: absolute;
    background: radial-gradient(circle at 35% 35%, #60a5fa, #2563eb, #1e3a8a);
    box-shadow: inset -6px -6px 14px rgba(0, 0, 0, 0.4),
                inset 6px 6px 14px rgba(255, 255, 255, 0.7),
                0 12px 24px rgba(0, 0, 0, 0.3);
    animation: bounce 2.4s infinite ease-in-out alternate;
}}

/* تفاصيل وأحجام ومواقع ومواعيد قفز عشوائية للدوائر */
.s1 {{ width: 48px; height: 48px; left: 10%; animation-delay: 0s; animation-duration: 2.1s; }}
.s2 {{ width: 26px; height: 26px; left: 34%; animation-delay: 0.4s; animation-duration: 1.7s; background: radial-gradient(circle at 35% 35%, #f43f5e, #e11d48, #881337); }}
.s3 {{ width: 56px; height: 56px; left: 54%; animation-delay: 0.8s; animation-duration: 2.5s; background: radial-gradient(circle at 35% 35%, #34d399, #059669, #064e3b); }}
.s4 {{ width: 20px; height: 20px; left: 82%; animation-delay: 0.2s; animation-duration: 1.4s; background: radial-gradient(circle at 35% 35%, #fbbf24, #d97706, #78350f); }}

/* أنيميشن القفز العشوائي المجسم ثلاثي الأبعاد */
@keyframes bounce {{
    0% {{
        transform: translateY(28px) scale(0.85) rotateX(15deg);
    }}
    50% {{
        transform: translateY(-22px) scale(1.12) rotateX(-20deg);
    }}
    100% {{
        transform: translateY(18px) scale(0.92) rotateX(25deg);
    }}
}}

/* ترويسة العنوان والعبارة */
.header-title {{
    text-align: center;
    font-size: 2.3rem;
    font-weight: 800;
    margin-bottom: 0px;
    color: {text_primary};
}}

.header-subtitle {{
    text-align: center;
    font-size: 0.95rem;
    color: {text_secondary};
    margin-top: 2px;
    margin-bottom: 6px;
}}

.motto-box {{
    text-align: center;
    font-size: 1.05rem;
    font-weight: 700;
    color: #2563eb;
    background: {'rgba(37, 99, 235, 0.12)' if is_dark else 'rgba(37, 99, 235, 0.08)'};
    padding: 6px 16px;
    border-radius: 20px;
    display: inline-block;
    margin: 4px auto 0 auto;
    border: 1px solid {'rgba(37, 99, 235, 0.3)' if is_dark else 'rgba(37, 99, 235, 0.2)'};
}}

.motto-wrapper {{
    text-align: center;
}}

/* كارت مستخرج البيانات */
.card-container {{
    background-color: {card_bg};
    border: 1px solid {card_border};
    border-radius: 16px;
    padding: 24px;
    margin-top: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
}}
</style>
""", unsafe_allow_html=True)

# 5. الهيدر الرئيسي المقسم إلى 3 أعمدة
col_left, col_center, col_right = st.columns([1.2, 2.6, 1.2])

# الطرف الأيسر (الثاني): الدوائر القافزة ثلاثية الأبعاد
with col_left:
    st.markdown("""
    <div class="spheres-container">
        <div class="sphere s1"></div>
        <div class="sphere s2"></div>
        <div class="sphere s3"></div>
        <div class="sphere s4"></div>
    </div>
    """, unsafe_allow_html=True)

# الوسط: العنوان والوصف وعبارة (الفصل في الذمة.. الوصل في الأمانة)
with col_center:
    st.markdown(f"<div class='header-title'>{t['title']} <span style='color: #2563eb;'>Pro</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header-subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='motto-wrapper'><div class='motto-box'>{t['motto']}</div></div>", unsafe_allow_html=True)

# الطرف الأيمن: شريط/صورة الرسوم البيانية المتحركة
with col_right:
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 110px;">
        <svg width="100%" height="80" viewBox="0 0 300 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="300" height="80" rx="12" fill="#2563eb" fill-opacity="0.15"/>
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

st.markdown("<br>", unsafe_allow_html=True)

# 6. التبويبات الرئيسية
tab1, tab2 = st.tabs([t['tab_convert'], t['tab_ocr']])

with tab1:
    st.markdown(f"""
    <div class="card-container">
        <div style="text-align: center; margin-bottom: 15px;">
            <div style="font-size: 3rem; color: #10b981;">📊</div>
            <h2 style="margin: 5px 0; color: {text_primary};">{t['extractor_title']}</h2>
            <p style="color: {text_secondary}; font-size: 0.95rem;">{t['extractor_desc']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        t['upload_label'],
        type=["pdf", "csv"],
        accept_multiple_files=True
    )

with tab2:
    st.info("قسم استخراج النصوص الذكي (OCR) جاهز لربط المحرك الخاص بك.")
