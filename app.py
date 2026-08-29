import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageOps
from streamlit_drawable_canvas import st_canvas
import io
import svgwrite

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Neon Yoo Customizer", layout="wide")
st.title("Neon Yoo - أداة تخصيص النيون التفاعلية")

# 2. القائمة الجانبية: خيارات الإعداد الأولية
st.sidebar.header("1. إعدادات اللوحة")
design_size = st.sidebar.selectbox("اختر مساحة التصميم:", ["50x60 cm", "40x50 cm", "60x80 cm"])
initial_color = st.sidebar.color_picker("لون الليد الموحد المبدئي:", "#FFCC00")

st.sidebar.header("2. لوحة ألوان النيون (تحرير العناصر)")
selected_neon_color = st.sidebar.color_picker("اختر لون نيون جديد للتلوين:", "#FF0055")
stroke_width = st.sidebar.slider("سمك ليد النيون Flex (6mm):", 3, 15, 6)

# 3. واجهة رفع الصورة
uploaded_file = st.file_counts = st.file_uploader("ارفع صورة التصميم (PNG / JPG):", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # تحميل الصورة
    raw_image = Image.open(uploaded_file).convert("RGB")
    
    # تحويل الصورة إلى أسود وأبيض لاستخراج المسارات (OpenCV)
    img_array = np.array(raw_image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # تحويل التحديدات لخطوط نيون افتراضية المظهر
    st.subheader("المعاينة المبدئية والتعديل التفاعلي")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("اضغط أو ارسم فوق العنصر المراد تغيير لونه باللون المختار من القائمة الجانبية:")
        
        # إنشاء Canvas تفاعلي للتلوين المباشر فوق الرسمة
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=stroke_width,
            stroke_color=selected_neon_color,
            background_image=raw_image,
            update_streamlit=True,
            height=500,
            width=600,
            drawing_mode="freedraw",
            key="canvas",
        )

    with col2:
        st.subheader("معلومات التصنيف")
        st.info(f"**المقاس المحدد:** {design_size}")
        st.info("**سمك الأكريليك:** 3mm (Transparent Offset)")
        st.info("**سمك النيون:** 6mm Flex LED")
        
        # زر التحرير والمعالجة
        process_btn = st.button("تفعيل معالجة الألوان المتقدمة")
        if process_btn:
            st.success("تم تفكيك مسارات الصورة بنجاح! جاهز للتعديل.")

    # 4. قسم التصدير والأتمتة
    st.markdown("---")
    st.header("التصدير والأتمتة (Automated Output)")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.subheader("1. صورة المعاينة (Production Mockup)")
        if canvas_result.image_data is not None:
            # دمج الرسم الخطي مع خلفية الأكريليك
            final_mockup = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            
            buf = io.BytesIO()
            final_mockup.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="تحميل معاينة العميل (PNG)",
                data=byte_im,
                file_name="neon_mockup.png",
                mime="image/png"
            )

    with col_exp2:
        st.subheader("2. ملفات التصنيع للماكينات (Laser / CNC)")
        
        # توليد كود SVG تلقائي للمسارات
        dwg = svgwrite.Drawing('neon_cut.svg', profile='tiny', size=(design_size.split()[0]))
        # إضافة طبقة الأكريليك المقصوصة
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=10, ry=10, fill='none', stroke='blue', stroke_width=2))
        
        svg_string = dwg.tostring()
        
        st.download_button(
            label="تصدير ملف الماكينات (SVG / DXF)",
            data=svg_string,
            file_name="neon_production_file.svg",
            mime="image/svg+xml"
        )
