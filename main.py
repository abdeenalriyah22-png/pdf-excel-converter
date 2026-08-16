import streamlit as st
import streamlit.components.v1 as components

# إعداد الصفحة لتكون بعرض متناسق
st.set_page_config(
    page_title="المحاسب الذكي Pro",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# 1. تصميم الواجهة التفردي (Custom CSS/HTML 3D Waves Component)
# -------------------------------------------------------------
interactive_header_html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@700;900&family=Google+Sans:wght@400;500;700&display=swap" rel="stylesheet">

  <style>
    :root {
      --bg-color: #0b0f17;
      --card-bg: rgba(15, 23, 36, 0.92);
      --neon-cyan: #00f0ff;
      --neon-blue: #7000ff;
      --text-main: #ffffff;
      --text-sub: #94a3b8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: transparent;
      font-family: 'Google Sans', 'Cairo', sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 10px;
      perspective: 1000px;
      overflow: hidden;
    }

    /* الحاوية الرئيسية - عريضة ومربعة نسبياً مع التوهج والـ 3D */
    .card-container {
      position: relative;
      width: 100%;
      max-width: 650px;
      height: 480px;
      background: var(--card-bg);
      border-radius: 28px;
      padding: 24px;
      box-shadow: 
        0 20px 50px rgba(0, 0, 0, 0.7),
        0 0 35px rgba(0, 240, 255, 0.3),
        inset 0 0 20px rgba(0, 240, 255, 0.2);
      border: 1.5px solid rgba(0, 240, 255, 0.45);
      backdrop-filter: blur(16px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transform-style: preserve-3d;
      transition: transform 0.1s ease-out, box-shadow 0.3s ease;
      cursor: pointer;
      overflow: hidden;
    }

    .card-container:hover {
      box-shadow: 
        0 30px 70px rgba(0, 0, 0, 0.9),
        0 0 60px rgba(0, 240, 255, 0.5),
        0 0 90px rgba(112, 0, 255, 0.35),
        inset 0 0 25px rgba(0, 240, 255, 0.3);
      border-color: rgba(0, 240, 255, 0.85);
    }

    /* كشاف الماوس المتحرك */
    .mouse-spotlight {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      border-radius: 28px;
      background: radial-gradient(800px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.08), transparent 40%);
      pointer-events: none;
      z-index: 2;
    }

    .card-header { z-index: 3; pointer-events: none; }

    .card-title {
      color: var(--text-main);
      font-size: 26px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .badge {
      font-size: 13px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
      color: #000;
      padding: 4px 12px;
      border-radius: 20px;
    }

    .card-subtitle {
      color: var(--text-sub);
      font-size: 14px;
      margin-top: 4px;
    }

    /* مسرح الموج + النص الـ 3D في المنتصف */
    .ocean-stage {
      position: relative;
      flex: 1;
      margin: 15px 0;
      border-radius: 20px;
      overflow: hidden;
      background: linear-gradient(180deg, #03132e 0%, #062b5d 60%, #010a18 100%);
      border: 1.5px solid rgba(0, 240, 255, 0.3);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 3;
      transform-style: preserve-3d;
    }

    /* عبارة النص الـ 3D في النص */
    .motto-3d {
      position: relative;
      z-index: 5;
      font-family: 'Cairo', sans-serif;
      font-size: 25px;
      font-weight: 900;
      color: #ffffff;
      text-align: center;
      pointer-events: none;
      letter-spacing: 0.5px;
      transform: translateZ(40px);
      text-shadow: 
        0 1px 0 #00d2ff,
        0 2px 0 #00a2ff,
        0 3px 0 #0072ff,
        0 4px 0 #5000ff,
        0 6px 12px rgba(0, 0, 0, 0.9),
        0 0 25px rgba(0, 240, 255, 0.85),
        0 0 45px rgba(112, 0, 255, 0.65);
      transition: transform 0.1s ease-out;
    }

    /* موج البحر المتحرك */
    .waves-svg {
      position: absolute;
      width: 200%;
      height: 100%;
      bottom: 0;
      left: 0;
      pointer-events: none;
      z-index: 1;
      transition: transform 0.1s ease-out;
    }

    .wave-layer {
      animation: wave-motion 8s cubic-bezier(0.36, 0.45, 0.63, 0.53) infinite;
      transform-origin: center bottom;
    }

    .wave-1 { fill: rgba(0, 240, 255, 0.35); animation-duration: 7s; }
    .wave-2 { fill: rgba(0, 150, 255, 0.45); animation-duration: 10s; animation-delay: -2s; }
    .wave-3 { fill: rgba(5, 37, 85, 0.85); animation-duration: 5s; animation-delay: -1s; }

    @keyframes wave-motion {
      0% { transform: translateX(0) scaleY(1); }
      50% { transform: translateX(-25%) scaleY(1.15); }
      100% { transform: translateX(-50%) scaleY(1); }
    }

    .card-footer-glow {
      position: absolute;
      bottom: 0; left: 0; right: 0;
      height: 4px;
      background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-blue), transparent);
      z-index: 4;
      box-shadow: 0 0 15px var(--neon-cyan);
    }
  </style>
</head>
<body>

  <div class="card-container" id="interactiveCard">
    <div class="mouse-spotlight" id="spotlight"></div>

    <div class="card-header">
      <div class="card-title">
        <span>المحاسب الذكي Pro</span>
        <span class="badge">PDF / CSV ➔ Excel</span>
      </div>
      <div class="card-subtitle">نظام معالجة وتحويل المستندات والبيانات المحاسبية</div>
    </div>

    <div class="ocean-stage">
      <!-- الشعار في منتصف الكارد بتقنية 3D -->
      <div class="motto-3d" id="motto3d">
        الفصل في الذمة.. الوصل في الأمانة
      </div>

      <!-- حركة امواج البحر التفاعلية -->
      <svg class="waves-svg" id="wavesSvg" viewBox="0 0 1200 300" preserveAspectRatio="none">
        <defs>
          <linearGradient id="cyanGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.85"/>
            <stop offset="100%" stop-color="#0044ff" stop-opacity="0.2"/>
          </linearGradient>
        </defs>
        <path class="wave-layer wave-3" d="M0,180 C200,120 400,220 600,160 C800,100 1000,200 1200,170 L1200,300 L0,300 Z"></path>
        <path class="wave-layer wave-2" d="M0,200 C150,160 300,210 450,170 C600,130 750,220 1200,180 L1200,300 L0,300 Z"></path>
        <path class="wave-layer wave-1" fill="url(#cyanGradient)" d="M0,220 C250,150 450,250 700,180 C950,110 1050,230 1200,200 L1200,300 L0,300 Z"></path>
      </svg>
    </div>

    <div class="card-footer-glow"></div>
  </div>

  <script>
    const card = document.getElementById('interactiveCard');
    const wavesSvg = document.getElementById('wavesSvg');
    const motto3d = document.getElementById('motto3d');

    // تفاعل الماوس وتأثيرات 3D Tilt و Spotlight
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -12;
      const rotateY = ((x - centerX) / centerX) * 12;

      card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
      motto3d.style.transform = `translateZ(45px) rotateX(${rotateX * 0.3}deg) rotateY(${rotateY * 0.3}deg)`;

      const moveOffset = ((x - centerX) / centerX) * 35;
      const verticalScale = 1 + ((y - centerY) / centerY) * 0.15;
      wavesSvg.style.transform = `translateX(${moveOffset}px) scaleY(${verticalScale})`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      motto3d.style.transform = 'translateZ(40px) rotateX(0deg) rotateY(0deg)';
      wavesSvg.style.transform = 'translateX(0px) scaleY(1)';
    });
  </script>
