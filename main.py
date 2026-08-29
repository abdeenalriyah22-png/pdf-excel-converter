# ---------------------------------------------------------
# 2. دالة استخراج الجداول وعكس ترتيب الأعمدة لتتطابق مع اليمين لليسار
# ---------------------------------------------------------
def extract_and_combine_tables(uploaded_files):
    all_dfs = []
    
    strategies = [
        {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
        {"vertical_strategy": "text", "horizontal_strategy": "text", "snap_tolerance": 5, "join_tolerance": 5},
        {"vertical_strategy": "explicit", "horizontal_strategy": "text"}
    ]
    
    for file in uploaded_files:
        if file.name.endswith('.csv'):
            try:
                df = pd.read_csv(file)
                try:
                    df = df.map(smart_arabic_ai_fix)
                except Exception:
                    df = df.applymap(smart_arabic_ai_fix)
                df = df.dropna(how='all', axis=1).reset_index(drop=True)
                if not df.empty:
                    df.columns = [smart_arabic_ai_fix(str(col)) for col in df.columns]
                    all_dfs.append(df)
            except Exception as e:
                st.error(f"خطأ في معالجة ملف CSV: {e}")
                
        elif file.name.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
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
                        
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        df = pd.DataFrame(table)
                        df = df.dropna(how='all').dropna(how='all', axis=1)
                        if df.empty or df.shape[0] < 2:
                            continue

                        # تصحيح الاتجاه وعكس الأعمدة لتتوافق مع اللغة العربية (من اليمين لليسار)
                        df = df.iloc[:, ::-1]

                        # تثبيت الصف الأول كعناوين صحيحة بعد إعادة الترتيب
                        raw_headers = [str(col).replace('\n', ' ') if col is not None else "" for col in df.iloc[0]]
                        fixed_headers = [smart_arabic_ai_fix(h) for h in raw_headers]
                        
                        df = df[1:].reset_index(drop=True)
                        df.columns = fixed_headers

                        try:
                            df = df.map(smart_arabic_ai_fix)
                        except Exception:
                            df = df.applymap(smart_arabic_ai_fix)

                        df = df.dropna(how='all', axis=1)
                        if not df.empty:
                            df = df.reset_index(drop=True)
                            all_dfs.append(df)

    if not all_dfs:
        return None

    master_df = pd.concat(all_dfs, ignore_index=True)
    return master_df
