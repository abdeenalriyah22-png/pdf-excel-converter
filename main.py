import streamlit as st
import streamlit.components.v1 as components
import pdfplumber  # بديل tabula (لا يحتاج جافا)
import pandas as pd
import io
import arabic_reshaper # لتصحيح شكل الحروف
from bidi.algorithm import get_display # لتصحيح اتجاه النصوص
from PIL import Image
import pytesseract
import fitz
from st_copy_to_clipboard import st_copy_to_clipboard

# ... (نفس إعدادات الصفحة، كود الإعلانات، وقاموس اللغات كما هي في ملفك الأصلي) ...

# وظيفة جديدة لتصحيح النصوص قبل وضعها في الإكسل
def fix_arabic(text):
    if isinstance(text, str):
        return get_display(arabic_reshaper.reshape(text))
    return text

# ... (نفس كود التصميم - apply_neon_style - كما هو) ...

# داخل تبويب التحويل (Tab1):
# استبدل الجزء الخاص بـ tabula.read_pdf بهذا الجزء:
if st.button(f"{lang['btn_convert']}{uploaded_pdf.name}"):
    try:
        with st.spinner(lang["status_loading"]):
            all_data = []
            with pdfplumber.open(uploaded_pdf) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        # تصحيح كل خلية عربية
                        fixed_table = [[fix_arabic(cell) if isinstance(cell, str) else cell for cell in row] for row in table]
                        all_data.extend(fixed_table)
            
            if all_data:
                df = pd.DataFrame(all_data[1:], columns=all_data[0])
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                    writer.sheets['Data'].right_to_left() # إجبار الإكسل على الاتجاه الصحيح
                st.success(lang["success_convert"])
                st.download_button(lang["download_excel"], output.getvalue(), f"Excel_{uploaded_pdf.name}.xlsx")
            else:
                st.warning(lang["warning_no_tables"])
    except Exception as e:
        st.error(f"Error: {str(e)}")
