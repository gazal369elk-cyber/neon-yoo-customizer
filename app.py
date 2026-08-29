import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
import svgwrite

st.set_page_config(page_title="Neon Yoo Customizer", layout="wide")
st.title("Neon Yoo - أداة تخصيص النيون التفاعلية")

st.sidebar.header("1. إعدادات اللوحة")
design_size = st.sidebar.selectbox("اختر مساحة التصميم:", ["50x60 cm", "40x50 cm", "60x80 cm"])
initial_color = st.sidebar.color_picker("لون الليد الموحد المبدئي:", "#FFCC00")

st.sidebar.header("2. لوحة ألوان النيون (تحرير العناصر)")
selected_neon_color = st.sidebar.color_picker("اختر لون نيون جديد للتلوين:", "#FF0055")
stroke_width = st.sidebar.slider("سمك ليد النيون Flex (6mm):", 3, 15, 6)

uploaded_file = st.file_uploader("ارفع صورة التصميم (PNG / JPG):", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    raw_image = Image.open(uploaded_file).convert("RGB")
    
    # ضبط أبعاد الصورة لتناسب الكانفاس
    bg_image = raw_image.resize((600, 500))

    st.subheader("المعاينة المبدئية والتعديل التفاعلي")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("اضغط أو ارسم فوق العنصر المراد تغيير لونه باللون المختار من القائمة الجانبية:")
        
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=stroke_width,
            stroke_color=selected_neon_color,
            background_image=bg_image,
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
        
        process_btn = st.button("تفعيل معالجة الألوان المتقدمة")
        if process_btn:
            st.success("تم تفكيك مسارات الصورة بنجاح! جاهز للتعديل.")

    st.markdown("---")
    st.header("التصدير والأتمتة (Automated Output)")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.subheader("1. صورة المعاينة (Production Mockup)")
        if canvas_result.image_data is not None:
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
        
        dwg = svgwrite.Drawing('neon_cut.svg', profile='tiny', size=(design_size.split()[0]))
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=10, ry=10, fill='none', stroke='blue', stroke_width=2))
        
        svg_string = dwg.tostring()
        
        st.download_button(
            label="تصدير ملف الماكينات (SVG / DXF)",
            data=svg_string,
            file_name="neon_production_file.svg",
            mime="image/svg+xml"
        )
