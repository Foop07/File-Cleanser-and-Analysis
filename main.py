import os
import streamlit as st
from PIL import Image
from utils.text_extractor import extract_text  # Updated text extractor
from utils.logo_detector import detect_logo    # Logo detection

st.title("File Cleanser & Logo Detection")

# -----------------------------
# File upload section
# -----------------------------
uploaded_file = st.file_uploader("Upload your document or image file")

if uploaded_file:
    # Extract text and initial info
    result = extract_text(uploaded_file)

    # Display errors if any
    if result.get("error"):
        st.error(result["error"])
    else:
        # Display extracted text
        st.subheader("Extracted Text")
        st.text_area("", value=result.get("text", ""), height=300)

        # Logo detection for images (optional: user can provide logo path)
        logo_path = st.text_input(
            "Enter folder path containing logos for detection (optional):"
        )
        if logo_path:
            try:
                image_extensions = ['.jpg', '.jpeg', '.png']
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                if file_ext in image_extensions:
                    image = Image.open(uploaded_file)
                    logos_detected = detect_logo(image, logo_path)
                    st.subheader("Logo Detection")
                    if logos_detected:
                        for logo_name, detected in logos_detected.items():
                            st.write(
                                f"{logo_name}: {'Detected ✅' if detected else 'Not detected ❌'}"
                            )
                    else:
                        st.write("No logos detected in the uploaded image.")
                else:
                    st.info("Logo detection only works with image files.")
            except Exception as e:
                st.error(f"Error during logo detection: {e}")