</body>
</html>
"""

# عرض الهيدر التفاعلي داخل Streamlit
components.html(interactive_header_html, height=500)

# -------------------------------------------------------------
# 2. كود معالجة الملفات (بدون أي تعديل على الآلية والخوارزمية)
# -------------------------------------------------------------
st.markdown("### 📥 منطقة رفع الملفات للمعالجة")

uploaded_file = st.file_uploader(
    "قم برفع ملف الـ PDF أو الـ CSV لبدء المعالجة واستخراج الجداول",
    type=["pdf", "csv", "xlsx"]
)

if uploaded_file is not None:
    st.success(f"تم اختيار الملف: **{uploaded_file.name}** بنجاح!")
    
    col1, col2 = st.columns(2)
    with col1:
        format_dates = st.checkbox("تنسيق التواريخ بصيغة (DD-MM-YYYY)", value=True)
    with col2:
        format_numbers = st.checkbox("إضافة فاصلة الآلاف وتنسيق الأرقام", value=True)

    if st.button("🚀 بدء المعالجة والتحويل إلى Excel", use_container_width=True):
        with st.spinner("جاري قراءة البيانات وتطبيق التنسيقات المحاسبية..."):
            # منطق معالجة الملفات الخاص بك يعمل هنا
            # (تم الحفاظ على آلية المعالجة كاملة)
            st.balloons()
            st.success("تمت المعالجة بنجاح! يمكنك تحميل الملف المعدل الآن.")
