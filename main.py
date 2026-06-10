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

# --- 2. ستايل النيون المتطور والأيقونات المتحركة (CSS) ---
def apply_neon_style():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght=400;700;900&display=swap');
    
    <style>
    /* التنسيق العام والخطوط */
    html, body, [class*="st-emotion-cache"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* خلفية الفضاء الداكن الفخمة */
    .stApp {
        background: radial-gradient(circle at center, #111723 0%, #07090e 100%) !important;
        color: #e6edf3;
    }

    /* إخفاء العناصر الافتراضية للمنصة */
    header, [data-testid="stHeader"] {
        visibility: hidden;
        display: none;
    }

    /* حاوية المحتوى الرئيسية وتأثير التوهج الخلفي */
    [data-testid="stAppViewBlockContainer"] {
        padding: 2rem 5rem;
    }

    /* تصميم التبويبات العلوية الحديثة (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: rgba(22, 27, 34, 0.5);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #21262d;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        color: #8b949e;
        border: none;
        padding: 0 25px;
        font-weight: bold;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1f6feb 0%, #0d44a5 100%) !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(31, 111, 235, 0.6);
        transform: scale(1.02);
    }

    /* 💎 صناديق رفع الملفات النيونية المتحركة 💎 */
    [data-testid="stFileUploader"] {
        background-color: rgba(22, 27, 34, 0.7) !important;
        border: 2px dashed #21262d !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.4s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #58a6ff !important;
        background-color: rgba(28, 33, 40, 0.9) !important;
        box-shadow: 0 0 25px rgba(88, 166, 255, 0.25);
        transform: translateY(-4px);
    }

    /* إيضاح نصوص صناديق الرفع */
    [data-testid="stFileUploader"] section *, 
    [data-testid="stFileUploader"] div, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] p {
        color: #ffffff !important;
    }

    /* علامة الـ X لحذف الملف الخاطئ بتأثير نيون أحمر */
    [data-testid="stFileUploader"] button[aria-label="Remove file"] {
        background-color: rgba(255, 75, 75, 0.15) !important;
        border: 1px solid rgba(255, 75, 75, 0.4) !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"] button[aria-label="Remove file"]:hover {
        background-color: #ff4b4b !important;
        box-shadow: 0 0 12px #ff4b4b;
        transform: rotate(90deg);
    }
    [data-testid="stFileUploader"] button[aria-label="Remove file"] svg {
        fill: #ff4b4b !important;
    }
    [data-testid="stFileUploader"] button[aria-label="Remove file"]:hover svg {
        fill: #ffffff !important;
    }

    /* ⚡ تصميم الأيقونات المتحركة المخصصة ⚡ */
    .icon-container {
        font-size: 55px;
        margin-bottom: 15px;
        transition: all 0.4s ease;
        display: inline-block;
    }
    
    /* حركة النبض والارتفاع عند تمرير الماوس */
    .excel-icon { color: #2ea043; text-shadow: 0 0 20px rgba(46, 160, 67, 0.4); }
    .ocr-icon { color: #58a6ff; text-shadow: 0 0 20px rgba(88, 166, 255, 0.4); }
    
    .custom-card:hover .excel-icon {
        transform: scale(1.15) translateY(-5px);
        filter: drop-shadow(0 0 15px #2ea043);
    }
    .custom-card:hover .ocr-icon {
        transform: scale(1.15) rotate(10deg);
        filter: drop-shadow(0 0 15px #58a6ff);
    }

    /* بطاقة العرض الداخلي الاحترافية */
    .custom-card {
        background: linear-gradient(145deg, #161b22 0%, #0f1319 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .custom-card:hover {
        border-color: #444c56;
    }

    /* العناوين المتوهجة */
    h1 {
        color: #ffffff !important;
        font-weight: 900 !important;
        background: linear-gradient(to right, #ffffff, #58a6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* الأزرار الكبيرة وتأثير الحركة عند التمرير */
    .stButton>button {
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
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(46, 160, 67, 0.5);
    }

    /* زر التحميل الأزرق المتوهج */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.2);
        transition: all 0.3s ease;
    }
    [data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(31, 111, 235, 0.5);
    }

    /* تجميل مربع النص المستخرج */
    .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
    }

    /* التذييل الثابت والسفلي الفخم */
    .footer {
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
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

apply_neon_style()

# --- 3. واجهة البرنامج الرئيسية ---

# الرأسية والتصميم العلوي
st.markdown("""
<div style='text-align: right; margin-bottom: 10px;'>
    <h1>📊 المحاسب الذكي <span style='font-size:22px; color:#58a6ff; font-weight:normal;'>Pro</span></h1>
    <p style='font-size:16px; color:#8b949e; margin-top:-10px;'>النظام السحابي المطور لمعالجة الجداول والبيانات ذكياً</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 تحويل PDF إلى جداول Excel", "🔍 استخراج النصوص الذكي (OCR)"])

# --- التبويب الأول: تحويل الجداول لـ Excel ---
with tab1:
    st.markdown("""
    <div class="custom-card">
        <div class="icon-container excel-icon"><i class="fa-solid fa-file-excel fa-beat-hover"></i></div>
        <h3 style='margin:0; color:#ffffff;'>مستخرج جداول البيانات</h3>
        <p style='font-size:14px; color:#8b949e; margin:5px 0;'>ارفع ملفاتك لتحويل أي جدول صامت داخل الـ PDF إلى ملف إكسيل منسق تلقائياً</p>
    </div>
    """, unsafe_allow_html=True)
    
    pdf_files = st.file_uploader("قم بسحب وإفلات ملفات الـ PDF الخاصة بالجداول هنا", type=["pdf"], key="pdf_main", accept_multiple_files=True)
    
    if pdf_files:
        for uploaded_pdf in pdf_files:
            st.write("")
            with st.container():
                st.info(f"📁 ملف قيد التحضير: {uploaded_pdf.name}")
                if st.button(f"بدأ تحويل وجدولة: {uploaded_pdf.name}"):
                    try:
                        with st.spinner('جاري تفكيك الجداول وهيكلتها...'):
                            dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                            
                            if dfs:
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    workbook = writer.book
                                    current_row = 0
                                    for df in dfs:
                                        df = df.fillna('').replace([float('inf'), float('-inf')], 0)
                                        df.to_excel(writer, index=False, startrow=current_row, sheet_name='البيانات المستخرجة')
                                        current_row += len(df) + 2
                                    
                                st.success("🚀 اكتمل التحويل بنجاح وبأعلى دقة!")
                                st.download_button(
                                    label=f"📥 اضغط هنا لتحميل ملف Excel المستخرج",
                                    data=output.getvalue(),
                                    file_name=f"Excel_{uploaded_pdf.name.replace('.pdf', '')}.xlsx",
                                    mime="application/vnd.ms-excel"
                                )
                            else:
                                st.warning("⚠️ لم نكتشف جداول رقمية واضحة داخل هذا الملف.")
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")

# --- التبويب الثاني: استخراج النصوص OCR ---
with tab2:
    st.markdown("""
    <div class="custom-card">
        <div class="icon-container ocr-icon"><i class="fa-solid fa-eye fa-pulse-hover"></i></div>
        <h3 style='margin:0; color:#ffffff;'>قارئ النصوص والماسح الضوئي</h3>
        <p style='font-size:14px; color:#8b949e; margin:5px 0;'>استخراج النصوص العربية والإنجليزية بدقة كاملة من المستندات المصورة والـ PDF الممسوح ضوئياً</p>
    </div>
    """, unsafe_allow_html=True)
    
    ocr_file = st.
