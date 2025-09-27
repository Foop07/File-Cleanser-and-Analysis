import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

st.title("Logo Detection App")

# Upload multiple logo images
uploaded_logos = st.file_uploader(
    "Upload logo images (PNG/JPG)", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg']
)

# Upload the image to check
uploaded_image = st.file_uploader(
    "Upload test image", 
    type=['png', 'jpg', 'jpeg']
)

# Ensure output folder exists
OUTPUT_DIR = "output_files"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def detect_logos(test_image_file, logo_files):
    # Open the test image with PIL and convert to RGB
    test_image = Image.open(test_image_file).convert('RGB')
    img = np.array(test_image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    output_img = img.copy()

    for logo_file in logo_files:
        # Open each logo image with PIL
        logo_img = Image.open(logo_file).convert('RGB')
        logo_gray = cv2.cvtColor(np.array(logo_img), cv2.COLOR_RGB2GRAY)

        # Try multiple scales
        scales = [0.5, 0.75, 1.0, 1.25, 1.5]
        detected = False
        for scale in scales:
            w = int(logo_gray.shape[1] * scale)
            h = int(logo_gray.shape[0] * scale)

            # Skip if logo is larger than test image
            if w > img_gray.shape[1] or h > img_gray.shape[0]:
                continue

            resized_logo = cv2.resize(logo_gray, (w, h))
            res = cv2.matchTemplate(img_gray, resized_logo, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.6)
            if loc[0].size > 0:
                detected = True
                for pt in zip(*loc[::-1]):
                    cv2.rectangle(output_img, pt, (pt[0]+w, pt[1]+h), (0,255,0), 2)

        if detected:
            st.success(f"Detected logo: {logo_file.name}")
        else:
            st.warning(f"Not detected: {logo_file.name}")

    # Save output image
    output_path = os.path.join(OUTPUT_DIR, "detected_image.png")
    cv2.imwrite(output_path, cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR))
    st.info(f"Output saved to {output_path}")

    return Image.fromarray(output_img)

# Only run detection if files are uploaded
if uploaded_image is not None and uploaded_logos is not None and len(uploaded_logos) > 0:
    result_img = detect_logos(uploaded_image, uploaded_logos)
    st.image(result_img, caption="Detected logos", use_column_width=True)
else:
    st.info("Please upload a test image and at least one logo image.")


