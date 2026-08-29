import io
import cv2
import numpy as np
import streamlit as st
import svgwrite
from PIL import Image

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Neon Yoo - Automated Vectorizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Neon Yoo - محرك الأتمتة لتصنيع النيون ⚡")

# 2. القائمة الجانبية: خيارات الأتمتة ومقاسات الأكريليك
st.sidebar.header("1. إعدادات أبعاد اللوحة")
SIZES = {"50x60 cm": (500, 600), "40x50 cm": (400, 500), "60x80 cm": (600, 800)}
selected_size_label = st.sidebar.selectbox("اختر المقاس المطلوب:", list(SIZES.keys()))
canvas_width_mm, canvas_height_mm = SIZES[selected_size_label]

st.sidebar.header("2. التحكم الآلي في المتجهات (Autopilot)")
threshold_val = st.sidebar.slider("حساسية التقاط المسارات (Threshold):", 50, 255, 180)
blur_kernel = st.sidebar.slider("تنعيم الحواف (Smoothing):", 1, 9, 3, step=2)

# 3. معالجة الصورة الآلية (Automated Vectorization Pipeline)
uploaded_file = st.file_uploader(
    "ارفع صورة التصميم (PNG / JPG):", 
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    try:
        raw_image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(raw_image)

        # ---------------------------------------------------------
        # مرحلة الرؤية الحاسوبية للتتبع الآلي (Automated Processing)
        # ---------------------------------------------------------
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
        _, thresh = cv2.threshold(blurred, threshold_val, 255, cv2.THRESH_BINARY_INV)

        # استخراج الكنتور/المسارات بدون تدخل يدوي
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # رسم المعاينة الآلية على الصورة الأصلية
        preview_img = img_np.copy()
        cv2.drawContours(preview_img, contours, -1, (0, 255, 85), 2)  # رسم حواف نيون افتراضية باللون الأخضر

        # ---------------------------------------------------------
        # واجهة العرض والمراقبة (Monitor Interface)
        # ---------------------------------------------------------
        st.subheader("لوحة المراقبة والمعاينة الفورية (Monitoring & Preview)")
        col_img1, col_img2 = st.columns(2)

        with col_img1:
            st.write("**1. الصورة الأصلية:**")
            st.image(raw_image, use_container_width=True)

        with col_img2:
            st.write(f"**2. المسارات المكتشفة آلياً (عدد المسارات: {len(contours)}):**")
            st.image(preview_img, use_container_width=True)

        # ---------------------------------------------------------
        # محرك توليد ملف التصنيع SVG (Manufacturing File Generation)
        # ---------------------------------------------------------
        st.markdown("---")
        st.header("التصدير الآلي للماكينات (Automated Output Pipelines)")

        h_img, w_img = gray.shape
        scale_x = canvas_width_mm / w_img
        scale_y = canvas_height_mm / h_img

        dwg = svgwrite.Drawing(
            size=(f"{canvas_width_mm}mm", f"{canvas_height_mm}mm"),
            profile="tiny"
        )

        # إطار الأكريليك الخارجي المقصوص (Cutting Border)
        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(f"{canvas_width_mm}mm", f"{canvas_height_mm}mm"),
            rx="10mm", ry="10mm",
            fill="none",
            stroke="blue",
            stroke_width="1mm"
        ))

        # تحويل مسارات OpenCV إلى عناصر SVG أوتوماتيكياً
        for contour in contours:
            points = []
            for pt in contour:
                px, py = pt[0]
                # تحويل إحداثيات البكسل إلى مليمترات دقيقة للقطع
                mm_x = round(px * scale_x, 2)
                mm_y = round(py * scale_y, 2)
                points.append((f"{mm_x}mm", f"{mm_y}mm"))

            if len(points) > 1:
                dwg.add(dwg.polyline(
                    points=points,
                    fill="none",
                    stroke="red",
                    stroke_width="0.5mm"
                ))

        svg_output = dwg.tostring()

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.info(f"✅ تم تحويل التصميم إلى مسارات CNC بنسبة 1:1 لمقاس {selected_size_label}.")

        with col_dl2:
            st.download_button(
                label="⚙️ تحميل ملف الماكينات المؤتمت (SVG / CNC)",
                data=svg_output,
                file_name="automated_neon_cut.svg",
                mime="image/svg+xml",
                type="primary"
            )

    except Exception as e:
        st.error(f"حدث خطأ في وحدة الأتمتة: {str(e)}")
else:
    st.info("💡 بانتظار رفع صورة البداية لاستخراج المسارات آلياً...")
