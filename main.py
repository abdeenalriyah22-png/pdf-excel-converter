# --- داخل التبويب الأول في الجزء الخاص بمعالجة الجداول ---

            try:
                with st.spinner(f'جاري معالجة وتطهير جداول: {uploaded_pdf.name} ...'):
                    # استخدام lattice=True لقراءة الجداول المخططة بدقة وتقليل الأعمدة الوهمية
                    dfs = tabula.read_pdf(uploaded_pdf, pages='all', multiple_tables=True, lattice=True)
                    
                    if dfs:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                            sheet_name = 'Data_Sheet'
                            workbook = writer.book
                            worksheet = workbook.add_worksheet(sheet_name)
                            writer.sheets[sheet_name] = worksheet
                            
                            # تنسيقات المحاسب المحترف
                            border_fmt = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
                            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD700', 'color': 'black', 'border': 1, 'align': 'center'})
                            
                            current_row = 0
                            for df in dfs:
                                # 1. تنظيف القيم غير الرقمية
                                df = df.replace([float('inf'), float('-inf')], 0).fillna('')
                                
                                # 2. الحل السحري: حذف الأعمدة الفارغة تماماً التي تظهر زيادة (مثل العمود 14 إلى 35)
                                # نحذف الأعمدة التي تحتوي على نصوص فارغة فقط أو Unnamed
                                df = df.loc[:, ~df.columns.str.contains('^Unnamed')] 
                                df = df.replace('', pd.NA).dropna(axis=1, how='all').fillna('')
                                
                                if df.empty or len(df.columns) == 0: continue
                                
                                # كتابة رأس الجدول
                                for col_num, value in enumerate(df.columns.values):
                                    worksheet.write(current_row, col_num, value, header_fmt)
                                    worksheet.set_column(col_num, col_num, 20)
                                
                                # كتابة البيانات
                                for row_idx, row_data in enumerate(df.values):
                                    for col_num, col_data in enumerate(row_data):
                                        worksheet.write(current_row + row_idx + 1, col_num, col_data, border_fmt)
                                
                                current_row += len(df) + 3
                            
                        st.success(f"تم تنظيف وتقليص الأعمدة في {uploaded_pdf.name}")
                        st.download_button(label=f"📥 تحميل الملف المنظف: {uploaded_pdf.name}", data=output.getvalue(), file_name=f"Clean_{uploaded_pdf.name.split('.')[0]}.xlsx")
