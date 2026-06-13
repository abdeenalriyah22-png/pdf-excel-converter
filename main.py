import streamlit as st
import streamlit.components.v1 as components

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المحاسب الذكي Pro", layout="wide", initial_sidebar_state="expanded")

# --- قاموس الترجمة ---
translations = {
    "العربية": {"dir": "rtl", "align": "right", "title": "📊 المحاسب الذكي Pro", "menu": "🛠️ الأدوات", "theme": "🌓 المظهر", "lang": "🌐 اللغة", "excel": "📊 تحويل PDF", "ocr": "🔍 OCR", "motto": "الفصل في الذمة.. الوصل في الأمانة"},
    "English": {"dir": "ltr", "align": "left", "title": "📊 Smart Accountant Pro", "menu": "🛠️ Tools", "theme": "🌓 Theme", "lang": "🌐 Language", "excel": "📊 PDF to Excel", "ocr": "🔍 OCR", "motto": "Separation of liability... connection in trust"},
    "اردو": {"dir": "rtl", "align": "right", "title": "📊 سمارٹ اکاؤنٹنٹ Pro", "menu": "🛠️ ٹولز", "theme": "🌓 تھیم", "lang": "🌐 زبان", "excel": "📊 پی ڈی ایف ٹو ایکسل", "ocr": "🔍 OCR", "motto": "الفصل في الذمة.. الوصل في الأمانة"}
}

# --- القائمة الجانبية (اللغة في الأسفل) ---
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    theme_choice = st.radio("🌓 المظهر / Theme", ["Dark Neon 🌑", "Light ☀️"])
    st.markdown("---")
    current_tool = st.radio("🛠️ الأدوات / Tools", ["📊 تحويل PDF", "🔍 OCR", "📂 دمج ملفات"])
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True) # مسافة لضمان نزول اللغة
    selected_lang = st.selectbox("🌐 اللغة / Language", ["العربية", "English", "اردو"])
    lang = translations[selected_lang]

# --- التنسيق النيون الشامل ---
st.markdown(f"""
<style>
    /* القائمة الجانبية */
    [data-testid="stSidebar"] {{ background-color: #050a14 !important; border-left: 2px solid #00f2fe !important; }}
    
    /* الألوان النيون */
    .stApp {{ background-color: #050a14 !important; color: #00f2fe !important; }}
    
    /* المستطيلات (Upload & Inputs) */
    [data-testid="stFileUploader"] {{ 
        border: 2px dashed #00f2fe !important; 
        background: #0b1526 !important; 
        border-radius: 15px !important; 
    }}
    
    /* القوائم المنسدلة */
    div[data-baseweb="select"] {{ 
        background: #0b1526 !important; 
        border: 1px solid #00f2fe !important; 
    }}
    
    /* النصوص والخطوط */
    h1, h2, h3, label {{ color: #00f2fe !important; font-family: 'Cairo', sans-serif !important; }}
    
    /* إعدادات الاتجاه */
    html, body {{ direction: {lang['dir']} !important; text-align: {lang['align']} !important; }}
</style>
""", unsafe_allow_html=True)

# --- عرض المحتوى ---
st.markdown(f"<h1>{lang['title']}</h1>", unsafe_allow_html=True)

# مثال لأداة الـ Upload
st.markdown("<div style='border:1px solid #00f2fe; padding:20px; border-radius:15px;'>", unsafe_allow_html=True)
st.file_uploader("قم برفع الملف هنا (نيون ستايل)", type=["pdf"])
st.markdown("</div>", unsafe_allow_html=True)

# التذييل
st.markdown(f"<div style='text-align:center; padding:50px; color:#00f2fe;'>{lang['motto']} | 2026 ©</div>", unsafe_allow_html=True)
