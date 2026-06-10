import streamlit as st
import tabula
import pandas as pd
import io
import base64
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="المحاسب الذكي Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ستايل احترافي (CSS) بدون صور خلفية ---
def apply_custom_style():
    st.markdown("""
    <style>
    /* الخطوط واتجاه الصفحة */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700;900&display=swap');
    
    html, body, [class*="st-emotion-cache"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* الخلفية العامة للموقع */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }

    /* إخفاء الهيدر الافتراضي */
    header, [data-testid="stHeader"] {
        visibility: hidden;
        display: none;
    }

    /* حاوية المحتوى الرئيسية */
    [data-testid="stAppViewBlockContainer"] {
        padding: 2rem 5rem;
    }

    /* تصميم البطاقات (Cards) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #161b22;
        border-radius: 10px 10px 0 0;
        color: #8b949e;
        border: 1px solid #30363d;
        padding: 0 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: white !important;
        border-color: #58a6ff !important;
    }

    /* تجميل صناديق الرفع */
    [data-testid="stFileUploader"] {
        background-color: #161b22;
        border: 2px dashed #30363d;
        border-radius: 15px;
        padding: 20px;
        transition: 0.3s;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #58a6ff;
        background-color: #1c2128;
    }

    /* العناوين */
    h1 {
        color: #58a6ff;
        font-weight: 900;
        text-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
    }

    /* الأزرار */
    .stButton>button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 160, 67, 0.4);
    }

    /* زر التحميل */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        width: 100%;
    }

    /* التذييل الفخم */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #161b22;
        color: #8b949e;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #30363d;
        font-size: 14px;
    }

    /* إخفاء القائمة المزعجة */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# --- 3. واجهة البرنامج الرئيسية ---

# الهيدر
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1>📊 المحاسب الذكي <span style='font-size:20px; color:#8b949e;'>النسخة الاحترافية</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:18px; color:#c9d1d9;'>حوّل مستنداتك الورقية إلى بيانات رقمية بدقة متناهية</p>", unsafe_allow_html=True)

st.markdown("---")

tab1, tab2 = st.tabs(["📑 تحويل PDF إلى Excel", "🔍 استخراج النصوص (OCR)"])

# --- التبويب الأول: PDF to Excel ---
with tab1:
    st.markdown("### 📥 رفع ملفات الـ PDF")
    pdf_files = st.file_uploader("يمكنك رفع عدة ملفات معاً", type=["pdf"], key="pdf_main", accept_multiple_files=True)
    
    if pdf_files:
        for uploaded_pdf in pdf_files:
            with st.container():
                st.info(f"📁 معالجة ملف: {uploaded_pdf.name}")
                if st.button(f"بدأ التحويل لـ {uploaded_pdf.name}"):
                    try:
                        with st.spinner('جاري تحليل الجداول...'):
                            # قراءة الجداول باستخدام tabula
                            dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                            
                            if dfs:
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    workbook = writer.book
                                    header_fmt = workbook.add_format({
                                        'bold': True, 'bg_color': '#1f6feb', 
                                        'font_color': 'white', 'border': 1, 'align': 'center'
                                    })
                                    
                                    current_row = 0
                                    for i, df in enumerate(dfs):
                                        # تنظيف البيانات وسد الأقواس بشكل صحيح هنا
                                        df = df.fillna('').replace([float('inf'), float('-inf')], 0)
                                        df.to_excel(writer, index=False, startrow=current_row, sheet_name='البيانات المستخرجة')
                                        current_row += len(df) + 2
                                    
                                st.success("🚀 تمت المعالجة بنجاح!")
                                st.download_button(
                                    label="📥 تحميل ملف Excel الجاهز",
                                    data=output.getvalue(),
                                    file_name=f"Excel_{uploaded_pdf.name.replace('.pdf', '')}.xlsx",
                                    mime="application/vnd.ms-excel"
                                )
                            else:
                                st.warning("⚠️ لم يتم العثور على جداول واضحة في هذا الملف.")
                    except Exception as e:
                        st.error(f"حدث خطأ: {str(e)}")

# --- التبويب الثاني: OCR ---
with tab2:
    st.markdown("### 🔍 استخراج نصوص الصور والـ PDF")
    ocr_file = st.file_uploader("ارفع صورة (JPG, PNG) أو ملف PDF", type=["jpg", "png", "jpeg", "pdf"], key="ocr_main")
    
    if ocr_file:
        if st.button("🚀 ابدأ استخراج النصوص الآن"):
            full_text = ""
            try:
                with st.spinner('جاري قراءة النصوص بالذكاء الاصطناعي...'):
                    if ocr_file.type == "application/pdf":
                        # معالجة PDF نصي أو صوري
                        doc = fitz.open(stream=ocr_file.read(), filetype="pdf")
                        for page in doc:
                            text = page.get_text()
                            if text.strip():
                                full_text += text + "\n"
                            else:
                                # إذا كانت الصفحة صورة
                                pix = page.get_pixmap()
                                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                full_text += pytesseract.image_to_string(img, lang='ara+eng') + "\n"
                    else:
                        # معالجة صورة مباشرة
                        img = Image.open(ocr_file)
                        full_text = pytesseract.image_to_string(img, lang='ara+eng')

                if full_text.strip():
                    st.markdown("#### ✅ النتائج المستخرجة:")
                    st.text_area("", value=full_text, height=300)
                    st.download_button(
                        label="📥 حفظ النص كملف TXT",
                        data=full_text,
                        file_name="extracted_text.txt"
                    )
                else:
                    st.warning("لم نتمكن من العثور على نصوص واضحة.")
            except Exception as e:
                st.error(f"خطأ في المعالجة: {e}")

# التذييل (Footer)
st.markdown("""
    <div class="footer">
        المحاسب الذكي Pro | الفصل في الذمة.. الوصل في الأمانة | 2026 ©
    </div>
""", unsafe_allow_html=True)
